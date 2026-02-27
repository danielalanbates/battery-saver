#!/usr/bin/env python3
import os
import AppKit

# Hide from Dock immediately before any other imports
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSUIElement"] = "1"

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
    def __init__(self):
        super(LowPowerAutomator, self).__init__("🔋")
        self.config_path = os.path.join(os.path.expanduser("~"), ".lowpower_automator_config.json")
        self.config = self.load_config()
        self.threshold = self.config.get("threshold", 20)
        self.threshold_mode = self.config.get("threshold_mode", "percentage")
        self.time_threshold_minutes = self.config.get("time_threshold_minutes", 90)
        self.notification_shown = False
        self.last_battery_level = 100
        self.setup_complete = self.config.get("setup_complete", True)

        self.battery_data_path = os.path.join(os.path.expanduser("~"), ".lowpower_automator_battery_data.json")
        self.battery_history = []
        self.charging_cycles = 0
        self.last_cycle_check_time = datetime.now()
        self.last_battery_count = None
        self.smart_auto_enabled = self.config.get("smart_auto_enabled", False)

        self.load_battery_data()

        if self.threshold_mode == "percentage":
            if self.smart_auto_enabled:
                self.threshold_menu = rumps.MenuItem(f"Threshold: Smart ✨")
            else:
                self.threshold_menu = rumps.MenuItem(f"Threshold: {self.threshold}%")
        else:
            self.threshold_menu = rumps.MenuItem(f"Threshold: {self.time_threshold_minutes} minutes")

        self.threshold_mode_menu = rumps.MenuItem(self.get_threshold_mode_label(), callback=self.toggle_threshold_mode)
        self.smart_auto_menu = rumps.MenuItem(self.get_smart_auto_label(), callback=self.toggle_smart_auto)

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

        self.menu["Current Battery"].set_callback(self.show_battery_info)
        self.menu["Current Power Mode"].set_callback(self.show_power_mode)
        self.menu["Battery Analytics"].set_callback(self.show_battery_analytics)
        self.menu["About"].set_callback(self.show_about)

        self.timer = rumps.Timer(self.check_battery, 30)
        self.timer.start()
        self.update_icon()

        if not self.setup_complete:
            self.launch_timer = rumps.Timer(self.show_first_launch_setup, 1)
            self.launch_timer.start()
        else:
            self.check_battery_on_launch()
            self.launch_timer = rumps.Timer(self.show_launch_notification, 1)
            self.launch_timer.start()

        # The threshold_menu needs to be populated, but it is already a MenuItem.
        # Calling build_threshold_submenu() here might fail because the app hasn't
        # been fully realized by the underlying Cocoa bridge yet.
        # We'll use a short timer to defer the submenu population.
        rumps.Timer(self.init_submenus_timer, 0.5).start()

    def init_submenus_timer(self, timer):
        timer.stop()
        self.build_threshold_submenu()

    def get_smart_auto_label(self) -> str:
        return "Smart Auto: ON ✨" if self.smart_auto_enabled else "Smart Auto: OFF"

    def toggle_smart_auto(self, sender) -> None:
        self.smart_auto_enabled = not self.smart_auto_enabled
        self.config["smart_auto_enabled"] = self.smart_auto_enabled
        self.save_config()
        sender.title = self.get_smart_auto_label()
        self.update_threshold_menu_title()
        self.build_threshold_submenu()

    def load_battery_data(self) -> None:
        if os.path.exists(self.battery_data_path):
            try:
                with open(self.battery_data_path, 'r') as f:
                    data = json.load(f)
                    self.battery_history = data.get('history', [])
                    self.charging_cycles = data.get('cycles', 0)
                    for entry in self.battery_history:
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
            except:
                self.battery_history = []
                self.charging_cycles = 0

    def save_battery_data(self) -> None:
        try:
            data = {'history': [], 'cycles': self.charging_cycles}
            for entry in self.battery_history:
                data['history'].append({**entry, 'timestamp': entry['timestamp'].isoformat()})
            with open(self.battery_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def record_battery_data(self) -> None:
        battery_level = self.get_battery_level()
        if battery_level is None: return
        self.battery_history.append({
            'timestamp': datetime.now(),
            'battery_level': battery_level,
            'on_battery': self.is_on_battery(),
            'power_mode': self.get_power_mode(),
            'time_remaining_minutes': self.get_time_remaining_minutes()
        })
        if len(self.battery_history) > 1000:
            self.battery_history = self.battery_history[-1000:]
        self.save_battery_data()

    def get_battery_longevity_score(self) -> float:
        if not self.battery_history: return 100.0
        depth_of_discharge = [entry['battery_level'] for entry in self.battery_history if not entry['on_battery']]
        if not depth_of_discharge: return 100.0
        avg_low_level = sum(depth_of_discharge) / len(depth_of_discharge)
        score = 100.0 - (max(0, 40 - avg_low_level) * 1.5)
        return max(0, min(100, score))

    def get_smart_threshold_recommendation(self) -> Optional[int]:
        lpm_entries = [entry for entry in self.battery_history if entry['power_mode'] == 1]
        if len(lpm_entries) < 10: return None
        lpm_levels = [entry['battery_level'] for entry in lpm_entries]
        try:
            recommended = int((statistics.mode(lpm_levels) + statistics.median(lpm_levels)) / 2)
            return max(15, min(50, recommended))
        except:
            return None

    def get_battery_health_trends(self) -> Dict[str, Any]:
        if len(self.battery_history) < 10: return {'trend': 'insufficient_data', 'days': 0}
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_data = [entry for entry in self.battery_history if entry['timestamp'] > thirty_days_ago]
        if not recent_data: return {'trend': 'insufficient_data', 'days': 0}
        discharge_entries = [entry for entry in recent_data if entry['on_battery'] and entry['time_remaining_minutes']]
        avg_discharge_time = statistics.mean(entry['time_remaining_minutes'] for entry in discharge_entries) if discharge_entries else 180
        power_mode_ratio = sum(1 for entry in recent_data if entry['power_mode'] == 1) / len(recent_data)
        trend = 'fair'
        if power_mode_ratio > 0.3: trend = 'frequent_lpm'
        elif avg_discharge_time > 300: trend = 'excellent'
        elif avg_discharge_time > 240: trend = 'good'
        return {'trend': trend, 'days': (datetime.now() - recent_data[0]['timestamp']).days, 'avg_discharge_time': max(30, avg_discharge_time), 'power_mode_ratio': power_mode_ratio, 'cycles': self.charging_cycles}

    def load_config(self) -> Dict[str, Any]:
        default_config = {"threshold": 20, "threshold_mode": "percentage", "time_threshold_minutes": 90, "notifications": True, "setup_complete": True, "smart_auto_enabled": False}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except: pass
        return default_config

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump({"threshold": self.threshold, "threshold_mode": self.threshold_mode, "time_threshold_minutes": self.time_threshold_minutes, "notifications": self.config.get("notifications", True), "setup_complete": self.setup_complete, "smart_auto_enabled": self.smart_auto_enabled}, f, indent=2)
        except: pass

    def get_battery_level(self) -> Optional[int]:
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if '%' in line:
                    return int(line.split('\t')[-1].split(';')[0].replace('%', '').strip())
        except: pass
        return None

    def get_time_remaining(self) -> Optional[str]:
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'remaining' in line.lower():
                    match = re.search(r'(\d+:\d+)\s+remaining', line)
                    if match: return match.group(1)
        except: pass
        return None

    def get_time_remaining_minutes(self) -> Optional[int]:
        time_str = self.get_time_remaining()
        if not time_str: return None
        try:
            h, m = map(int, time_str.split(":"))
            return h * 60 + m
        except: return None

    def update_threshold_menu_title(self) -> None:
        if self.threshold_mode == "percentage":
            self.threshold_menu.title = "Threshold: Smart ✨" if self.smart_auto_enabled else f"Threshold: {self.threshold}%"
        else:
            self.threshold_menu.title = f"Threshold: {self.time_threshold_minutes} minutes"

    def get_threshold_mode_label(self) -> str:
        return "Mode: Battery % 🔄" if self.threshold_mode == "percentage" else "Mode: Time Remaining ⏱ 🔄"

    def toggle_threshold_mode(self, sender) -> None:
        self.threshold_mode = "time" if self.threshold_mode == "percentage" else "percentage"
        self.save_config()
        sender.title = self.get_threshold_mode_label()
        self.update_threshold_menu_title()
        self.build_threshold_submenu()

    def is_on_battery(self) -> bool:
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            return 'Battery Power' in result.stdout
        except: return False

    def get_power_mode(self) -> Optional[int]:
        try:
            result = subprocess.run(['pmset', '-g', 'custom'], capture_output=True, text=True, timeout=5)
            curr_section = ""
            for line in result.stdout.split('\n'):
                if 'Battery Power:' in line: curr_section = "batt"
                elif 'AC Power:' in line: curr_section = "ac"
                if 'lowpowermode' in line.lower():
                    val = int(line.strip().split()[-1])
                    if (curr_section == "batt" and self.is_on_battery()) or (curr_section == "ac" and not self.is_on_battery()):
                        return val
        except: pass
        return 0

    def get_battery_health(self) -> Optional[Dict[str, str]]:
        try:
            result = subprocess.run(['system_profiler', 'SPPowerDataType'], capture_output=True, text=True, timeout=10)
            health = {}
            for line in result.stdout.split('\n'):
                if 'Cycle Count:' in line: health['cycle_count'] = line.split(':')[1].strip()
                elif 'Condition:' in line: health['condition'] = line.split(':')[1].strip()
                elif 'Maximum Capacity:' in line: health['max_capacity'] = line.split(':')[1].strip()
            return health
        except: return None

    def set_power_mode(self, mode: int) -> bool:
        try:
            if subprocess.run(['sudo', '-n', 'pmset', '-b', 'lowpowermode', str(mode)], capture_output=True, timeout=5).returncode == 0:
                return True
            script = f'do shell script "pmset -b lowpowermode {mode}" with administrator privileges'
            return subprocess.run(['osascript', '-e', script], capture_output=True, timeout=30).returncode == 0
        except: return False

    def should_trigger_threshold(self) -> bool:
        if self.threshold_mode == "percentage":
            lvl = self.get_battery_level()
            return lvl is not None and lvl <= self.threshold
        rem = self.get_time_remaining_minutes()
        return rem is not None and rem <= self.time_threshold_minutes

    def check_battery_on_launch(self) -> None:
        lvl = self.get_battery_level()
        if lvl and self.is_on_battery() and self.should_trigger_threshold() and self.get_power_mode() != 1:
            self.set_power_mode(1)

    def check_battery(self, _) -> None:
        lvl = self.get_battery_level()
        if lvl is None: return
        self.record_battery_data()
        self.last_battery_level = lvl
        self.update_icon()
        if self.smart_auto_enabled and self.threshold_mode == "percentage":
            smart = self.get_smart_threshold_recommendation()
            if smart and smart != self.threshold:
                self.threshold = smart
                self.save_config()
                self.update_threshold_menu_title()
                self.build_threshold_submenu()
        if self.is_on_battery() and self.should_trigger_threshold() and self.get_power_mode() != 1:
            if self.set_power_mode(1) and not self.notification_shown:
                rumps.notification(title="LowPower Automator Pro", message="Low Power Mode enabled automatically")
                self.notification_shown = True
        else: self.notification_shown = False

    def show_launch_notification(self, timer) -> None:
        timer.stop()
        rumps.notification(title="LowPower Automator Pro", message="App is active in menu bar")

    def update_icon(self) -> None:
        lvl = self.last_battery_level
        mode = self.get_power_mode()
        if mode == 1: self.title = "💤"
        elif not self.is_on_battery(): self.title = "🔌"
        else: self.title = "🪫" if lvl <= 20 else "🔋"

    def build_threshold_submenu(self):
        self.threshold_menu.clear()
        if self.threshold_mode == "percentage":
            for p in range(10, 100, 10):
                self.threshold_menu.add(rumps.MenuItem(f"{'✓ ' if p==self.threshold else ''}{p}%", callback=self.change_threshold))
        else:
            for m in [60, 90, 120, 180, 240]:
                self.threshold_menu.add(rumps.MenuItem(f"{'✓ ' if m==self.time_threshold_minutes else ''}{m} mins", callback=self.change_time_threshold))

    def change_threshold(self, sender):
        self.threshold = int(sender.title.replace('✓','').replace('%','').strip())
        self.save_config()
        self.update_threshold_menu_title()
        self.build_threshold_submenu()

    def change_time_threshold(self, sender):
        self.time_threshold_minutes = int(sender.title.replace('✓','').replace('mins','').strip())
        self.save_config()
        self.update_threshold_menu_title()
        self.build_threshold_submenu()

    def show_battery_info(self, _):
        lvl = self.get_battery_level()
        msg = f"Level: {lvl}%\nSource: {'Battery' if self.is_on_battery() else 'AC'}\nThreshold: {self.threshold}%"
        rumps.alert(title="Battery Info", message=msg)

    def show_power_mode(self, _):
        m = self.get_power_mode()
        rumps.alert(title="Low Power Mode" if m==1 else "Normal Mode")

    def show_battery_analytics(self, _):
        rumps.alert(title="Analytics", message="Data collection in progress...")

    def show_about(self, _):
        rumps.alert(title="LowPower Automator Pro", message="v2.0.0 Pro\n© 2025 Daniel Alan Bates")

    def show_first_launch_setup(self, timer):
        timer.stop()
        self.setup_complete = True
        self.save_config()

if __name__ == "__main__":
    app = LowPowerAutomator()
    app.run()
