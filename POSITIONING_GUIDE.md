# Battery Saver - Menu Bar Positioning Guide

This guide explains how to position Battery Saver's icon next to the macOS system battery icon.

## Understanding macOS Menu Bar Layout

### Default Menu Bar Structure

```
┌─────────────────────────────────────────────────────────┐
│  [Menu Items] ... [App Icons] [Battery] [Time]         │
└─────────────────────────────────────────────────────────┘
                      ←          →
              Right-to-left based on launch order
```

### How Apps are Positioned

Menu bar apps are positioned **right-to-left** based on launch order:
- **Last launched** → Furthest right (closest to battery/clock)
- **First launched** → Furthest left

**System icons (Battery, WiFi, Clock) are always rightmost and cannot be moved.**

## Method 1: Launch Order (Simple)

### Step-by-Step

1. **Quit other menu bar apps** (if you want Battery Saver closest to battery):
   ```bash
   # Find menu bar apps
   ps aux | grep -i "menu\|statusbar"

   # Quit specific apps (example)
   killall "Dropbox" "Bartender" "Alfred"
   ```

2. **Launch Battery Saver LAST**:
   ```bash
   cd /Users/daniel/Documents/aicode/Battery_saver
   ./start_battery_saver_minimal.sh  # Minimal version recommended
   ```

3. **Relaunch other apps** (they'll appear to the left of Battery Saver)

### Result

```
[Other Apps] [⚡] [🔋] [Clock]
              ↑    ↑
        Battery   System
         Saver   Battery
```

## Method 2: LaunchAgent Priority (Automatic)

### Make Battery Saver Launch Early

Edit `com.daniel.batterysaver.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.daniel.batterysaver</string>

    <!-- Use minimal version for better positioning -->
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/daniel/Documents/aicode/Battery_saver/battery_saver_minimal.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <!-- Priority: Higher number = later launch = closer to battery -->
    <key>Nice</key>
    <integer>20</integer>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/battery_saver.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/battery_saver_error.log</string>
</dict>
</plist>
```

### Install Modified LaunchAgent

```bash
./uninstall_launch_agent.sh
./install_launch_agent.sh
```

Now Battery Saver will auto-launch in the correct position.

## Method 3: Menu Bar Manager Apps (Best)

### Use Third-Party Tools

These apps give you **full control** over menu bar icon positioning:

#### Bartender 5 (Paid, $18)
- Drag and drop icon positioning
- Hide/show icons
- Custom icon spacing
- **Best for precise control**

Download: https://www.macbartender.com/

#### Hidden Bar (Free, Open Source)
- Hide icons behind a separator
- Simple one-click show/hide
- Lightweight

Download: https://github.com/dwarvesf/hidden

#### Dozer (Free, Open Source)
- Hide/show icons
- Minimalist design
- Lightweight

Download: https://github.com/Mortennn/Dozer

### Setup with Bartender Example

1. Install Bartender
2. Launch Battery Saver (minimal version)
3. Open Bartender preferences
4. Drag Battery Saver icon next to system battery
5. Click "Save arrangement"

**Result:** Battery Saver always appears next to system battery, regardless of launch order.

## Recommended Setup

### For Best Results

**1. Use Minimal Version**
```bash
python3 battery_saver_minimal.py
```
- Smaller icon (⚡ or XX%)
- Blends better with system icons
- Less visual clutter

**2. Enable Battery Percentage**
- Click Battery Saver icon
- Select "Show Percentage"
- Now displays: `85%` instead of `⚡`

**3. Hide System Battery Percentage** (Optional)
- System Settings → Control Center → Battery
- Turn off "Show Percentage"
- Now you have one clean percentage display from Battery Saver

**Visual Result:**
```
[...Apps] [85%] [🔋] [2:30 PM]
           ↑     ↑
      Battery   System
       Saver   Battery
              (no %)
```

## Icon Style Recommendations

### For Positioning Next to System Battery

**Best Icons:**
- `⚡` - Lightning bolt (default)
- `XX%` - Percentage (minimal version)
- `🍃` - Leaf (when Low Power Mode active)

**Avoid:**
- Large emoji (🔋🪫)
- Warning icons (⚠️) as default
- Text labels ("Battery Saver")

### Comparison

**Good (Minimal):**
```
[⚡] [🔋 100%] [Clock]
 ↑      ↑
Clean  System
```

**Less Ideal (Standard):**
```
[🔋] [🔋 100%] [Clock]
 ↑      ↑
Duplicate battery icons = confusing
```

## Troubleshooting

### Issue: Battery Saver appears far from system battery

**Cause:** Other apps launched after Battery Saver

**Fix:** Use Method 3 (Bartender/Hidden Bar) or relaunch in correct order

### Issue: Icon keeps moving on restart

**Cause:** LaunchAgent load order is inconsistent

**Fix:**
1. Use Bartender to lock position
2. Or adjust `Nice` priority in plist file
3. Or manually launch after login

### Issue: Too many icons, can't see Battery Saver

**Cause:** Menu bar is crowded

**Fix:**
1. Hide unused menu bar apps
2. Use Bartender/Hidden Bar to organize
3. Enable "Show Percentage" in Battery Saver (easier to spot)

### Issue: Can't tell Battery Saver apart from system battery

**Good!** That's the minimal design working. Key differences:
- Battery Saver shows `🍃` when Low Power Mode is active
- System battery never shows leaf icon
- Battery Saver responds to clicks with custom menu

## Advanced: Custom Icon Position Script

### Auto-Reorder on Login

Create `~/Library/Scripts/reorder_menubar.sh`:

```bash
#!/bin/bash
# Reorder menu bar icons on login

# Wait for desktop to load
sleep 10

# Quit all menu bar apps
killall Dropbox 2>/dev/null
killall Alfred 2>/dev/null
# ... add your apps

# Launch in desired order (last = rightmost)
sleep 2
open -a Dropbox
sleep 1
open -a Alfred
sleep 1

# Launch Battery Saver last
cd /Users/daniel/Documents/aicode/Battery_saver
./start_battery_saver_minimal.sh
```

### Make it Run on Login

1. System Settings → Users & Groups → Login Items
2. Click `+` button
3. Add `reorder_menubar.sh`

Now icons auto-arrange on every login!

## Summary

### Quick Answer: How to Get Battery Saver Next to System Battery

**Easiest:** Use Bartender ($18) - drag and drop positioning

**Free:** Launch Battery Saver last:
```bash
./start_battery_saver_minimal.sh
```

**Automatic:** Modify LaunchAgent plist with higher `Nice` value

**Best Looking:** Use minimal version + enable percentage display

---

## Visual Examples

### Layout Option 1: Side-by-Side
```
[Apps...] [⚡] [🔋 100%] [Time]
```
Battery Saver (⚡) next to system battery

### Layout Option 2: Percentage Display
```
[Apps...] [85%] [🔋] [Time]
```
Battery Saver shows percentage, system battery icon only

### Layout Option 3: Low Power Mode Active
```
[Apps...] [🍃] [🔋 100%] [Time]
```
Leaf icon indicates Low Power Mode is ON

### Layout Option 4: Hidden System Percentage
```
[Apps...] [85%] [🔋] [Time]
```
Only Battery Saver shows percentage (cleanest look)

---

**Pro Tip:** Use the minimal version with percentage display and hide the system battery percentage for the cleanest, most functional setup!

---

**Last Updated:** October 18, 2025
**Applies to:** Battery Saver v1.0.0
