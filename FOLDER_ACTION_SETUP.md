# Folder Action Setup (Alternative to Daemon)

Using macOS Folder Actions instead of a background daemon has several advantages:
- ✅ **Better permissions**: Runs in user context, easier to grant access
- ✅ **Native macOS integration**: Uses built-in Folder Actions
- ✅ **Visual feedback**: Can show notifications when conversions complete
- ✅ **No daemon management**: No need for launchd
- ✅ **Easy to enable/disable**: Toggle in System Settings

## Quick Setup

### Step 1: Run Setup Script

```bash
cd /Users/omri.a/Code/pdf-to-md
./setup_folder_action.sh
```

This creates the necessary wrapper scripts.

### Step 2: Create Folder Action via Automator

#### Option A: GUI Method (Recommended)

1. Open **Automator** app (in `/Applications`)

2. Choose **"New Document"** → **"Folder Action"**

3. At the top, **"Folder Action receives files and folders added to:"**
   - Choose your folder (e.g., Downloads, Desktop, or create a new one)

4. In the left sidebar, search for **"Run Shell Script"**

5. Drag **"Run Shell Script"** to the workflow area

6. Configure the action:
   - **Shell**: `/bin/bash`
   - **Pass input**: `as arguments`
   - **Script** (replace with your actual path):
   ```bash
   /Users/omri.a/Code/pdf-to-md/convert_pdf_folder_action.sh "$@"
   ```

7. **Save** as: "PDF to Markdown Converter" (or any name)
   - Location: `~/Library/Workflows/Applications/Folder Actions/`

8. The Folder Action is now active!

#### Option B: Command Line Method

```bash
# Open Folder Actions Setup
open -a "Folder Actions Setup"

# Or directly open Automator
open -a Automator
```

### Step 3: Enable Folder Actions

1. Go to **System Settings** → **Extensions** → **Finder**
2. Enable **"Folder Actions"**

### Step 4: Test It!

Drop a PDF file into your watched folder - it should automatically convert!

Check the log:
```bash
tail -f ~/Library/Logs/pdf-to-md.log
```

## Advantages Over Daemon Approach

| Feature | Daemon (launchd) | Folder Action |
|---------|------------------|---------------|
| Permission Issues | ❌ Needs Full Disk Access | ✅ User context |
| Setup Complexity | Medium | Easy (GUI) |
| System Resources | Always running | Only when triggered |
| Visual Feedback | Log files only | Can show notifications |
| Enable/Disable | Terminal commands | System Settings toggle |

## Advanced: Add Notifications

To get visual feedback when conversions complete, modify the Automator workflow:

1. Add **"Display Notification"** action after the shell script
2. Configure message: "PDF converted successfully"

Or add to the shell script:
```bash
osascript -e 'display notification "PDF converted to Markdown" with title "PDF Converter"'
```

## Troubleshooting

### Folder Action not triggering

1. Check if Folder Actions are enabled:
   - **System Settings** → **Extensions** → **Finder** → **Folder Actions**

2. Verify workflow is attached to folder:
   - Right-click folder → **Services** → **Folder Action Setup**
   - Your workflow should be listed

3. Check permissions:
   - **System Settings** → **Privacy & Security** → **Automation**
   - Ensure Automator can control Finder

### Permission errors

If you still get permission errors with Downloads:
- Use a different folder (Desktop, Documents/PDFs)
- Or grant **Automator** Full Disk Access instead of Python

### View active Folder Actions

```bash
# List all folder actions
ls ~/Library/Workflows/Applications/Folder\ Actions/

# Open Folder Actions Setup
open -a "Folder Actions Setup"
```

## Switching from Daemon to Folder Action

If you have the daemon running:

```bash
# Stop and disable daemon
launchctl unload ~/Library/LaunchAgents/com.user.pdf-to-md.plist

# Optional: Remove daemon
rm ~/Library/LaunchAgents/com.user.pdf-to-md.plist
```

Then follow the Folder Action setup above.

## Which Approach Should You Use?

**Use Folder Action if:**
- You want easy GUI setup
- You're okay with visual Automator configuration
- You want notifications
- You only need to watch 1-2 specific folders

**Use Daemon (launchd) if:**
- You need to watch multiple directories
- You want pure command-line setup
- You're okay granting Full Disk Access
- You need more complex processing logic

**For most users: Folder Action is simpler and more Mac-like! 🍎**

