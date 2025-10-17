#!/bin/bash
#
# Setup macOS Folder Action for PDF to Markdown conversion
#
# This creates an Automator workflow that triggers when PDFs are added to a folder.
# Folder Actions avoid many permission issues because they run with user context.
#

set -e

echo "===================================="
echo "PDF to Markdown - Folder Action Setup"
echo "===================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Create the wrapper script that Automator will call
cat > "$SCRIPT_DIR/convert_pdf_folder_action.sh" << 'WRAPPER_EOF'
#!/bin/bash
# Wrapper script called by Folder Action
# Receives file paths as arguments

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Log file
LOG_FILE="$HOME/Library/Logs/pdf-to-md.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Process each file passed by Folder Action
for file in "$@"; do
    # Only process PDF files
    if [[ "$file" == *.pdf ]] || [[ "$file" == *.PDF ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing: $file" >> "$LOG_FILE"
        
        # Run the conversion using our existing converter
        python3 "$SCRIPT_DIR/convert_single_pdf.py" "$file" >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Successfully converted: $file" >> "$LOG_FILE"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Failed to convert: $file" >> "$LOG_FILE"
        fi
    fi
done
WRAPPER_EOF

chmod +x "$SCRIPT_DIR/convert_pdf_folder_action.sh"
echo "✓ Created wrapper script: convert_pdf_folder_action.sh"

# Create the single file converter script
cat > "$SCRIPT_DIR/convert_single_pdf.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
Single PDF converter for Folder Actions.
Called by convert_pdf_folder_action.sh when a PDF is added to watched folder.
"""

import sys
from pathlib import Path
from datetime import datetime

from config import load_config
from converters import get_converter


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_single_pdf.py <path-to-pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1]).resolve()
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    if pdf_path.suffix.lower() != ".pdf":
        print(f"Skipping non-PDF file: {pdf_path}")
        sys.exit(0)

    # Load config
    config = load_config()
    
    # Get converter
    converter = get_converter(config.conversion_method)
    
    # Convert
    print(f"Converting {pdf_path.name} using {converter.name}...")
    markdown = converter.convert(pdf_path)
    
    # Create output directory
    config.output_directory.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    output_name = f"{pdf_path.stem}.md"
    output_path = config.output_directory / output_name
    
    # If file exists, append timestamp
    if output_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{pdf_path.stem}_{timestamp}.md"
        output_path = config.output_directory / output_name
    
    # Write markdown
    output_path.write_text(markdown, encoding='utf-8')
    
    print(f"✓ Saved to: {output_path}")


if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x "$SCRIPT_DIR/convert_single_pdf.py"
echo "✓ Created converter script: convert_single_pdf.py"

# Create config if needed
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "✓ Created config.yaml"
fi

echo ""
echo "===================================="
echo "Folder Action Files Ready!"
echo "===================================="
echo ""
echo "Now set up the Folder Action in macOS:"
echo ""
echo "1. Right-click on your Downloads folder (or any folder)"
echo "2. Choose 'Quick Actions' or 'Services' → 'Folder Actions Setup'"
echo "3. If that doesn't work, open 'Automator' app:"
echo "   - Create new 'Folder Action'"
echo "   - Choose folder: ~/Downloads (or your preferred folder)"
echo "   - Add action: 'Run Shell Script'"
echo "   - Set shell to: /bin/bash"
echo "   - Set 'Pass input': as arguments"
echo "   - Paste this script:"
echo ""
echo "   $SCRIPT_DIR/convert_pdf_folder_action.sh \"\$@\""
echo ""
echo "4. Save the workflow"
echo "5. Enable Folder Actions in System Settings → Extensions → Folder Actions"
echo ""
echo "OR use the quick command:"
echo "  open -a 'Folder Actions Setup'"
echo ""
echo "Test by dropping a PDF into the watched folder!"
echo ""

