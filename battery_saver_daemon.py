#!/usr/bin/env python3
"""
Battery Saver Daemon - Background Low Power Mode Manager for macOS
Copyright (c) 2025 Daniel
Licensed under the MIT License

This version runs completely in the background with no UI.
"""

import subprocess
import json
import os
import time
import signal
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class BatterySaverDaemon:
    """Background daemon to automatically enable Low Power Mode at specified battery levels."""

    def __init__(self):
        self.config_path = os.path.join(
            os.path.expanduser("~"),
            ".battery_saver_config.json"
        )

        self.log_path = os.path.join(
            os.path.expanduser("~"),
            ".battery_saver_daemon.log"
        )

        # Load configuration
        self.config = self.load_config()
        self.threshold = self.config.get("threshold", 20)
        self.enabled = self.config.get("enabled", True)
        self.check_interval = self.config.get("check_interval", 30)  # seconds
        self.notification_shown = False
        self.running = True

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        self.log("Battery Saver Daemon starting...")
        self.log(f"Threshold: {self.threshold}%, Enabled: {self.enabled}, Check interval: {self.check_interval}s")

    def log(self, message: str):
        """Write to log file with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        try:
            with open(self.log_path, 'a') as f:
                f.write(log_message)
        except Exception as e:
            print(f"Error writing to log: {e}")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.log(f"Received signal {signum}, shutting down...")
        self.running = False
        sys.exit(0)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "threshold": 20,
            "enabled": True,
            "notifications": True,
            "check_interval": 30
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Reload settings on each check to allow external changes
                    return {**default_config, **config}
            except Exception as e:
                self.log(f"Error loading config: {e}")
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
                    "check_interval": self.check_interval
                }, f, indent=2)
        except Exception as e:
            self.log(f"Error saving config: {e}")

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
            self.log(f"Error getting battery level: {e}")
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
            self.log(f"Error checking power source: {e}")
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
                in_battery_section = False
                for line in result.stdout.split('\n'):
                    if 'Battery Power:' in line:
                        in_battery_section = True
                    elif 'AC Power:' in line:
                        in_battery_section = False
                    elif in_battery_section and 'lowpowermode' in line.lower():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return int(parts[-1])
            return None
        except Exception as e:
            self.log(f"Error getting power mode: {e}")
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

            # If sudo fails, try without (will fail but we log it)
            self.log(f"Warning: Cannot set power mode without passwordless sudo. Run setup_passwordless_pmset.sh")
            return False

        except Exception as e:
            self.log(f"Error setting power mode: {e}")
            return False

    def send_notification(self, title: str, message: str):
        """Send macOS notification."""
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            self.log(f"Error sending notification: {e}")

    def check_battery(self):
        """Check battery level and enable Low Power Mode if needed."""
        # Reload config to get any external changes
        self.config = self.load_config()
        self.threshold = self.config.get("threshold", 20)
        self.enabled = self.config.get("enabled", True)

        if not self.enabled:
            self.log("Monitoring disabled, skipping check")
            return

        battery_level = self.get_battery_level()
        if battery_level is None:
            self.log("Could not get battery level")
            return

        on_battery = self.is_on_battery()
        power_mode = self.get_power_mode()

        self.log(f"Battery: {battery_level}%, On battery: {on_battery}, Power mode: {power_mode}, Threshold: {self.threshold}%")

        # Only act if on battery power
        if not on_battery:
            self.notification_shown = False
            return

        # Check if battery is at or below threshold
        if battery_level <= self.threshold:
            current_mode = self.get_power_mode()

            # Only enable if not already in low power mode
            if current_mode != 1:
                self.log(f"Battery at {battery_level}%, enabling Low Power Mode...")
                success = self.set_power_mode(1)

                if success:
                    self.log("Low Power Mode enabled successfully")
                    if not self.notification_shown and self.config.get("notifications", True):
                        self.send_notification(
                            "Battery Saver",
                            f"Battery at {battery_level}% - Low Power Mode enabled"
                        )
                        self.notification_shown = True
                else:
                    self.log("Failed to enable Low Power Mode")
            else:
                self.log("Low Power Mode already active")
        else:
            # Reset notification flag when battery is above threshold
            self.notification_shown = False

    def run(self):
        """Main daemon loop."""
        self.log("Daemon running, checking battery every {self.check_interval} seconds...")

        while self.running:
            try:
                self.check_battery()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.log("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(self.check_interval)

        self.log("Daemon stopped")


if __name__ == "__main__":
    daemon = BatterySaverDaemon()
    daemon.run()
