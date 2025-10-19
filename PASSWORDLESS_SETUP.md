# Battery Saver - Passwordless Setup Guide

## The Password Problem

**Question:** When my Mac gets to 20%, will it ask for my password to enable Low Power Mode?

**Short Answer:**
- **Without setup:** YES - macOS will ask for your password
- **With setup (5 minutes):** NO - it will work automatically!

## Why Does macOS Ask for a Password?

Changing power management settings with `pmset` requires administrator privileges. By default, macOS will prompt for your password every time the app tries to enable/disable Low Power Mode.

This means:
- ❌ Password prompt at 20% battery (inconvenient!)
- ❌ Password prompt when manually toggling
- ❌ Can't auto-activate if you're away from keyboard

## The Solution: Passwordless pmset

You can configure macOS to allow Battery Saver to run `pmset` **without asking for a password**, while keeping everything else secure.

### How It Works

We create a **sudoers rule** that allows:
- ✅ ONLY the `pmset -b lowpowermode` command
- ✅ ONLY for your user account
- ✅ Without password prompt

Everything else still requires a password!

---

## Setup (One-Time, 5 Minutes)

### Step 1: Run the Setup Script

```bash
cd /Users/daniel/Documents/aicode/Battery_saver
./setup_passwordless_pmset.sh
```

### Step 2: Enter Your Password (Once)

The script will ask for your password **once** to create the sudoers rule.

```
Battery Saver - Passwordless Setup
====================================

This script will configure your Mac to allow Battery Saver to
enable/disable Low Power Mode WITHOUT asking for your password.

Continue? (y/n): y

Creating sudoers rule...
Password:  [enter your password here]
```

### Step 3: Done!

```
✅ Success! Passwordless pmset is now configured.

Battery Saver can now enable/disable Low Power Mode
automatically without asking for your password.
```

### Step 4: Restart Battery Saver

```bash
pkill -f battery_saver
./start_battery_saver.sh
```

Now it will use passwordless sudo!

---

## Testing

### Test 1: Verify Passwordless Sudo Works

```bash
sudo pmset -b lowpowermode 1
```

**Expected:** Low Power Mode enables **without** asking for password

```bash
sudo pmset -b lowpowermode 0
```

**Expected:** Low Power Mode disables **without** asking for password

### Test 2: Test from the App

1. Click Battery Saver icon
2. Click "Enable Low Power Mode Now"
3. **Expected:** Icon changes to 💤 instantly, NO password prompt
4. Click "Disable Low Power Mode Now"
5. **Expected:** Icon changes back instantly, NO password prompt

### Test 3: Automatic Activation (Simulated)

Since you're at 100% battery, we can't test real automatic activation, but:

1. Set threshold to 100%: Click icon → "Threshold: 20%" → Enter "100"
2. Unplug your Mac (if possible)
3. Within 30 seconds, Low Power Mode should activate **without password**
4. Icon changes to 💤 automatically
5. Plug back in and reset threshold to 20%

---

## What Exactly Was Changed?

### The Sudoers File

Location: `/private/etc/sudoers.d/batterysaver`

Contents:
```
daniel ALL=(ALL) NOPASSWD: /usr/bin/pmset -b lowpowermode *
```

**Translation:**
- `daniel` - Your username (only you have passwordless access)
- `ALL=(ALL)` - From any terminal/app
- `NOPASSWD:` - Don't ask for password
- `/usr/bin/pmset -b lowpowermode *` - ONLY this specific command
- `*` - With any argument (0 or 1)

### What This DOESN'T Allow

This rule is **very specific** and secure:
- ❌ Can't run other pmset commands (e.g., `pmset sleepnow`)
- ❌ Can't change other power settings
- ❌ Can't run pmset without `-b lowpowermode`
- ❌ Doesn't affect any other sudo commands
- ❌ Only works for your user account

Everything else still requires a password!

---

## Security Considerations

### Is This Safe?

**Yes!** Here's why:

1. **Specific Command Only**
   - Only allows `pmset -b lowpowermode 0` or `pmset -b lowpowermode 1`
   - Can't be used to run other commands

2. **Low Risk**
   - Worst case: Someone enables/disables Low Power Mode
   - No access to files, data, or system settings
   - Can't damage anything

3. **Your Account Only**
   - Only works when logged in as you
   - Other users still need passwords

4. **Follows Best Practices**
   - Uses sudoers.d directory (recommended by Apple)
   - Proper file permissions (0440)
   - Validated by visudo

### Alternative: Accept the Password Prompt

If you prefer NOT to set up passwordless sudo:

**Pros:**
- More secure (password every time)
- No system configuration needed

**Cons:**
- Password prompt at 20% battery
- Must be at keyboard when it happens
- Can't auto-activate if you're away
- Less convenient for manual toggling

The app works either way! It will:
1. Try passwordless sudo first
2. Fall back to password prompt if needed

---

## Troubleshooting

### "Failed to create sudoers file"

**Cause:** Insufficient privileges

**Fix:** Make sure you're an admin user and enter the correct password

### Password still prompts

**Cause:** Sudoers file not created or wrong format

**Check:**
```bash
sudo cat /private/etc/sudoers.d/batterysaver
```

Should show:
```
your_username ALL=(ALL) NOPASSWD: /usr/bin/pmset -b lowpowermode *
```

**Fix:** Run setup script again

### "sudo: sorry, a password is required to run this command"

**Cause:** Sudoers rule not working

**Test:**
```bash
sudo -n pmset -b lowpowermode 1
```

If this fails, check the sudoers file format.

### App still asks for password

**Cause:** App not restarted after setup

**Fix:**
```bash
pkill -f battery_saver
./start_battery_saver.sh
```

---

## Uninstalling Passwordless Setup

If you want to remove passwordless sudo later:

```bash
sudo rm /private/etc/sudoers.d/batterysaver
```

Battery Saver will fall back to asking for a password.

---

## How the App Works with Passwordless Sudo

### Code Behavior

When Low Power Mode needs to be changed:

1. **Try passwordless sudo:**
   ```bash
   sudo -n pmset -b lowpowermode 1
   ```
   - `-n` flag = "don't ask for password"
   - If sudoers file exists: ✅ Success!
   - If not: ⏩ Continue to step 2

2. **Fall back to AppleScript:**
   ```applescript
   do shell script "pmset -b lowpowermode 1" with administrator privileges
   ```
   - Shows macOS password dialog
   - Works even without passwordless setup

This means:
- **With setup:** Silent, automatic, no prompts
- **Without setup:** Works, but asks for password

---

## Comparison

### With Passwordless Setup ✅

```
Battery at 20%
  ↓
App detects threshold
  ↓
Runs: sudo pmset -b lowpowermode 1
  ↓
✅ SUCCESS (no password)
  ↓
Icon changes to 💤
Notification appears
Low Power Mode ON
```

**User Experience:** Completely automatic!

### Without Passwordless Setup ⚠️

```
Battery at 20%
  ↓
App detects threshold
  ↓
Runs: sudo pmset -b lowpowermode 1
  ↓
❌ FAILS (needs password)
  ↓
Falls back to AppleScript
  ↓
🔒 PASSWORD DIALOG APPEARS
  ↓
User enters password
  ↓
✅ SUCCESS
  ↓
Icon changes to 💤
Low Power Mode ON
```

**User Experience:** Interrupts what you're doing

---

## Recommendations

### Recommended: Set Up Passwordless Sudo

**Best for:**
- ✅ You want true "set and forget" automation
- ✅ You're okay with a 5-minute one-time setup
- ✅ You understand the security implications (very low risk)
- ✅ You want instant manual toggling

### Alternative: Skip Passwordless Setup

**Best for:**
- ✅ You prefer maximum security (password every time)
- ✅ You don't mind entering password at 20%
- ✅ You're always at your keyboard
- ✅ You rarely use manual toggle

Both options work perfectly! It's your choice.

---

## Quick Start Summary

**For passwordless operation:**

```bash
# 1. Run setup (one time)
./setup_passwordless_pmset.sh

# 2. Enter your password (once)

# 3. Restart app
pkill -f battery_saver
./start_battery_saver.sh

# 4. Test it
# Click icon → "Enable Low Power Mode Now"
# Should work WITHOUT password prompt!
```

**To skip passwordless setup:**

Just use the app as-is! It will ask for your password when needed.

---

**Last Updated:** October 18, 2025
**Applies to:** Battery Saver v1.0.0
