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
