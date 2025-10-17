#!/bin/bash
#
# Setup script for PDF to Markdown Daemon
#
# This script:
# 1. Creates a Python virtual environment
# 2. Installs dependencies
# 3. Creates config.yaml if it doesn't exist
# 4. Sets up launchd service for auto-start
#

set -e  # Exit on error

echo "===================================="
echo "PDF to Markdown Daemon Setup"
echo "===================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Create virtual environment
echo "Step 1: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Step 3: Create config.yaml
echo ""
echo "Step 3: Creating configuration file..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "✓ Created config.yaml from example"
    echo ""
    echo "IMPORTANT: Please review and edit config.yaml to customize:"
    echo "  - watch_directory (default: ~/Downloads)"
    echo "  - output_directory (default: ~/AI_Context/pdfs)"
    echo "  - conversion_method (default: pdfplumber)"
    echo ""
    read -p "Press Enter to continue after reviewing config.yaml..."
else
    echo "✓ config.yaml already exists"
fi

# Step 4: Test file access permissions
echo ""
echo "Step 4: Testing file access permissions..."
echo ""
echo "macOS requires explicit permission to access the Downloads folder."
echo "We'll now test if the daemon can access your configured watch directory."
echo ""

# Read watch directory from config
WATCH_DIR=$(grep "^watch_directory:" config.yaml | cut -d: -f2 | xargs)
WATCH_DIR_EXPANDED=$(eval echo "$WATCH_DIR")

# Create a test PDF if none exists
TEST_PDF="$WATCH_DIR_EXPANDED/.pdf_daemon_test.pdf"
echo "Creating test file: $TEST_PDF"
echo "%PDF-1.4 test" > "$TEST_PDF" 2>/dev/null || true

echo ""
echo "Running daemon for 10 seconds to trigger permission prompts..."
echo "If macOS shows a permission dialog, please click 'Allow' or 'OK'."
echo ""
sleep 2

# Run daemon briefly to trigger permissions (with timeout using background process)
venv/bin/python3 pdf_to_md_daemon.py 2>&1 &
DAEMON_PID=$!
sleep 8
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true

# Clean up test file
rm -f "$TEST_PDF" 2>/dev/null || true

echo ""
echo "✓ Permission test complete"
echo ""
echo "If you saw a permission error above, please:"
echo "  1. Open System Settings → Privacy & Security → Files and Folders"
echo "  2. Find 'Python' or 'Terminal' in the list"
echo "  3. Enable access to Downloads folder"
echo "  4. Then rerun this setup script"
echo ""
read -p "Press Enter to continue with launchd setup..."

# Step 5: Setup launchd service
echo ""
echo "Step 5: Setting up launchd service..."

# Get paths
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
SCRIPT_PATH="$SCRIPT_DIR/pdf_to_md_daemon.py"
PLIST_SOURCE="$SCRIPT_DIR/com.user.pdf-to-md.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.user.pdf-to-md.plist"
USERNAME=$(whoami)

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Replace placeholders in plist file
sed -e "s|REPLACE_PYTHON_PATH|$PYTHON_PATH|g" \
    -e "s|REPLACE_SCRIPT_PATH|$SCRIPT_PATH|g" \
    -e "s|REPLACE_WORKING_DIR|$SCRIPT_DIR|g" \
    -e "s|REPLACE_USERNAME|$USERNAME|g" \
    "$PLIST_SOURCE" > "$PLIST_DEST"

echo "✓ Created launchd plist: $PLIST_DEST"

# Unload existing service if it's running
if launchctl list | grep -q "com.user.pdf-to-md"; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Load the service
echo "Loading launchd service..."
launchctl load "$PLIST_DEST"
echo "✓ Service loaded and started"

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "The PDF to Markdown daemon is now running and will:"
echo "  - Monitor: $(grep watch_directory config.yaml | cut -d: -f2 | xargs)"
echo "  - Output to: $(grep output_directory config.yaml | cut -d: -f2 | xargs)"
echo "  - Start automatically at login"
echo ""
echo "Useful commands:"
echo "  - Stop daemon:    launchctl unload ~/Library/LaunchAgents/com.user.pdf-to-md.plist"
echo "  - Start daemon:   launchctl load ~/Library/LaunchAgents/com.user.pdf-to-md.plist"
echo "  - Check status:   launchctl list | grep pdf-to-md"
echo "  - View logs:      tail -f ~/Library/Logs/pdf-to-md.log"
echo "  - Manual run:     ./venv/bin/python3 pdf_to_md_daemon.py"
echo ""
echo "Try it: Drop a PDF file into your Downloads folder!"
echo ""

