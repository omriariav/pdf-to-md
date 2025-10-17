# PDF to Markdown Auto-Converter

Automatically convert PDF files to Markdown format when they appear in your Downloads folder. Perfect for feeding PDF content to AI agents and other tools that work better with text formats.

## Features

- 🔍 **Real-time monitoring**: Watches your Downloads folder (or any configured directory) for new PDF files
- ⚡ **Automatic conversion**: Converts PDFs to Markdown immediately after download
- 🎛️ **Configurable converters**: Choose between fast text extraction or high-quality OCR
- 🚀 **Runs in background**: Set-and-forget daemon that starts automatically at login
- 📝 **Smart handling**: Debouncing, duplicate detection, comprehensive error handling
- 🍎 **macOS native**: Uses launchd for proper system integration

## Quick Start

### Installation

1. Clone this repository:
   ```bash
   cd ~/Code
   git clone <repository-url> pdf-to-md
   cd pdf-to-md
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. The script will:
   - Create a Python virtual environment
   - Install dependencies
   - Create a configuration file (`config.yaml`)
   - Set up the daemon to start automatically

4. Review and customize `config.yaml` if needed (see Configuration section)

5. Done! The daemon is now running and will start automatically at login.

### Test It

1. Download or copy a PDF file to your Downloads folder
2. Wait 2-3 seconds
3. Check the output directory (default: `~/AI_Context/pdfs/`)
4. You should see a markdown file with the converted content!

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Directory to monitor for new PDF files
watch_directory: ~/Downloads

# Directory where converted markdown files will be saved
output_directory: ~/AI_Context/pdfs

# PDF conversion method
conversion_method: pdfplumber  # or marker-pdf

# Path to log file
log_file: ~/Library/Logs/pdf-to-md.log

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_level: INFO

# Seconds to wait after file creation before processing
debounce_seconds: 2
```

### Conversion Methods

#### pdfplumber (Default)
- ✅ Fast and lightweight
- ✅ Good for text-based PDFs
- ✅ Handles tables reasonably well
- ❌ Limited support for complex layouts
- ❌ No OCR for scanned documents

**Installation**: Included by default

#### marker-pdf
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

### Daemon Management

The daemon runs automatically in the background. Use these commands to control it:

```bash
# Stop the daemon
launchctl unload ~/Library/LaunchAgents/com.user.pdf-to-md.plist

# Start the daemon
launchctl load ~/Library/LaunchAgents/com.user.pdf-to-md.plist

# Check if daemon is running
launchctl list | grep pdf-to-md

# View live logs
tail -f ~/Library/Logs/pdf-to-md.log
```

### Manual Run (for testing)

Run the daemon in your terminal to see live output:

```bash
cd /Users/omri.a/Code/pdf-to-md
source venv/bin/activate
python pdf_to_md_daemon.py
```

Press `Ctrl+C` to stop.

### Uninstallation

```bash
# Stop and remove the daemon
launchctl unload ~/Library/LaunchAgents/com.user.pdf-to-md.plist
rm ~/Library/LaunchAgents/com.user.pdf-to-md.plist

# Remove the project directory
cd ~
rm -rf /Users/omri.a/Code/pdf-to-md
```

## How It Works

1. **File System Monitoring**: Uses the `watchdog` library to monitor the configured directory for file creation events
2. **Debouncing**: Waits 2 seconds (configurable) after a PDF appears to ensure the download is complete
3. **Conversion**: Processes the PDF using your chosen converter
4. **Markdown Generation**: Creates a well-formatted markdown file with:
   - Original filename as title
   - Page-by-page content
   - Tables (when detected)
   - Metadata
5. **Output**: Saves the markdown file to your configured directory
6. **Duplicate Handling**: If a file with the same name exists, appends a timestamp

## File Structure

```
pdf-to-md/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── config.yaml.example            # Example configuration
├── config.yaml                    # Your configuration (created by setup.sh)
├── pdf_to_md_daemon.py           # Main daemon script
├── converters.py                  # PDF conversion logic
├── config.py                      # Configuration management
├── setup.sh                       # Installation script
├── com.user.pdf-to-md.plist      # launchd service template
└── venv/                          # Python virtual environment (created by setup.sh)
```

## Troubleshooting

### Daemon not starting

Check the launchd logs:
```bash
cat /tmp/pdf-to-md.err.log
cat /tmp/pdf-to-md.out.log
```

Check if it's loaded:
```bash
launchctl list | grep pdf-to-md
```

### PDFs not being converted

1. Check the daemon is running:
   ```bash
   launchctl list | grep pdf-to-md
   ```

2. Check the logs:
   ```bash
   tail -f ~/Library/Logs/pdf-to-md.log
   ```

3. Verify your configuration:
   ```bash
   cat config.yaml
   ```

4. Test manually:
   ```bash
   cd /Users/omri.a/Code/pdf-to-md
   source venv/bin/activate
   python pdf_to_md_daemon.py
   ```
   Then drop a PDF in the watched folder and observe the output.

### Conversion fails

Some PDFs are encrypted, corrupted, or use formats that are difficult to parse. Check the log file for specific error messages:

```bash
tail -50 ~/Library/Logs/pdf-to-md.log
```

If using `pdfplumber` fails, try switching to `marker-pdf` for better OCR support.

### Permission errors

Ensure the daemon has permission to:
- Read from the watch directory
- Write to the output directory
- Write to the log file directory

Check directory permissions:
```bash
ls -la ~/Downloads
ls -la ~/AI_Context
```

## Advanced Usage

### Multiple Watch Directories

To monitor multiple directories, create separate configurations and launchd services:

1. Copy the project directory:
   ```bash
   cp -r pdf-to-md pdf-to-md-documents
   ```

2. Edit the new `config.yaml`:
   ```yaml
   watch_directory: ~/Documents
   output_directory: ~/AI_Context/documents
   ```

3. Run setup.sh in the new directory (edit the plist label to be unique)

### Custom Processing

Extend the `PDFConverter` base class in `converters.py` to implement custom conversion logic:

```python
class CustomConverter(PDFConverter):
    @property
    def name(self) -> str:
        return "custom"
    
    def convert(self, pdf_path: Path) -> str:
        # Your custom conversion logic
        return markdown_content
```

Then update the factory in `converters.py` and your config.yaml.

## Integration with AI Agents

The markdown files are saved to a configured directory (default: `~/AI_Context/pdfs/`) where they can be easily accessed by:

- Cursor AI (add the directory to your workspace)
- Custom AI agents with file system access
- RAG (Retrieval Augmented Generation) systems
- Document processing pipelines
- Search/indexing systems

## Requirements

- macOS 10.15 or later
- Python 3.8 or later
- ~50MB disk space (base installation)
- ~2GB additional for marker-pdf (optional)

## Dependencies

- `watchdog`: File system monitoring
- `pdfplumber`: Fast PDF text extraction
- `PyYAML`: Configuration file parsing
- `marker-pdf` (optional): High-quality PDF conversion with OCR

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Note**: This daemon processes files locally on your machine. No data is sent to external services unless you explicitly use a converter that does so (not included in the default setup).
