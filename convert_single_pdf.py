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
