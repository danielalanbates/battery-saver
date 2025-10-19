#!/usr/bin/env python3
"""
Battery Saver (Minimal Icon Version) - Automatic Low Power Mode Manager for macOS
Copyright (c) 2025 Daniel
Licensed under the MIT License

This version uses a minimal text-based icon to sit nicely next to the system battery icon.
"""

import rumps
import subprocess
import json
import os
from typing import Dict, Any, Optional
import time


class BatterySaver(rumps.App):
    """Menu bar app to automatically enable Low Power Mode at specified battery levels."""

    def __init__(self):
        # Start with minimal icon
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
        self.show_percentage = self.config.get("show_percentage", False)
        self.notification_shown = False
        self.last_battery_level = 100

        # Build menu
        self.menu = [
            rumps.MenuItem(f"Threshold: {self.threshold}%", callback=self.set_threshold),
            rumps.separator,
            rumps.MenuItem(
                "Enabled" if self.enabled else "Disabled",
                callback=self.toggle_enabled
            ),
            rumps.MenuItem(
                "Show Percentage" if not self.show_percentage else "Hide Percentage",
                callback=self.toggle_percentage
            ),
            rumps.separator,
            rumps.MenuItem("Current Battery", callback=self.show_battery_info),
            rumps.MenuItem("Current Power Mode", callback=self.show_power_mode),
            rumps.separator,
            rumps.MenuItem("Enable Low Power Mode Now", callback=self.enable_low_power_now),
            rumps.MenuItem("Disable Low Power Mode Now", callback=self.disable_low_power_now),
            rumps.separator,
            rumps.MenuItem("About", callback=self.show_about),
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
            "notifications": True,
            "show_percentage": False
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
                    "notifications": self.config.get("notifications", True),
                    "show_percentage": self.show_percentage
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
                for line in result.stdout.split('\n'):
                    if '%' in line:
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
        """Get current power mode (0=auto, 1=low, 2=high)."""
        try:
            result = subprocess.run(
                ['pmset', '-g', 'custom'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'lowpowermode' in line.lower():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return int(parts[-1])
            return None
        except Exception as e:
            print(f"Error getting power mode: {e}")
            return None

    def set_power_mode(self, mode: int) -> bool:
        """
        Set power mode.

        Args:
            mode: 0 (automatic), 1 (low power), 2 (high power)

        Returns:
            True if successful, False otherwise
        """
        try:
            script = f'''
            do shell script "pmset -b powermode {mode}" with administrator privileges
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
        """Update menu bar icon - minimal style to complement system battery icon."""
        battery_level = self.last_battery_level
        power_mode = self.get_power_mode()

        # Option 1: Show percentage next to system battery
        if self.show_percentage:
            self.title = f"{battery_level}%"
        # Option 2: Show Low Power Mode indicator
        elif power_mode == 1:
            self.title = "🍃"  # Leaf = Low Power Mode active
        # Option 3: Minimal lightning bolt
        else:
            self.title = "⚡"

    @rumps.clicked("Threshold")
    def set_threshold(self, _) -> None:
        """Allow user to set battery threshold."""
        response = rumps.Window(
            message=f"Enter battery threshold (current: {self.threshold}%)",
            title="Set Battery Threshold",
            default_text=str(self.threshold),
            ok="Set",
            cancel="Cancel",
            dimensions=(200, 20)
        ).run()

        if response.clicked:
            try:
                new_threshold = int(response.text)
                if 5 <= new_threshold <= 95:
                    self.threshold = new_threshold
                    self.save_config()
                    self.menu["Threshold"].title = f"Threshold: {self.threshold}%"
                    rumps.notification(
                        title="Battery Saver",
                        subtitle="Threshold Updated",
                        message=f"Low Power Mode will activate at {self.threshold}%"
                    )
                else:
                    rumps.alert(
                        title="Invalid Threshold",
                        message="Threshold must be between 5% and 95%"
                    )
            except ValueError:
                rumps.alert(
                    title="Invalid Input",
                    message="Please enter a valid number"
                )

    @rumps.clicked("Enabled")
    def toggle_enabled(self, sender) -> None:
        """Toggle monitoring on/off."""
        self.enabled = not self.enabled
        sender.title = "Enabled" if self.enabled else "Disabled"
        self.save_config()

        status = "enabled" if self.enabled else "disabled"
        rumps.notification(
            title="Battery Saver",
            subtitle=f"Monitoring {status}",
            message=f"Automatic Low Power Mode is now {status}"
        )

    @rumps.clicked("Show Percentage")
    def toggle_percentage(self, sender) -> None:
        """Toggle battery percentage display."""
        self.show_percentage = not self.show_percentage
        sender.title = "Hide Percentage" if self.show_percentage else "Show Percentage"
        self.save_config()
        self.update_icon()

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

    @rumps.clicked("Enable Low Power Mode Now")
    def enable_low_power_now(self, _) -> None:
        """Manually enable Low Power Mode."""
        success = self.set_power_mode(1)

        if success:
            self.update_icon()  # Update to show leaf icon
            rumps.notification(
                title="Battery Saver",
                subtitle="Low Power Mode Enabled",
                message="Power mode set to Low Power"
            )
        else:
            rumps.alert(
                title="Error",
                message="Failed to enable Low Power Mode. You may need to grant permissions."
            )

    @rumps.clicked("Disable Low Power Mode Now")
    def disable_low_power_now(self, _) -> None:
        """Manually disable Low Power Mode (set to automatic)."""
        success = self.set_power_mode(0)

        if success:
            self.update_icon()  # Update to remove leaf icon
            rumps.notification(
                title="Battery Saver",
                subtitle="Low Power Mode Disabled",
                message="Power mode set to Automatic"
            )
        else:
            rumps.alert(
                title="Error",
                message="Failed to disable Low Power Mode. You may need to grant permissions."
            )

    @rumps.clicked("About")
    def show_about(self, _) -> None:
        """Show about information."""
        rumps.alert(
            title="Battery Saver",
            message=f"Automatic Low Power Mode Manager\n\n"
                    f"Version: 1.0.0 (Minimal)\n"
                    f"Current Threshold: {self.threshold}%\n\n"
                    f"Automatically enables Low Power Mode when your battery reaches the specified threshold.\n\n"
                    f"Icon Legend:\n"
                    f"⚡ - Monitoring active\n"
                    f"🍃 - Low Power Mode ON\n\n"
                    f"© 2025 Daniel\n"
                    f"Licensed under MIT License"
        )

    @rumps.clicked("Quit")
    def quit_app(self, _) -> None:
        """Quit the application."""
        rumps.quit_application()


if __name__ == "__main__":
    BatterySaver().run()
