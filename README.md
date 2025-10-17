# PDF to Markdown Auto-Converter

Automatically convert PDF files to Markdown format using macOS Folder Actions. Drop a PDF in your watched folder, and it instantly converts to markdown - perfect for feeding PDF content to AI agents and other tools.

## Features

- 🔍 **Automatic monitoring**: Uses macOS Folder Actions to watch for new PDFs
- ⚡ **Instant conversion**: Converts PDFs to Markdown as soon as they appear
- 🎛️ **Configurable converters**: Choose between fast text extraction or high-quality OCR
- 📝 **Smart handling**: Duplicate detection, comprehensive error handling
- 🍎 **Native macOS**: Uses Automator Folder Actions - no daemon, no permission issues!
- 🔔 **Optional notifications**: Get visual feedback when conversions complete

## Quick Start

### 1. Run Setup Script

```bash
cd /Users/omri.a/Code/pdf-to-md
./setup.sh
```

This will:
- Create a Python virtual environment
- Install dependencies
- Create configuration files
- Generate wrapper scripts for Automator

### 2. Set Up Folder Action in Automator

1. Open **Automator** app (in `/Applications`)

2. Create **"New Document"** → **"Folder Action"**

3. Choose your folder (Downloads, Desktop, or any folder you want to monitor)

4. Search for **"Run Shell Script"** in the left sidebar and drag it to the workflow

5. Configure:
   - **Shell**: `/bin/bash`
   - **Pass input**: `as arguments`
   - **Script**: 
   ```bash
   /Users/omri.a/Code/pdf-to-md/convert_pdf_folder_action.sh "$@"
   ```

6. **Save** as "PDF to Markdown" 
   - Location: `~/Library/Workflows/Applications/Folder Actions/`

7. Enable in **System Settings** → **Extensions** → **Finder** → **Folder Actions**

### 3. Test It!

Drop a PDF into your watched folder - it should automatically convert!

Check the output: `~/AI_Context/pdfs/`

View the log:
```bash
tail -f ~/Library/Logs/pdf-to-md.log
```

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Directory where converted markdown files will be saved
output_directory: ~/AI_Context/pdfs

# PDF conversion method
conversion_method: pdfplumber  # or marker-pdf

# Path to log file
log_file: ~/Library/Logs/pdf-to-md.log

# Logging level
log_level: INFO
```

### Conversion Methods

#### pdfplumber (Default)
- ✅ Fast and lightweight
- ✅ Good for text-based PDFs
- ✅ Handles tables reasonably well
- ❌ Limited support for complex layouts
- ❌ No OCR for scanned documents

**Installation**: Included by default

#### marker-pdf (Optional)
- ✅ High-quality OCR
- ✅ Better layout preservation
- ✅ Handles complex documents and images
- ❌ Slower conversion
- ❌ Requires additional dependencies (~2GB)

**Installation**:
```bash
source venv/bin/activate
pip install marker-pdf torch transformers
```

Then update `config.yaml`:
```yaml
conversion_method: marker-pdf
```

## Usage

### Managing Folder Actions

#### Enable/Disable
**System Settings** → **Extensions** → **Finder** → Toggle **Folder Actions**

#### View Active Folder Actions
```bash
open -a "Folder Actions Setup"
```

#### Add to More Folders
- Right-click any folder
- **Services** → **Folder Actions Setup**
- Attach the "PDF to Markdown" workflow

### Manual Conversion

Test a single PDF without Folder Actions:

```bash
source venv/bin/activate
./test_conversion.py ~/path/to/file.pdf
```

### Logs

```bash
# View live log
tail -f ~/Library/Logs/pdf-to-md.log

# View recent entries
tail -50 ~/Library/Logs/pdf-to-md.log
```

## How It Works

1. **Folder Action**: macOS watches your chosen folder for new files
2. **Trigger**: When a PDF is added, Automator runs the wrapper script
3. **Conversion**: Script uses pdfplumber (or marker-pdf) to extract content
4. **Markdown Generation**: Creates formatted markdown with:
   - Original filename as title
   - Page-by-page content
   - Tables (when detected)
   - Metadata
5. **Output**: Saves to your configured directory
6. **Duplicate Handling**: Appends timestamp if file already exists

## File Structure

```
pdf-to-md/
├── README.md                           # This file
├── SETUP.md                            # Detailed setup guide
├── requirements.txt                    # Python dependencies
├── config.yaml.example                 # Example configuration
├── config.yaml                         # Your configuration
├── converters.py                       # PDF conversion logic
├── config.py                           # Configuration management
├── test_conversion.py                  # Manual test utility
├── setup.sh                            # Installation script
├── convert_pdf_folder_action.sh        # Wrapper for Automator (generated)
├── convert_single_pdf.py               # Single file converter (generated)
└── venv/                               # Python virtual environment
```

## Troubleshooting

### Folder Action not triggering

1. **Check if enabled**:
   - **System Settings** → **Extensions** → **Finder** → **Folder Actions** ✓

2. **Verify workflow is attached**:
   - Right-click your folder → **Services** → **Folder Action Setup**
   - Your workflow should be listed

3. **Check Automator permissions**:
   - **System Settings** → **Privacy & Security** → **Automation**
   - Ensure Automator can control Finder

### Conversion fails

Check the log for specific errors:
```bash
tail -50 ~/Library/Logs/pdf-to-md.log
```

Some PDFs are encrypted, corrupted, or use difficult formats. Try:
- Different PDF
- Switch to `marker-pdf` in config.yaml for better OCR

### Permission errors

Folder Actions run in your user context, so they have the same permissions as you. If you can manually open the PDF, the script should be able to process it.

If issues persist:
- Try watching a different folder (Desktop instead of Downloads)
- Ensure Automator has necessary permissions in System Settings

## Advanced Usage

### Add Visual Notifications

Edit your Automator workflow:
1. Add **"Display Notification"** action after the shell script
2. Message: "PDF converted successfully"

Or modify the wrapper script to include:
```bash
osascript -e 'display notification "PDF converted to Markdown" with title "PDF Converter"'
```

### Watch Multiple Folders

Create separate Folder Action workflows for each folder you want to monitor. They can all use the same conversion script.

### Custom Processing

Extend the `PDFConverter` base class in `converters.py`:

```python
class CustomConverter(PDFConverter):
    @property
    def name(self) -> str:
        return "custom"
    
    def convert(self, pdf_path: Path) -> str:
        # Your custom conversion logic
        return markdown_content
```

Update the factory in `converters.py` and your `config.yaml`.

## Integration with AI Agents

Converted markdown files are saved to `~/AI_Context/pdfs/` (configurable) where they can be easily accessed by:

- **Cursor AI**: Add the directory to your workspace
- **Custom AI agents**: With file system access
- **RAG systems**: Retrieval Augmented Generation
- **Document pipelines**: Search, indexing, processing
- **Note-taking apps**: Obsidian, Notion, etc.

## Why Folder Actions?

Compared to background daemons, Folder Actions offer:

✅ **Better permissions**: Runs in your user context  
✅ **Native macOS**: Built-in Automator integration  
✅ **Easy setup**: Visual GUI configuration  
✅ **No daemon management**: No launchd complexity  
✅ **Visual feedback**: Optional notifications  
✅ **Lower resource usage**: Only runs when triggered  

## Requirements

- macOS 10.15 or later
- Python 3.8 or later
- ~50MB disk space (base installation)
- ~2GB additional for marker-pdf (optional)

## Dependencies

- `watchdog`: File system events (used by converter)
- `pdfplumber`: Fast PDF text extraction (default)
- `PyYAML`: Configuration file parsing
- `marker-pdf` (optional): High-quality PDF conversion with OCR

## Support

For the complete setup guide with screenshots and troubleshooting, see [SETUP.md](SETUP.md).

## License

MIT License - feel free to use and modify as needed.

---

**Note**: This tool processes files locally on your machine. No data is sent to external services.
