#!/usr/bin/env python3
"""Test the fixed power mode detection"""

import subprocess

def get_power_mode():
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

print("Testing power mode detection...")
print(f"Current Low Power Mode status: {get_power_mode()}")
print("0 = OFF, 1 = ON")
