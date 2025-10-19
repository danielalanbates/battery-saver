# Battery Saver - Icon Style Guide

Battery Saver offers two versions with different menu bar icon styles to complement the macOS system battery icon.

## Version Comparison

### Standard Version (`battery_saver.py`)

**Icon Behavior:**
- 🍃 **Leaf** - Low Power Mode is active
- ⚡ **Lightning** - Monitoring active (default state)
- ⚠️ **Warning** - Battery ≤ 20%

**When to use:**
- You want a clear visual indicator of Low Power Mode status
- The leaf emoji (🍃) immediately shows when power saving is active
- You prefer emoji-based indicators

**Location in menu bar:**
- Will appear near other menu bar apps
- Position depends on launch order (earlier launch = further right)

---

### Minimal Version (`battery_saver_minimal.py`)

**Icon Behavior:**
- 🍃 **Leaf** - Low Power Mode is active
- ⚡ **Lightning** - Monitoring active (default)
- **XX%** - Battery percentage (optional toggle)

**Additional Features:**
- Toggle to show/hide battery percentage in menu bar
- Option to display percentage next to system battery icon
- More minimal appearance

**Menu Options:**
- Everything from standard version, plus:
- "Show Percentage" / "Hide Percentage" toggle

**When to use:**
- You want the app icon next to the system battery
- You prefer showing battery percentage as text
- You want the most minimal appearance

---

## Icon Position in Menu Bar

### macOS Menu Bar Layout

```
[Apple Logo] [App Menus...]        [...Menu Bar Items] [Battery] [Clock]
                                    ← Apps load here →
```

### Positioning Your Battery Saver Icon

To get Battery Saver **close to the system battery icon**:

1. **Launch Battery Saver LAST** (after other menu bar apps)
2. **Use a minimal icon style** (⚡ or XX%)
3. **Enable "Show Percentage"** (minimal version only)

### Launch Order Trick

Menu bar apps appear from **right to left** based on launch order:
- First app launched → furthest right
- Last app launched → furthest left (closer to battery/clock)

**To position next to system battery:**

```bash
# 1. Quit all other menu bar apps (if possible)
# 2. Launch Battery Saver
./start_battery_saver.sh

# 3. Relaunch other menu bar apps
```

Or use LaunchAgent with higher `ProcessType`:

```xml
<key>ProcessType</key>
<string>Interactive</string>
<key>Nice</key>
<integer>-20</integer>  <!-- Launch early -->
```

---

## Icon Appearance Examples

### Standard Version

**Normal state (on AC power):**
```
[⚡] Battery Saver
```

**Low Power Mode active:**
```
[🍃] Battery Saver
```

**Low battery warning:**
```
[⚠️] Battery Saver
```

### Minimal Version

**Default (minimal):**
```
[⚡]
```

**Low Power Mode active:**
```
[🍃]
```

**With percentage enabled:**
```
[85%]
```

**Next to system battery:**
```
[...other apps] [⚡] [🔋 100%] [12:34 PM]
                 ↑       ↑
          Battery Saver  System Battery
```

---

## Icon Meanings

### Leaf Icon 🍃
- **Meaning:** Low Power Mode is currently active
- **When shown:** Power mode is set to Low Power (mode 1)
- **Why leaf:** Universal symbol for eco/power saving mode
- **Color:** Green (on most systems)

### Lightning Bolt ⚡
- **Meaning:** App is monitoring, Low Power Mode not active
- **When shown:** Default state when monitoring
- **Why lightning:** Related to power/electricity
- **Also used:** When on AC power

### Warning ⚠️
- **Meaning:** Battery is critically low (≤20%)
- **When shown:** Battery level drops to 20% or below
- **Why warning:** Alerts you to low battery
- **Color:** Yellow/amber (on most systems)

### Percentage (XX%)
- **Meaning:** Current battery level
- **When shown:** When "Show Percentage" is enabled (minimal version)
- **Why useful:** Quick glance at battery without clicking
- **Example:** "85%", "42%", "15%"

---

## Customization Options

### Change the Default Icon

Edit the `update_icon()` method in either version:

```python
def update_icon(self) -> None:
    # Option 1: Always show percentage
    self.title = f"{self.last_battery_level}%"

    # Option 2: Simple dot indicator
    self.title = "●"  # or "•" or "◆"

    # Option 3: Text-based
    self.title = "LPM" if power_mode == 1 else "BAT"

    # Option 4: Numbers only
    self.title = f"{self.threshold}"  # Show threshold
```

### Create Your Own Icon Style

1. Copy `battery_saver.py` to `battery_saver_custom.py`
2. Modify the `update_icon()` method
3. Choose your preferred symbols:
   - Emoji: ⚡🔋🪫🍃⚠️💚💛🔴⏸️▶️●◆★
   - Text: "BAT", "LPM", "PWR", "LOW"
   - Numbers: Battery %, Threshold, Minutes remaining
   - Symbols: ▲▼◄►■□●○

---

## Which Version Should You Use?

### Use **Standard Version** if:
- ✅ You want clear visual feedback
- ✅ You like emoji indicators
- ✅ You want to know when Low Power Mode is active at a glance
- ✅ You don't mind the icon position

### Use **Minimal Version** if:
- ✅ You want to show battery percentage
- ✅ You prefer a cleaner look
- ✅ You want the icon next to system battery
- ✅ You toggle the percentage display on/off

### Use Both! (Advanced)
- Run standard version normally
- Use minimal version for specific scenarios
- **Note:** Don't run both at the same time (conflicts)

---

## Installation

### Standard Version (Default)
```bash
./start_battery_saver.sh
# or
python3 battery_saver.py
```

### Minimal Version
```bash
python3 battery_saver_minimal.py
```

### Auto-Launch Setup

To change which version auto-launches, edit `com.daniel.batterysaver.plist`:

```xml
<!-- For standard version -->
<string>/Users/daniel/Documents/aicode/Battery_saver/battery_saver.py</string>

<!-- For minimal version -->
<string>/Users/daniel/Documents/aicode/Battery_saver/battery_saver_minimal.py</string>
```

Then reinstall:
```bash
./uninstall_launch_agent.sh
./install_launch_agent.sh
```

---

## Tips for Best Appearance

### Tip 1: Use Minimal Icons
Smaller icons blend better with macOS UI:
- ⚡ Lightning (default)
- 🍃 Leaf (Low Power Mode)
- XX% Percentage

### Tip 2: Launch Order
Launch Battery Saver after other menu bar apps to position it closer to the system battery.

### Tip 3: Hide System Battery Percentage
If using minimal version with percentage:
1. System Settings → Control Center → Battery
2. Turn off "Show Percentage" in system battery
3. Enable "Show Percentage" in Battery Saver
4. Now you have one clean percentage display

### Tip 4: Bartender/Hidden Bar
Use menu bar management apps to organize icons:
- [Bartender](https://www.macbartender.com/)
- [Hidden Bar](https://github.com/dwarvesf/hidden)
- [Dozer](https://github.com/Mortennn/Dozer)

These let you position Battery Saver exactly where you want it.

---

## FAQ

**Q: Can I move the icon manually?**
A: No, macOS doesn't allow dragging menu bar icons (except system ones with ⌘-drag). Position is determined by launch order.

**Q: Why doesn't it appear next to the battery?**
A: Launch order determines position. Try launching Battery Saver last, or use a menu bar manager app.

**Q: Can I use a custom image icon?**
A: Yes, but requires using rumps' `icon` parameter with a `.png` file. See rumps documentation for details.

**Q: The icon is too big/small**
A: Icon size is determined by macOS. Use text-based icons (%, numbers) for smaller appearance.

**Q: Can I hide the icon completely?**
A: Not recommended - you won't see when Low Power Mode activates. But you could set `self.title = ""` for no icon.

---

## Examples from Other Apps

Similar menu bar apps that sit near battery:
- **iStat Menus** - Shows system stats with icons
- **AlDente** - Battery charge limiting (shows percentage)
- **coconutBattery** - Battery health (shows battery icon)
- **Amphetamine** - Keep awake utility (shows coffee cup)

Battery Saver's 🍃 leaf icon is unique and distinguishable from these.

---

**Last Updated:** October 18, 2025
**Applies to:** Battery Saver v1.0.0
