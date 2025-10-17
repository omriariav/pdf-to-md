#!/usr/bin/env python3
"""
Test script for PDF to Markdown conversion.

Use this to test your converter without running the full daemon.
"""

import sys
from pathlib import Path

from config import load_config
from converters import get_converter


def main():
    """Test PDF conversion with a specific file."""
    if len(sys.argv) < 2:
        print("Usage: python test_conversion.py <path-to-pdf>")
        print()
        print("Example:")
        print("  python test_conversion.py ~/Downloads/sample.pdf")
        sys.exit(1)

    pdf_path = Path(sys.argv[1]).expanduser().resolve()

    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    if pdf_path.suffix.lower() != ".pdf":
        print(f"Error: Not a PDF file: {pdf_path}")
        sys.exit(1)

    print(f"Testing PDF conversion...")
    print(f"Input file: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print()

    # Load config
    try:
        config = load_config()
        print(f"Using converter: {config.conversion_method}")
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
        print("Using default converter: pdfplumber")
        from converters import PdfPlumberConverter
        converter = PdfPlumberConverter()
    else:
        converter = get_converter(config.conversion_method)

    print()
    print("Converting...")
    print("-" * 60)

    try:
        markdown = converter.convert(pdf_path)
        
        print()
        print("=" * 60)
        print("CONVERSION SUCCESSFUL!")
        print("=" * 60)
        print()
        print(f"Generated {len(markdown)} characters of markdown")
        print()
        
        # Show preview
        lines = markdown.split("\n")
        preview_lines = lines[:50]
        print("Preview (first 50 lines):")
        print("-" * 60)
        for line in preview_lines:
            print(line)
        
        if len(lines) > 50:
            print()
            print(f"... ({len(lines) - 50} more lines)")
        
        print()
        print("-" * 60)
        
        # Offer to save
        output_path = pdf_path.parent / f"{pdf_path.stem}.md"
        response = input(f"\nSave to {output_path}? [y/N]: ").strip().lower()
        
        if response == 'y':
            output_path.write_text(markdown, encoding='utf-8')
            print(f"✓ Saved to: {output_path}")
        else:
            print("Not saved.")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("CONVERSION FAILED!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

