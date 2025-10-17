"""
PDF to Markdown converters.

Provides an abstract base class and concrete implementations for converting
PDF files to Markdown format using different extraction methods.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PDFConverter(ABC):
    """Abstract base class for PDF to Markdown converters."""

    @abstractmethod
    def convert(self, pdf_path: Path) -> str:
        """
        Convert a PDF file to Markdown format.

        Args:
            pdf_path: Path to the PDF file to convert

        Returns:
            Markdown string representation of the PDF content

        Raises:
            Exception: If conversion fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this converter."""
        pass


class PdfPlumberConverter(PDFConverter):
    """
    Fast text-based PDF converter using pdfplumber.
    
    Good for text-based PDFs. Fast and lightweight, but doesn't handle
    complex layouts, images, or scanned documents well.
    """

    def __init__(self):
        try:
            import pdfplumber
            self._pdfplumber = pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required for this converter. "
                "Install it with: pip install pdfplumber"
            )

    @property
    def name(self) -> str:
        return "pdfplumber"

    def convert(self, pdf_path: Path) -> str:
        """
        Convert PDF to Markdown using pdfplumber.

        Extracts text page-by-page and formats with page separators.
        Attempts to preserve basic table structure.
        """
        logger.info(f"Converting {pdf_path.name} using pdfplumber...")

        markdown_content = []
        markdown_content.append(f"# {pdf_path.stem}\n")
        markdown_content.append(f"*Converted from: {pdf_path.name}*\n")
        markdown_content.append("---\n\n")

        try:
            with self._pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.debug(f"Processing {total_pages} pages...")

                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text
                    text = page.extract_text()
                    
                    if text:
                        markdown_content.append(f"## Page {page_num}\n\n")
                        markdown_content.append(text)
                        markdown_content.append("\n\n")
                    
                    # Try to extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, start=1):
                            markdown_content.append(f"### Table {table_num} (Page {page_num})\n\n")
                            markdown_content.append(self._table_to_markdown(table))
                            markdown_content.append("\n\n")

                logger.info(f"Successfully converted {total_pages} pages")

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path.name}: {e}")
            raise

        return "".join(markdown_content)

    def _table_to_markdown(self, table: list) -> str:
        """Convert a table array to Markdown table format."""
        if not table or not table[0]:
            return ""

        lines = []
        
        # Header row
        header = table[0]
        lines.append("| " + " | ".join(str(cell or "") for cell in header) + " |")
        
        # Separator
        lines.append("| " + " | ".join("---" for _ in header) + " |")
        
        # Data rows
        for row in table[1:]:
            if row:  # Skip empty rows
                lines.append("| " + " | ".join(str(cell or "") for cell in row) + " |")
        
        return "\n".join(lines)


class MarkerPdfConverter(PDFConverter):
    """
    High-quality PDF converter using marker-pdf.
    
    Better for complex layouts, images, and scanned documents.
    Slower but produces higher quality markdown with better structure preservation.
    """

    def __init__(self):
        try:
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models
            self._convert_single_pdf = convert_single_pdf
            self._load_all_models = load_all_models
            self._models = None
        except ImportError:
            raise ImportError(
                "marker-pdf is required for this converter. "
                "Install it with: pip install marker-pdf"
            )

    @property
    def name(self) -> str:
        return "marker-pdf"

    def convert(self, pdf_path: Path) -> str:
        """
        Convert PDF to Markdown using marker-pdf.

        Uses ML models for better layout detection and text extraction.
        Loads models on first use and caches them.
        """
        logger.info(f"Converting {pdf_path.name} using marker-pdf...")

        try:
            # Load models on first use
            if self._models is None:
                logger.debug("Loading marker-pdf models (first time only)...")
                self._models = self._load_all_models()

            # Convert the PDF
            markdown_content, metadata = self._convert_single_pdf(
                str(pdf_path),
                self._models
            )

            logger.info(f"Successfully converted {pdf_path.name}")
            logger.debug(f"Metadata: {metadata}")

            return markdown_content

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path.name}: {e}")
            raise


def get_converter(method: str) -> PDFConverter:
    """
    Factory function to get the appropriate converter.

    Args:
        method: Converter method name ('pdfplumber' or 'marker-pdf')

    Returns:
        An instance of the appropriate converter

    Raises:
        ValueError: If the method is not supported
        ImportError: If required dependencies are not installed
    """
    converters = {
        "pdfplumber": PdfPlumberConverter,
        "marker-pdf": MarkerPdfConverter,
    }

    if method not in converters:
        raise ValueError(
            f"Unknown conversion method: {method}. "
            f"Supported methods: {', '.join(converters.keys())}"
        )

    try:
        return converters[method]()
    except ImportError as e:
        logger.error(f"Failed to initialize {method} converter: {e}")
        raise

