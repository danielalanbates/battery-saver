#!/usr/bin/env python3
"""
Test script for Battery Saver functions
Tests battery monitoring and power mode detection without GUI
"""

import subprocess
import re


def get_battery_level():
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


def is_on_battery():
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


def get_power_mode():
    """Get current power mode."""
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
                        mode = int(parts[-1])
                        return mode
        return None
    except Exception as e:
        print(f"Error getting power mode: {e}")
        return None


def main():
    """Run tests."""
    print("=" * 60)
    print("Battery Saver - Function Tests")
    print("=" * 60)
    print()

    # Test 1: Battery Level
    print("Test 1: Get Battery Level")
    battery = get_battery_level()
    if battery is not None:
        print(f"✅ Battery level: {battery}%")
    else:
        print("❌ Failed to get battery level")
    print()

    # Test 2: Power Source
    print("Test 2: Check Power Source")
    on_battery = is_on_battery()
    source = "Battery Power" if on_battery else "AC Power"
    print(f"✅ Power source: {source}")
    print()

    # Test 3: Power Mode
    print("Test 3: Get Power Mode")
    mode = get_power_mode()
    mode_names = {
        0: "Normal/Automatic",
        1: "Low Power Mode",
        2: "High Power Mode"
    }
    if mode in mode_names:
        print(f"✅ Current power mode: {mode_names[mode]} (mode {mode})")
    else:
        print(f"❌ Unknown power mode: {mode}")
    print()

    # Test 4: Simulation
    print("Test 4: Simulate Battery Threshold Check")
    threshold = 20
    print(f"   Threshold set to: {threshold}%")
    print(f"   Current battery: {battery}%")
    print(f"   On battery power: {on_battery}")

    if battery is not None:
        if on_battery and battery <= threshold:
            print(f"✅ Would activate Low Power Mode (battery {battery}% ≤ {threshold}%)")
        elif not on_battery:
            print(f"⏸️  Would NOT activate (on AC power)")
        else:
            print(f"⏸️  Would NOT activate (battery {battery}% > {threshold}%)")
    print()

    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
