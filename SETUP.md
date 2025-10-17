# PDF to Markdown - Complete Setup Guide

This guide walks you through setting up automatic PDF-to-Markdown conversion using macOS Folder Actions.

## Why Folder Actions?

- ✅ **Better permissions**: Runs in your user context
- ✅ **Native macOS integration**: Uses built-in Automator
- ✅ **Visual feedback**: Can show notifications when conversions complete
- ✅ **Easy to enable/disable**: Toggle in System Settings
- ✅ **No background daemon**: Lower resource usage

## Quick Setup

### Step 1: Run Setup Script

```bash
cd /Users/omri.a/Code/pdf-to-md
./setup.sh
```

This creates the necessary wrapper scripts and sets up the Python environment.

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

## Benefits of This Approach

✅ **No permission headaches**: Works with user-level permissions  
✅ **Visual setup**: GUI-based configuration via Automator  
✅ **Efficient**: Only runs when PDFs are added  
✅ **Flexible**: Can show notifications, easy to modify  
✅ **Native**: Uses macOS built-in automation tools

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

## Next Steps

After setup, try:
- Drop a PDF in your watched folder to test
- Check the log: `tail -f ~/Library/Logs/pdf-to-md.log`
- View converted files: `open ~/AI_Context/pdfs/`
- Add notifications to your workflow for visual feedback

Enjoy automatic PDF-to-Markdown conversion! 🎉

