#!/usr/bin/env python3
"""
Battery Saver - Automatic Low Power Mode Manager for macOS
Copyright (c) 2025 Daniel
Licensed under the MIT License
"""

import rumps
import subprocess
import json
import os
from typing import Dict, Any, Optional
import time

try:
    import AppKit  # type: ignore
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    if info is not None:
        info["LSUIElement"] = "1"
except Exception:
    # Non-fatal: if AppKit unavailable (e.g., tests), fall back to default behavior.
    pass


class BatterySaver(rumps.App):
    """Menu bar app to automatically enable Low Power Mode at specified battery levels."""

    def __init__(self):
        # Use empty string initially - will be set by update_icon()
        super(BatterySaver, self).__init__(
            "",
            quit_button=None
        )

        self.config_path = os.path.join(
            os.path.expanduser("~"),
            ".battery_saver_config.json"
        )

        # Load configuration
        self.config = self.load_config()
        self.threshold = self.config.get("threshold", 20)
        self.enabled = self.config.get("enabled", True)
        self.notification_shown = False
        self.last_battery_level = 100

        # Build threshold slider submenu
        self.threshold_menu = rumps.MenuItem(f"Threshold: {self.threshold}%")
        self.build_threshold_submenu()

        # Build menu with green checkmark next to active mode
        self.enabled_item = rumps.MenuItem("Enabled", callback=self.enable_monitoring)
        self.disabled_item = rumps.MenuItem("Disabled", callback=self.disable_monitoring)

        # Set initial checkmark
        if self.enabled:
            self.enabled_item.state = 1  # Checked
            self.disabled_item.state = 0  # Unchecked
        else:
            self.enabled_item.state = 0  # Unchecked
            self.disabled_item.state = 1  # Checked

        self.menu = [
            self.threshold_menu,
            rumps.separator,
            self.enabled_item,
            self.disabled_item,
            rumps.separator,
            rumps.MenuItem("Current Battery", callback=self.show_battery_info),
            rumps.MenuItem("Current Power Mode", callback=self.show_power_mode),
            rumps.separator,
            rumps.MenuItem("About", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Start monitoring
        self.timer = rumps.Timer(self.check_battery, 30)  # Check every 30 seconds
        self.timer.start()

        # Initial check
        self.update_icon()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "threshold": 20,
            "enabled": True,
            "notifications": True
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        return default_config

    def save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    "threshold": self.threshold,
                    "enabled": self.enabled,
                    "notifications": self.config.get("notifications", True)
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_battery_level(self) -> Optional[int]:
        """Get current battery percentage."""
        try:
            result = subprocess.run(
                ['pmset', '-g', 'batt'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse output: e.g., "Now drawing from 'Battery Power' -InternalBattery-0 (id=123456) 85%; discharging; 3:45 remaining"
                for line in result.stdout.split('\n'):
                    if '%' in line:
                        # Extract percentage
                        percentage_str = line.split('\t')[-1].split(';')[0].strip()
                        if '%' in percentage_str:
                            return int(percentage_str.replace('%', ''))
            return None
        except Exception as e:
            print(f"Error getting battery level: {e}")
            return None

    def is_on_battery(self) -> bool:
        """Check if Mac is running on battery power."""
        try:
            result = subprocess.run(
                ['pmset', '-g', 'batt'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return 'Battery Power' in result.stdout
            return False
        except Exception as e:
            print(f"Error checking power source: {e}")
            return False

    def get_power_mode(self) -> Optional[int]:
        """Get current power mode (0=off, 1=on for low power mode)."""
        try:
            result = subprocess.run(
                ['pmset', '-g', 'custom'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse lowpowermode setting (on Battery Power section)
                in_battery_section = False
                for line in result.stdout.split('\n'):
                    if 'Battery Power:' in line:
                        in_battery_section = True
                    elif 'AC Power:' in line:
                        in_battery_section = False
                    elif in_battery_section and 'lowpowermode' in line.lower():
                        # Extract mode number (0 or 1)
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return int(parts[-1])
            return None
        except Exception as e:
            print(f"Error getting power mode: {e}")
            return None

    def set_power_mode(self, mode: int) -> bool:
        """
        Set low power mode.

        Args:
            mode: 0 (disable low power mode), 1 (enable low power mode)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try sudo first (works if passwordless sudo is configured)
            result = subprocess.run(
                ['sudo', '-n', 'pmset', '-b', 'lowpowermode', str(mode)],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True

            # If sudo fails, fall back to AppleScript (will ask for password)
            script = f'''
            do shell script "pmset -b lowpowermode {mode}" with administrator privileges
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )

            return result.returncode == 0
        except Exception as e:
            print(f"Error setting power mode: {e}")
            return False

    def check_battery(self, _) -> None:
        """Timer callback to check battery level and enable Low Power Mode if needed."""
        if not self.enabled:
            return

        battery_level = self.get_battery_level()
        if battery_level is None:
            return

        self.last_battery_level = battery_level
        self.update_icon()

        # Only act if on battery power
        if not self.is_on_battery():
            self.notification_shown = False
            return

        # Check if battery is at or below threshold
        if battery_level <= self.threshold:
            current_mode = self.get_power_mode()

            # Only enable if not already in low power mode
            if current_mode != 1:
                success = self.set_power_mode(1)

                if success and not self.notification_shown:
                    rumps.notification(
                        title="Battery Saver",
                        subtitle=f"Battery at {battery_level}%",
                        message=f"Low Power Mode enabled automatically"
                    )
                    self.notification_shown = True
        else:
            # Reset notification flag when battery is above threshold
            self.notification_shown = False

    def update_icon(self) -> None:
        """Update menu bar icon based on battery level and Low Power Mode status."""
        battery_level = self.last_battery_level
        on_battery = self.is_on_battery()
        power_mode = self.get_power_mode()

        # Clear visual indicators
        # Priority: Show Low Power Mode status first, then battery status
        if power_mode == 1:  # Low Power Mode is ON
            icon = "💤"  # Sleep/Low Power indicator - clear and unambiguous
        elif not on_battery:
            # On AC power - charging
            icon = "🔌"  # Plug indicates AC power
        else:
            # On battery - show status
            if battery_level <= 20:
                icon = "🪫"  # Low battery (red battery)
            elif battery_level <= self.threshold:
                icon = "⚡"  # At threshold
            else:
                icon = "🔋"  # Normal battery

        self.title = icon

    def build_threshold_submenu(self):
        """Build threshold slider submenu with percentage options."""
        # Clear existing submenu if it exists
        try:
            self.threshold_menu.clear()
        except:
            pass

        # Add threshold options from 5% to 95% in increments of 5
        for percent in range(5, 100, 5):
            # Add checkmark to current threshold
            if percent == self.threshold:
                label = f"✓ {percent}%"
            else:
                label = f"  {percent}%"

            item = rumps.MenuItem(label, callback=self.change_threshold)
            self.threshold_menu.add(item)

    def change_threshold(self, sender):
        """Handle threshold change from submenu."""
        # Extract percentage from label (remove checkmark and spaces)
        label = sender.title.replace("✓", "").replace(" ", "").replace("%", "")
        try:
            new_threshold = int(label)
            self.threshold = new_threshold
            self.save_config()

            # Update main menu title
            self.threshold_menu.title = f"Threshold: {self.threshold}%"

            # Rebuild submenu to update checkmark
            self.build_threshold_submenu()

            rumps.notification(
                title="Battery Saver",
                subtitle="Threshold Updated",
                message=f"Low Power Mode will activate at {self.threshold}%"
            )
        except ValueError:
            pass

    def update_enabled_menu(self):
        """Update the enabled/disabled menu items with checkmarks."""
        # Update the menu items
        if self.enabled:
            self.menu["✅ Enabled"].title = "✅ Enabled"
            self.menu["Disabled"].title = "Disabled"
        else:
            self.menu["Enabled"].title = "Enabled"
            self.menu["❌ Disabled"].title = "❌ Disabled"

    def enable_monitoring(self, sender) -> None:
        """Enable Low Power Mode."""
        success = self.set_power_mode(1)

        if success:
            self.enabled = True
            self.save_config()

            # Update checkmarks
            self.enabled_item.state = 1  # Checked
            self.disabled_item.state = 0  # Unchecked

            # Update icon
            self.update_icon()

            rumps.notification(
                title="Battery Saver",
                subtitle="Low Power Mode Enabled",
                message="Power mode set to Low Power"
            )
        else:
            rumps.alert(
                title="Error",
                message="Failed to enable Low Power Mode. Run ./setup_passwordless_pmset.sh"
            )

    def disable_monitoring(self, sender) -> None:
        """Disable Low Power Mode."""
        success = self.set_power_mode(0)

        if success:
            self.enabled = False
            self.save_config()

            # Update checkmarks
            self.enabled_item.state = 0  # Unchecked
            self.disabled_item.state = 1  # Checked

            # Update icon
            self.update_icon()

            rumps.notification(
                title="Battery Saver",
                subtitle="Low Power Mode Disabled",
                message="Power mode set to Automatic"
            )
        else:
            rumps.alert(
                title="Error",
                message="Failed to disable Low Power Mode. Run ./setup_passwordless_pmset.sh"
            )

    @rumps.clicked("Current Battery")
    def show_battery_info(self, _) -> None:
        """Show current battery information."""
        battery_level = self.get_battery_level()
        on_battery = self.is_on_battery()

        if battery_level is not None:
            power_source = "Battery" if on_battery else "AC Power"
            rumps.alert(
                title="Battery Information",
                message=f"Battery Level: {battery_level}%\nPower Source: {power_source}\nThreshold: {self.threshold}%"
            )
        else:
            rumps.alert(
                title="Error",
                message="Unable to retrieve battery information"
            )

    @rumps.clicked("Current Power Mode")
    def show_power_mode(self, _) -> None:
        """Show current power mode."""
        mode = self.get_power_mode()

        mode_names = {
            0: "Automatic",
            1: "Low Power Mode",
            2: "High Power Mode"
        }

        if mode in mode_names:
            rumps.alert(
                title="Current Power Mode",
                message=f"Power Mode: {mode_names[mode]}"
            )
        else:
            rumps.alert(
                title="Error",
                message="Unable to retrieve power mode"
            )

    @rumps.clicked("About")
    def show_about(self, _) -> None:
        """Show about information."""
        rumps.alert(
            title="Battery Saver",
            message=f"Automatic Low Power Mode Manager\n\n"
                    f"Version: 1.0.0\n"
                    f"Current Threshold: {self.threshold}%\n\n"
                    f"Icon Legend:\n"
                    f"💤 - Low Power Mode ON\n"
                    f"🔌 - Charging (AC Power)\n"
                    f"🔋 - On Battery (normal)\n"
                    f"🪫 - Low Battery\n"
                    f"⚡ - At Threshold\n\n"
                    f"Automatically enables Low Power Mode when your battery reaches the specified threshold.\n\n"
                    f"© 2025 Daniel\n"
                    f"Licensed under MIT License"
        )

    @rumps.clicked("Quit")
    def quit_app(self, _) -> None:
        """Quit the application."""
        rumps.quit_application()


if __name__ == "__main__":
    BatterySaver().run()
