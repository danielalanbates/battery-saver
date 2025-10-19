#!/usr/bin/env python3
"""
Battery Saver Control - CLI tool to manage the background daemon
Copyright (c) 2025 Daniel
Licensed under the MIT License
"""

import json
import os
import subprocess
import sys


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".battery_saver_config.json")
LOG_PATH = os.path.join(os.path.expanduser("~"), ".battery_saver_daemon.log")


def load_config():
    """Load current configuration."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"threshold": 20, "enabled": True, "notifications": True, "check_interval": 30}


def save_config(config):
    """Save configuration."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def show_status():
    """Show current status."""
    config = load_config()

    print("=" * 50)
    print("Battery Saver - Status")
    print("=" * 50)
    print(f"Monitoring: {'✅ Enabled' if config.get('enabled', True) else '❌ Disabled'}")
    print(f"Threshold: {config.get('threshold', 20)}%")
    print(f"Notifications: {'✅ On' if config.get('notifications', True) else '❌ Off'}")
    print(f"Check Interval: {config.get('check_interval', 30)}s")
    print()

    # Check if daemon is running
    result = subprocess.run(
        ['pgrep', '-f', 'battery_saver_daemon.py'],
        capture_output=True
    )

    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"Daemon: 🟢 Running (PID: {', '.join(pids)})")
    else:
        print("Daemon: 🔴 Not running")

    # Show recent logs
    if os.path.exists(LOG_PATH):
        print("\nRecent logs:")
        print("-" * 50)
        with open(LOG_PATH, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(line.rstrip())

    print("=" * 50)


def set_threshold(value):
    """Set battery threshold."""
    try:
        threshold = int(value)
        if 5 <= threshold <= 95:
            config = load_config()
            config['threshold'] = threshold
            save_config(config)
            print(f"✅ Threshold set to {threshold}%")
        else:
            print("❌ Threshold must be between 5% and 95%")
    except ValueError:
        print("❌ Invalid threshold value")


def enable():
    """Enable monitoring."""
    config = load_config()
    config['enabled'] = True
    save_config(config)
    print("✅ Monitoring enabled")


def disable():
    """Disable monitoring."""
    config = load_config()
    config['enabled'] = False
    save_config(config)
    print("❌ Monitoring disabled")


def show_help():
    """Show help message."""
    print("""
Battery Saver Control

Usage:
    python3 battery_control.py <command> [options]

Commands:
    status              Show current status and recent logs
    threshold <percent> Set battery threshold (5-95)
    enable              Enable automatic monitoring
    disable             Disable automatic monitoring
    start               Start the daemon
    stop                Stop the daemon
    restart             Restart the daemon
    logs                Show recent log entries
    help                Show this help message

Examples:
    python3 battery_control.py status
    python3 battery_control.py threshold 25
    python3 battery_control.py enable
    python3 battery_control.py start
""")


def show_logs():
    """Show recent logs."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r') as f:
            print(f.read())
    else:
        print("No logs found")


def start_daemon():
    """Start the background daemon."""
    # Check if already running
    result = subprocess.run(
        ['pgrep', '-f', 'battery_saver_daemon.py'],
        capture_output=True
    )

    if result.returncode == 0:
        print("⚠️  Daemon is already running")
        return

    # Start daemon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    daemon_script = os.path.join(script_dir, 'battery_saver_daemon.py')

    subprocess.Popen(
        ['python3', daemon_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    print("✅ Daemon started")


def stop_daemon():
    """Stop the background daemon."""
    result = subprocess.run(
        ['pkill', '-f', 'battery_saver_daemon.py'],
        capture_output=True
    )

    if result.returncode == 0:
        print("✅ Daemon stopped")
    else:
        print("⚠️  Daemon was not running")


def restart_daemon():
    """Restart the daemon."""
    stop_daemon()
    import time
    time.sleep(1)
    start_daemon()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "status":
        show_status()
    elif command == "threshold":
        if len(sys.argv) < 3:
            print("❌ Please specify threshold percentage")
        else:
            set_threshold(sys.argv[2])
    elif command == "enable":
        enable()
    elif command == "disable":
        disable()
    elif command == "start":
        start_daemon()
    elif command == "stop":
        stop_daemon()
    elif command == "restart":
        restart_daemon()
    elif command == "logs":
        show_logs()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)
