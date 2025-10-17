# Alternative Approaches to Avoid Full Disk Access

The Downloads folder on macOS is heavily protected and requires Full Disk Access for programmatic access. Here are less intrusive alternatives:

## Option 1: Use a Different Watch Directory (Easiest)

Instead of monitoring `~/Downloads`, watch a less protected folder:

```yaml
# config.yaml
watch_directory: ~/Documents/PDFs-to-Convert
# OR
watch_directory: ~/Desktop
```

**Pros**: No special permissions needed
**Cons**: Have to manually move PDFs from Downloads

## Option 2: Manual Trigger Script

Instead of a daemon, use a script you run manually when needed:

```bash
# Convert all PDFs in Downloads
./convert_all.sh

# Or use the test script on specific files
./test_conversion.py ~/Downloads/file.pdf
```

**Pros**: No permissions, full control
**Cons**: Not automatic

## Option 3: Browser Extension or Hazel

Use a tool that has already been granted permissions:

- **Hazel**: macOS automation app that can watch Downloads and run scripts
- **Keyboard Maestro**: Trigger conversions via hotkey
- **Browser Extension**: Some extensions can save directly to custom locations

**Pros**: Works with Downloads folder
**Cons**: Requires third-party tools

## Option 4: Dropbox/iCloud Folder

Watch a synced folder instead:

```yaml
watch_directory: ~/Dropbox/PDFs
# or
watch_directory: ~/Library/Mobile Documents/com~apple~CloudDocs/PDFs
```

**Pros**: Also syncs to other devices
**Cons**: Requires cloud storage setup

## Option 5: Grant Full Disk Access (Most Intrusive)

If you decide the convenience is worth it:

1. System Settings → Privacy & Security → Full Disk Access
2. Add `/Library/Developer/CommandLineTools/usr/bin/python3`
3. Restart daemon

**Pros**: Works exactly as designed
**Cons**: Python gets access to all files on your system

## Recommended: Option 1 (Different Directory)

For most use cases, watching `~/Documents/PDFs` or `~/Desktop` is the best balance:
- No special permissions
- Easy to drag files there
- Still automatic conversion
- Clear separation of "to be processed" files

---

## Current Status

- Daemon is **stopped** (to avoid permission errors)
- To use later:
  1. Update `config.yaml` with your chosen watch directory
  2. Start daemon: `launchctl load ~/Library/LaunchAgents/com.user.pdf-to-md.plist`

