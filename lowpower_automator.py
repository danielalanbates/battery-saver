#!/usr/bin/env python3
"""
LowPower Automator - Automatic Low Power Mode Manager for macOS
Copyright (c) 2025 Daniel Alan Bates
Licensed under EULA

Automatically enables Low Power Mode at custom battery thresholds.
"""

# Hide Dock icon on macOS
import os
import re
import time
import json
import subprocess
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import rumps


class LowPowerAutomator(rumps.App):
    """Menu bar app to automatically enable Low Power Mode at specified battery levels."""

    def __init__(self):
        super(LowPowerAutomator, self).__init__("🔋")

        self.config_path = os.path.join(os.path.expanduser("~"), ".lowpower_automator_config.json")
        self.config = self.load_config()
        self.threshold = self.config.get("threshold", 20)
        self.threshold_mode = self.config.get("threshold_mode", "percentage")  # "percentage" or "time" - Pro version defaults to percentage
        self.time_threshold_minutes = self.config.get("time_threshold_minutes", 90)  # Pro version default 1:30 hours
        self.notification_shown = False
        self.last_battery_level = 100
        self.setup_complete = self.config.get("setup_complete", True)  # Temporarily set to True for testing

        # Pro features data
        self.battery_data_path = os.path.join(os.path.expanduser("~"), ".lowpower_automator_battery_data.json")
        self.battery_history: List[Dict[str, Any]] = []
        self.charging_cycles = 0
        self.last_cycle_check_time = datetime.now()
        self.last_battery_count = None
        self.smart_auto_enabled = self.config.get("smart_auto_enabled", False)

        # Load battery data
        self.load_battery_data()

        # Build threshold slider submenu with appropriate initial label
        if self.threshold_mode == "percentage":
            if self.smart_auto_enabled:
                self.threshold_menu = rumps.MenuItem(f"Threshold: Smart ✨")
            else:
                self.threshold_menu = rumps.MenuItem(f"Threshold: {self.threshold}%")
        else:
            self.threshold_menu = rumps.MenuItem(f"Threshold: {self.time_threshold_minutes} minutes")
        # We'll build the submenu after menu initialization

        # Build threshold mode toggle menu item
        self.threshold_mode_menu = rumps.MenuItem(
            self.get_threshold_mode_label(),
            callback=self.toggle_threshold_mode
        )

        # Build smart auto toggle
        self.smart_auto_menu = rumps.MenuItem(
            self.get_smart_auto_label(),
            callback=self.toggle_smart_auto
        )

        # Build menu
        self.menu = [
            self.threshold_menu,
            self.threshold_mode_menu,
            self.smart_auto_menu,
            rumps.separator,
            rumps.MenuItem("Current Battery"),
            rumps.MenuItem("Current Power Mode"),
            rumps.MenuItem("Battery Analytics"),
            rumps.separator,
            rumps.MenuItem("About")
        ]

        # Set up button click handlers
        self.menu["Current Battery"].set_callback(self.show_battery_info)
        self.menu["Current Power Mode"].set_callback(self.show_power_mode)
        self.menu["Battery Analytics"].set_callback(self.show_battery_analytics)
        self.menu["About"].set_callback(self.show_about)

        # Start monitoring
        self.timer = rumps.Timer(self.check_battery, 30)
        self.timer.start()

        # Initial update
        self.update_icon()

        # Check if first launch setup is needed
        if not self.setup_complete:
            # Show setup notification after a delay to ensure icon appears first
            # Don't check battery until after setup completes
            self.launch_timer = rumps.Timer(self.show_first_launch_setup, 1)
            self.launch_timer.start()
        else:
            # Setup is complete, safe to check battery now
            self.check_battery_on_launch()
            # Show regular launch notification
            self.launch_timer = rumps.Timer(self.show_launch_notification, 1)
            self.launch_timer.start()

        # Initialize threshold submenu after menu is set up
        self.init_submenus()

    def init_submenus(self) -> None:
        """Initialize submenus after app is fully set up."""
        self.build_threshold_submenu()

    def get_smart_auto_label(self) -> str:
        """Get label for smart auto toggle."""
        if self.smart_auto_enabled:
            return "Smart Auto: ON ✨"
        else:
            return "Smart Auto: OFF"

    def toggle_smart_auto(self, sender) -> None:
        """Toggle smart auto threshold adjustment."""
        self.smart_auto_enabled = not self.smart_auto_enabled
        self.config["smart_auto_enabled"] = self.smart_auto_enabled
        self.save_config()

        sender.title = self.get_smart_auto_label()

        # Update threshold menu title to reflect Smart Auto state
        self.update_threshold_menu_title()
        self.build_threshold_submenu()

        if self.smart_auto_enabled:
            rumps.alert(
                title="🤖 Smart Auto Activated",
                message="LowPower Automator Pro will now automatically learn and optimize\n"
                        "your battery threshold based on your usage patterns.\n\n"
                        "• Analyzes your battery usage for optimal thresholds\n"
                        "• Gradually adjusts settings for maximum battery life\n"
                        "• Works only in Battery % mode\n"
                        "• Uses historical data to make smart recommendations\n\n"
                        "The threshold menu now shows 'Smart ✨' and is automatically controlled."
            )
        else:
            rumps.alert(
                title="🔧 Manual Control Restored",
                message="Smart Auto disabled. You now have full manual control over\n"
                        "your battery threshold settings.\n\n"
                        "• Set your preferred battery % threshold manually\n"
                        "• Threshold remains exactly as you configure it\n"
                        "• Works in both Battery % and Time Remaining modes\n"
                        "• No automatic adjustments or learning\n\n"
                        "The threshold menu will show your manual settings again."
            )

    def load_battery_data(self) -> None:
        """Load historical battery data from JSON file."""
        if os.path.exists(self.battery_data_path):
            try:
                with open(self.battery_data_path, 'r') as f:
                    data = json.load(f)
                    self.battery_history = data.get('history', [])
                    self.charging_cycles = data.get('cycles', 0)

                    # Convert timestamps back to datetime objects
                    for entry in self.battery_history:
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
            except:
                self.battery_history = []
                self.charging_cycles = 0

    def save_battery_data(self) -> None:
        """Save historical battery data to JSON file."""
        try:
            data = {
                'history': [],
                'cycles': self.charging_cycles
            }

            # Convert datetime objects to strings for JSON serialization
            for entry in self.battery_history:
                data['history'].append({
                    **entry,
                    'timestamp': entry['timestamp'].isoformat()
                })

            with open(self.battery_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def record_battery_data(self) -> None:
        """Record current battery data point and check for charging cycles."""
        battery_level = self.get_battery_level()
        power_mode = self.get_power_mode()
        on_battery = self.is_on_battery()
        time_remaining_mins = self.get_time_remaining_minutes()

        if battery_level is None:
            return

        # Create data point
        data_point = {
            'timestamp': datetime.now(),
            'battery_level': battery_level,
            'power_mode': power_mode or 0,
            'on_battery': on_battery,
            'time_remaining_minutes': time_remaining_mins
        }

        # Check for charging cycles (complete charge from ~0% to ~100%)
        self.detect_charging_cycle(data_point)

        # Add to history and keep only last 1000 entries
        self.battery_history.append(data_point)
        if len(self.battery_history) > 1000:
            self.battery_history = self.battery_history[-1000:]

        # Save data every 10 minutes or if significant change
        now = datetime.now()
        last_save = getattr(self, '_last_data_save', datetime.min)
        significant_change = (
            self.last_battery_count is None or
            abs(battery_level - self.last_battery_count) >= 5
        )

        if (now - last_save).total_seconds() > 600 or significant_change:
            self.save_battery_data()
            self._last_data_save = now

        self.last_battery_count = battery_level

    def detect_charging_cycle(self, data_point: Dict[str, Any]) -> None:
        """Detect and count complete charging cycles."""
        if not data_point['on_battery']:  # Currently charging
            battery_level = data_point['battery_level']
            now = data_point['timestamp']

            # Need at least some history to detect cycles
            if len(self.battery_history) < 3:
                return

            # Check if we just completed a cycle (reached ~100% from ~0%)
            recent_history = [
                entry for entry in self.battery_history[-20:]  # Last 20 entries
                if (now - entry['timestamp']).total_seconds() < 3600  # Within last hour
            ]

            if len(recent_history) >= 3:  # Need minimum entries to analyze
                try:
                    # Separate battery and charging entries
                    recent_battery_entries = [entry for entry in recent_history if entry['on_battery']]
                    if recent_battery_entries:  # Only proceed if we have battery entries to analyze
                        min_level_recent = min(entry['battery_level'] for entry in recent_battery_entries)
                        max_level_recent = max(entry['battery_level'] for entry in recent_history)

                        # If we went from low (<20%) to high (>95%) recently, count it as a cycle
                        if min_level_recent <= 20 and max_level_recent >= 95 and (now - self.last_cycle_check_time).total_seconds() > 86400:  # Once per day
                            self.charging_cycles += 1
                            self.last_cycle_check_time = now

                            # Notify user of new cycle (removed spam notification)
                except (ValueError, IndexError):
                    # Skip cycle detection if data is malformed
                    pass

    def get_battery_longevity_score(self) -> float:
        """Calculate battery longevity score based on usage patterns."""
        if len(self.battery_history) < 10:
            return 100.0  # Default good score

        # Analyze usage patterns
        power_mode_usage = sum(1 for entry in self.battery_history if entry['power_mode'] == 1) / len(self.battery_history)

        # Deep discharge frequency (dangerous for battery health)
        deep_discharges = sum(1 for entry in self.battery_history if entry['battery_level'] <= 10)

        # Calculate score (0-100, higher is better)
        score = 100.0
        score -= power_mode_usage * 20  # LPM helps somewhat but not too much
        score -= deep_discharges * 5   # Penalty for deep discharges
        score -= self.charging_cycles * 0.1  # Small penalty per cycle

        # Factor in battery age (rough estimate)
        if self.battery_history:
            first_entry = min(self.battery_history, key=lambda x: x['timestamp'])
            age_days = (datetime.now() - first_entry['timestamp']).days
            age_penalty = age_days * 0.001  # Small daily penalty
            score -= age_penalty

        return max(0.0, min(100.0, score))

    def get_smart_threshold_recommendation(self) -> Optional[int]:
        """Provide smart threshold recommendation based on historical data."""
        if len(self.battery_history) < 20:
            return None

        # Analyze when LPM was typically engaged historically
        lpm_entries = [entry for entry in self.battery_history if entry['power_mode'] == 1]

        if not lpm_entries:
            return None

        # Find the most common battery levels when LPM was enabled
        lpm_levels = [entry['battery_level'] for entry in lpm_entries]
        if not lpm_levels:
            return None

        # Use mode (most common) or median
        try:
            mode_level = statistics.mode(lpm_levels)
            median_level = statistics.median(lpm_levels)
            recommended = int((mode_level + median_level) / 2)
            return max(15, min(50, recommended))  # Reasonable bounds
        except:
            return None

    def get_battery_health_trends(self) -> Dict[str, Any]:
        """Get battery health trends from historical data."""
        if len(self.battery_history) < 10:
            return {'trend': 'insufficient_data', 'days': 0}

        # Get data from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_data = [entry for entry in self.battery_history if entry['timestamp'] > thirty_days_ago]

        if len(recent_data) < 5:
            return {'trend': 'insufficient_data', 'days': 0}

        # Calculate discharge rate (how fast battery drains)
        discharge_entries = [entry for entry in recent_data if entry['on_battery'] and entry['time_remaining_minutes']]
        if discharge_entries:
            avg_discharge_time = statistics.mean(entry['time_remaining_minutes'] for entry in discharge_entries)
        else:
            avg_discharge_time = 180  # Default 3 hours

        # Classify battery health trend
        days_data = (datetime.now() - recent_data[0]['timestamp']).days
        power_mode_ratio = sum(1 for entry in recent_data if entry['power_mode'] == 1) / len(recent_data)

        if power_mode_ratio > 0.3:
            trend = 'frequent_lpm'
        elif avg_discharge_time > 300:  # >5 hours
            trend = 'excellent'
        elif avg_discharge_time > 240:  # >4 hours
            trend = 'good'
        elif avg_discharge_time > 180:  # >3 hours
            trend = 'fair'
        else:
            trend = 'poor'

        return {
            'trend': trend,
            'days': days_data,
            'avg_discharge_time': max(30, avg_discharge_time),
            'power_mode_ratio': power_mode_ratio,
            'cycles': self.charging_cycles
        }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "threshold": 20,
            "threshold_mode": "percentage",
            "time_threshold_minutes": 90,
            "notifications": True,
            "setup_complete": False,
            "smart_auto_enabled": False
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except:
                pass
        return default_config

    def save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    "threshold": self.threshold,
                    "threshold_mode": self.threshold_mode,
                    "time_threshold_minutes": self.time_threshold_minutes,
                    "notifications": self.config.get("notifications", True),
                    "setup_complete": self.setup_complete,
                    "smart_auto_enabled": self.smart_auto_enabled
                }, f, indent=2)
        except:
            pass

    def get_battery_level(self) -> Optional[int]:
        """Get current battery percentage."""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '%' in line:
                        percentage_str = line.split('\t')[-1].split(';')[0].strip()
                        if '%' in percentage_str:
                            return int(percentage_str.replace('%', ''))
        except:
            pass
        return None

    def get_time_remaining(self) -> Optional[str]:
        """Get estimated time remaining on battery."""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '%' in line:
                        # Look for time remaining pattern like "3:45 remaining" or "(no estimate)"
                        if 'remaining' in line.lower():
                            # Extract time remaining
                            match = re.search(r'(\d+:\d+)\s+remaining', line)
                            if match:
                                return match.group(1)
                        elif 'no estimate' in line.lower():
                            return "Calculating..."
                        elif 'charging' in line.lower():
                            # Check for "until full" time
                            match = re.search(r'(\d+:\d+)\s+until full', line)
                            if match:
                                return f"{match.group(1)} until full"
                            return "Charging"
        except:
            pass
        return None

    def get_time_remaining_minutes(self) -> Optional[int]:
        """Get time remaining in minutes."""
        time_str = self.get_time_remaining()
        if not time_str or time_str in ["Calculating...", "Charging"] or "until full" in time_str:
            return None

        try:
            # Parse "H:MM" format
            parts = time_str.split(":")
            if len(parts) == 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours * 60 + minutes
        except:
            pass
        return None

    def minutes_to_time_str(self, minutes: int) -> str:
        """Convert minutes to H:MM format."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}:{mins:02d}"

    def update_threshold_menu_title(self) -> None:
        """Update threshold menu title based on current mode and smart auto state."""
        if self.threshold_mode == "percentage":
            if self.smart_auto_enabled:
                self.threshold_menu.title = "Threshold: Smart ✨"
            else:
                self.threshold_menu.title = f"Threshold: {self.threshold}%"
        else:
            self.threshold_menu.title = f"Threshold: {self.time_threshold_minutes} minutes"

    def build_threshold_label(self) -> rumps.MenuItem:
        """Build threshold menu item with appropriate label."""
        label = f"Threshold: {self.threshold}%"
        return rumps.MenuItem(label)

    def get_threshold_mode_label(self) -> str:
        """Get label for threshold mode toggle."""
        if self.threshold_mode == "percentage":
            return "Mode: Battery % 🔄"
        else:
            return "Mode: Time Remaining ⏱ 🔄"

    def toggle_threshold_mode(self, sender) -> None:
        """Toggle between percentage and time-based thresholds."""
        if self.threshold_mode == "percentage":
            self.threshold_mode = "time"
        else:
            self.threshold_mode = "percentage"

        self.save_config()

        # Update menu labels
        sender.title = self.get_threshold_mode_label()

        # Update threshold menu title based on current mode and smart auto
        self.update_threshold_menu_title()

        self.build_threshold_submenu()

        # If switching to percentage mode, check immediately if LPM should activate
        if self.threshold_mode == "percentage":
            if self.should_trigger_threshold():
                battery_level = self.get_battery_level()
                if battery_level and self.is_on_battery() and self.get_power_mode() != 1:
                    if self.set_power_mode(1):
                        rumps.notification(
                            title="LowPower Automator Pro",
                            subtitle=f"Switched to Battery % mode - Battery at {battery_level}%",
                            message="Low Power Mode enabled automatically"
                        )
        # If switching to time mode, no immediate check needed since time-based triggering works differently

        # Removed notification spam - user doesn't want notifications for every setting change

    def is_on_battery(self) -> bool:
        """Check if Mac is running on battery power."""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            return 'Battery Power' in result.stdout if result.returncode == 0 else False
        except:
            return False

    def get_power_mode(self) -> Optional[int]:
        """Get current power mode (0=off, 1=on for low power mode)."""
        try:
            result = subprocess.run(['pmset', '-g', 'custom'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                in_battery_section = False
                in_ac_section = False
                battery_mode = None
                ac_mode = None

                for line in result.stdout.split('\n'):
                    if 'Battery Power:' in line:
                        in_battery_section = True
                        in_ac_section = False
                    elif 'AC Power:' in line:
                        in_battery_section = False
                        in_ac_section = True
                    elif in_battery_section and 'lowpowermode' in line.lower():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            battery_mode = int(parts[-1])
                    elif in_ac_section and 'lowpowermode' in line.lower():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ac_mode = int(parts[-1])

                # Return the mode for the current power source
                if self.is_on_battery():
                    # When on battery, use battery mode if set, otherwise default to 0
                    return battery_mode if battery_mode is not None else 0
                else:
                    # When on AC power, use AC mode if set, otherwise default to 0
                    return ac_mode if ac_mode is not None else 0
        except:
            pass
        return None

    def get_battery_health(self) -> Optional[Dict[str, str]]:
        """Get battery health information."""
        try:
            result = subprocess.run(['system_profiler', 'SPPowerDataType'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                health_info = {}
                in_health_section = False

                for line in result.stdout.split('\n'):
                    if 'Health Information:' in line:
                        in_health_section = True
                        continue

                    if in_health_section:
                        if 'Cycle Count:' in line:
                            health_info['cycle_count'] = line.split(':')[1].strip()
                        elif 'Condition:' in line:
                            health_info['condition'] = line.split(':')[1].strip()
                        elif 'Maximum Capacity:' in line:
                            health_info['max_capacity'] = line.split(':')[1].strip()
                        elif line.strip() and ':' not in line:
                            break

                return health_info if health_info else None
        except:
            pass
        return None

    def set_power_mode(self, mode: int) -> bool:
        """Set low power mode. Returns True if successful."""
        try:
            # Try passwordless sudo first (requires setup)
            result = subprocess.run(['sudo', '-n', 'pmset', '-b', 'lowpowermode', str(mode)],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True

            # Fallback to AppleScript (will prompt for password)
            # Use custom prompt so it doesn't show "osascript"
            script = f'do shell script "pmset -b lowpowermode {mode}" with administrator privileges with prompt "LowPower Automator Pro needs your password to change Low Power Mode."'
            result = subprocess.run(['osascript', '-e', script],
                                    capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except:
            return False

    def should_trigger_threshold(self) -> bool:
        """Check if current battery state is at or below threshold."""
        if self.threshold_mode == "percentage":
            battery_level = self.get_battery_level()
            return battery_level is not None and battery_level <= self.threshold
        else:
            time_remaining_mins = self.get_time_remaining_minutes()
            return time_remaining_mins is not None and time_remaining_mins <= self.time_threshold_minutes

    def check_battery_on_launch(self) -> None:
        """Check battery on launch and enable LPM if needed."""
        battery_level = self.get_battery_level()
        if battery_level is None or not self.is_on_battery():
            return

        self.last_battery_level = battery_level

        if self.should_trigger_threshold():
            current_mode = self.get_power_mode()
            if current_mode != 1:
                if self.set_power_mode(1):
                    rumps.notification(
                        title="LowPower Automator Pro",
                        subtitle=f"Battery at {battery_level}%",
                        message=f"Low Power Mode enabled (threshold: {self.threshold}%)"
                    )

    def check_battery(self, _) -> None:
        """Timer callback to check battery level and enable Low Power Mode if needed."""
        battery_level = self.get_battery_level()
        if battery_level is None:
            return

        # Record battery data point (for pro features tracking)
        self.record_battery_data()

        self.last_battery_level = battery_level
        self.update_icon()

        # Smart auto threshold adjustment (only in percentage mode)
        if self.smart_auto_enabled and self.threshold_mode == "percentage":
            smart_threshold = self.get_smart_threshold_recommendation()
            if smart_threshold and smart_threshold != self.threshold:
                # Automatically adjust threshold if different from smart recommendation
                old_threshold = self.threshold
                self.threshold = smart_threshold
                self.save_config()
                self.threshold_menu.title = f"Threshold: {self.threshold}%"
                self.build_threshold_submenu()

                # Removed notification spam - user doesn't want constant notifications

        if not self.is_on_battery():
            self.notification_shown = False
            return

        if self.should_trigger_threshold():
            current_mode = self.get_power_mode()
            if current_mode != 1:
                if self.set_power_mode(1) and not self.notification_shown:
                    rumps.notification(
                        title="LowPower Automator Pro",
                        subtitle=f"Battery at {battery_level}%",
                        message="Low Power Mode enabled automatically"
                    )
                    self.notification_shown = True
        else:
            self.notification_shown = False

    def show_first_launch_setup(self, timer) -> None:
        """Show first launch setup dialog and run passwordless sudo setup."""
        # Stop the timer so it only runs once
        timer.stop()

        # Show setup explanation
        response = rumps.alert(
            title="Welcome to LowPower Automator Pro!",
            message="LowPower Automator Pro needs one-time administrator access\n"
                    "to automatically control Low Power Mode.\n\n"
                    "You'll be prompted for your password to set this up.\n"
                    "After this, the app will work automatically without\n"
                    "asking for your password again.\n\n"
                    "Click 'Continue' to proceed with setup.",
            ok="Continue",
            cancel="Quit"
        )

        if response == 0:  # User clicked Cancel/Quit
            rumps.quit_application()
            return

        # Run setup - embed the logic directly to avoid file permission issues
        try:
            # Get current username
            username = os.environ.get('USER') or subprocess.run(
                ['stat', '-f', '%Su', '/dev/console'],
                capture_output=True,
                text=True
            ).stdout.strip()

            # Create the sudoers rule - properly escaped for AppleScript
            sudoers_rule = f"{username} ALL=(ALL) NOPASSWD: /usr/bin/pmset -b lowpowermode *"
            sudoers_file = "/private/etc/sudoers.d/lowpowerautomator"

            # Build the command with proper escaping
            # Use single quotes in shell and escape them for AppleScript
            setup_command = f"mkdir -p /private/etc/sudoers.d && echo '{sudoers_rule}' > {sudoers_file} && chmod 0440 {sudoers_file} && visudo -c -f {sudoers_file}"

            # Run with AppleScript to get admin privileges
            # Escape quotes properly for AppleScript
            applescript = f'''do shell script "{setup_command}" with administrator privileges with prompt "LowPower Automator Pro needs your password to set up automatic Low Power Mode control."'''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Mark setup as complete
                self.config["setup_complete"] = True
                self.setup_complete = True
                self.save_config()

                # Now that setup is complete, check battery for the first time
                self.check_battery_on_launch()

                # Show success message
                rumps.alert(
                    title="Setup Complete!",
                    message="LowPower Automator Pro is now configured.\n\n"
                            f"Current threshold: {self.threshold}%\n"
                            f"Low Power Mode will activate automatically when\n"
                            f"your battery reaches {self.threshold}%.\n\n"
                            f"The app is running in your menu bar.\n\n"
                            f"🎯 New Pro Features Available:\n"
                            f"• Battery analytics and cycle tracking\n"
                            f"• Smart threshold recommendations\n"
                            f"• Battery longevity optimization\n"
                            f"• Historical data monitoring",
                    ok="Get Started!"
                )
            else:
                # Setup failed
                rumps.alert(
                    title="Setup Failed",
                    message="Could not complete setup. The app will still work\n"
                            "but will prompt for your password each time it\n"
                            "needs to enable Low Power Mode.\n\n"
                            f"Error: {result.stderr}",
                    ok="OK"
                )

        except Exception as e:
            # Setup error
            rumps.alert(
                title="Setup Error",
                message=f"An error occurred during setup:\n{str(e)}\n\n"
                        "The app will still work but may prompt for\n"
                        "your password when enabling Low Power Mode.",
                ok="OK"
            )

    def show_launch_notification(self, timer) -> None:
        """Show launch notification popup."""
        # Stop the timer so it only runs once
        timer.stop()

        rumps.alert(
            title="LowPower Automator Pro is Running",
            message=f"The app is now active in your menu bar.\n\n"
                    f"Current threshold: {self.threshold}%\n"
                    f"Low Power Mode will activate automatically when\n"
                    f"your battery reaches {self.threshold}%.\n\n"
                    f"Click the battery icon in the menu bar anytime\n"
                    f"to view battery info or change settings.\n\n"
                    f"🎯 Check out Battery Analytics in the menu!",
            ok="Got it!"
        )

    def update_icon(self) -> None:
        """Update menu bar icon based on battery level and power mode."""
        battery_level = self.last_battery_level
        on_battery = self.is_on_battery()
        power_mode = self.get_power_mode()

        if power_mode == 1:
            icon = "💤"
        elif not on_battery:
            icon = "🔌"
        else:
            if battery_level <= 20:
                icon = "🪫"
            elif battery_level <= self.threshold:
                icon = "⚡"
            else:
                icon = "🔋"

        self.title = icon

    def build_threshold_submenu(self):
        """Build threshold slider submenu with percentage or time options based on current mode."""
        try:
            self.threshold_menu.clear()
        except:
            pass

        if self.threshold_mode == "percentage":
            # Show percentage options
            for percent in range(10, 100, 10):
                label = f"✓ {percent}%" if percent == self.threshold else f"  {percent}%"
                item = rumps.MenuItem(label, callback=self.change_threshold)
                self.threshold_menu.add(item)
        else:
            # Show time options in minutes
            time_options = [60, 90, 120, 150, 180, 210, 240, 300]  # 60, 90, 120, etc. minutes
            for minutes in time_options:
                label = f"✓ {minutes} minutes" if minutes == self.time_threshold_minutes else f"  {minutes} minutes"
                item = rumps.MenuItem(label, callback=self.change_time_threshold)
                self.threshold_menu.add(item)


    def change_threshold(self, sender):
        """Handle threshold change from submenu."""
        label = sender.title.replace("✓", "").replace(" ", "").replace("%", "")
        try:
            new_threshold = int(label)
            self.threshold = new_threshold
            self.save_config()

            self.threshold_menu.title = f"Threshold: {self.threshold}%"
            self.build_threshold_submenu()

            # If battery is at/below new threshold, trigger LPM immediately
            battery_level = self.get_battery_level()
            if battery_level and battery_level <= self.threshold:
                if self.is_on_battery() and self.get_power_mode() != 1:
                    if self.set_power_mode(1):
                        rumps.notification(
                            title="LowPower Automator Pro",
                            subtitle=f"Battery at {battery_level}%",
                            message=f"Low Power Mode enabled (threshold: {self.threshold}%)"
                        )
                        return

            rumps.notification(
                title="LowPower Automator Pro",
                subtitle="Threshold Updated",
                message=f"Low Power Mode will activate at {self.threshold}%"
            )
        except ValueError:
            pass

    def force_update_threshold_menu(self):
        """Force update of threshold menu after smart auto changes."""
        self.threshold_menu.title = f"Threshold: {self.threshold}%"
        self.build_threshold_submenu()

    def change_time_threshold(self, sender):
        """Handle time threshold change from submenu."""
        # Parse the menu item title to extract minutes
        label = sender.title.replace("✓", "").strip()  # Remove checkmark and strip whitespace
        try:
            # Extract minutes from "150 minutes" format
            if " minutes" in label:
                minutes_str = label.replace(" minutes", "")
                new_time_threshold = int(minutes_str)
            else:
                # Fallback: try to extract just the number if format is unexpected
                minutes_str = ''.join(filter(str.isdigit, label))
                new_time_threshold = int(minutes_str) if minutes_str else 90

            original_threshold = self.time_threshold_minutes
            self.time_threshold_minutes = new_time_threshold
            self.save_config()

            # Update menu title
            time_str = f"{new_time_threshold} minutes"
            self.threshold_menu.title = f"Threshold: {time_str}"
            self.build_threshold_submenu()

            # Success! Remove debug alerts after testing
            print(f"SUCCESS: Changed time threshold from {original_threshold} to {new_time_threshold} minutes")

        except ValueError as e:
            rumps.alert(title="Error", message=f"Failed to parse '{label}': {e}")


    def show_battery_info(self, _) -> None:
        """Show current battery information."""
        battery_level = self.get_battery_level()
        on_battery = self.is_on_battery()
        health_info = self.get_battery_health()

        if battery_level is not None:
            power_source = "Battery" if on_battery else "AC Power"
            message = f"Battery Level: {battery_level}%\n"
            message += f"Power Source: {power_source}\n"
            message += f"Threshold: {self.threshold}%\n"

            if health_info:
                message += "\nBattery Health:\n"
                if 'max_capacity' in health_info:
                    message += f"Maximum Capacity: {health_info['max_capacity']}\n"
                if 'condition' in health_info:
                    message += f"Condition: {health_info['condition']}\n"
                if 'cycle_count' in health_info:
                    message += f"Cycle Count: {health_info['cycle_count']}\n"

            # Show smart threshold recommendation
            smart_threshold = self.get_smart_threshold_recommendation()
            if smart_threshold and smart_threshold != self.threshold:
                message += f"\n🎯 Smart Recommendation: {smart_threshold}% threshold"

            rumps.alert(title="Battery Information", message=message)
        else:
            rumps.alert(title="Error", message="Unable to retrieve battery information")

    def show_power_mode(self, _) -> None:
        """Show current power mode."""
        mode = self.get_power_mode()
        mode_names = {0: "Automatic", 1: "Low Power Mode", 2: "High Power Mode"}

        if mode in mode_names:
            rumps.alert(title=mode_names[mode], message="")
        else:
            rumps.alert(title="Error", message="Unable to retrieve power mode")

    def show_battery_analytics(self, _) -> None:
        """Show comprehensive battery analytics."""
        # Calculate analytics
        longevity_score = self.get_battery_longevity_score()
        trend_data = self.get_battery_health_trends()
        smart_threshold = self.get_smart_threshold_recommendation()

        message = "🎯 Battery Analytics Dashboard\n\n"
        message += f"Battery Cycles Tracked: {self.charging_cycles}\n\n"

        # Longevity score
        if longevity_score >= 90:
            score_text = "Excellent"
        elif longevity_score >= 75:
            score_text = "Good"
        elif longevity_score >= 60:
            score_text = "Fair"
        elif longevity_score >= 40:
            score_text = "Poor"
        else:
            score_text = "Critical"

        message += f"Battery Longevity Score: {longevity_score:.1f}/100 ({score_text})\n\n"

        # Health trends
        if trend_data['trend'] != 'insufficient_data':
            trend_description = {
                'excellent': 'Battery performing excellently (5+ hours discharge time)',
                'good': 'Battery performing well (4+ hours discharge time)',
                'fair': 'Battery performance acceptable (3+ hours discharge time)',
                'poor': 'Battery needs attention (less than 3 hours discharge time)',
                'frequent_lpm': 'Frequent Low Power Mode usage detected'
            }.get(trend_data['trend'], trend_data['trend'].title())

            avg_hours = int(trend_data['avg_discharge_time'] // 60)
            avg_mins = int(trend_data['avg_discharge_time'] % 60)
            message += f"Battery Health Trend: {trend_data['trend'].title()}\n"
            message += f"Avg. Discharge Time: {avg_hours}:{avg_mins:02d}\n"
            message += f"Low Power Mode Usage: {trend_data['power_mode_ratio']*100:.1f}%\n"
            message += f"Analysis Period: {trend_data['days']} days\n\n"
        else:
            message += "Battery Trend: Collecting data (need more usage history)\n\n"

        # Smart recommendations
        if smart_threshold and smart_threshold != self.threshold:
            message += f"🎯 Smart Threshold Suggestion: {smart_threshold}%\n"
            message += f"(Based on your usage patterns)\n"
            message += f"Current threshold: {self.threshold}%\n\n"
        else:
            message += "🎯 Smart Threshold: Using optimal threshold\n\n"

        # Battery optimization tips - always show some helpful tips
        message += "💡 Battery Optimization Tips:\n"
        message += "• Maintain battery above 20% when possible\n"
        message += "• Use Low Power Mode for extended battery life\n"
        message += "• Calibrate battery monthly by fully charging and discharging\n"

        if self.charging_cycles > 500:
            message += "• Consider battery replacement soon (high cycle count)\n"
        if longevity_score < 70:
            message += "• Avoid frequent deep discharges (<20%)\n"
            message += "• Use Low Power Mode more often\n"
        if trend_data['trend'] != 'insufficient_data' and trend_data['power_mode_ratio'] < 0.1:
            message += "• Consider lowering threshold for better battery life\n"
        if trend_data['trend'] == 'insufficient_data':
            message += "• Tips will improve with more usage data\n"

        rumps.alert(title="Battery Analytics Dashboard", message=message)

    def show_about(self, _) -> None:
        """Show about information."""
        threshold_display = f"{self.threshold}%"
        mode_display = "Battery %" if self.threshold_mode == "percentage" else "Time Remaining"

        rumps.alert(
            title="LowPower Automator Pro",
            message=f"Automatic Low Power Mode Manager for macOS\n\n"
                    f"Version: 2.0.0 Pro\n"
                    f"Current Threshold: {threshold_display}\n"
                    f"Mode: {mode_display}\n"
                    f"Smart Auto: {'Enabled' if self.smart_auto_enabled else 'Disabled'}\n\n"
                    f"Icon Legend:\n"
                    f"💤 - Low Power Mode ON\n"
                    f"🔌 - Charging (AC Power)\n"
                    f"🔋 - On Battery (normal)\n"
                    f"🪫 - Low Battery\n"
                    f"⚡ - At Threshold\n\n"
                    f"✨ Pro Features:\n"
                    f"• Automatic Low Power Mode activation\n"
                    f"• Battery cycle tracking & analytics\n"
                    f"• Smart threshold recommendations\n"
                    f"• Battery longevity optimization\n"
                    f"• Historical data monitoring\n\n"
                    f"© 2025 Daniel Alan Bates\n"
                    f"Licensed under EULA"
        )


if __name__ == "__main__":
    LowPowerAutomator().run()
