#!/usr/bin/env python3
"""
PDF to Markdown Daemon

Monitors a directory for new PDF files and automatically converts them
to Markdown format, saving the results to a configured output directory.
"""

import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Timer
from typing import Dict

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from config import load_config, Config
from converters import get_converter, PDFConverter

# Global flag for graceful shutdown
shutdown_requested = False


def setup_logging(config: Config):
    """
    Configure logging to both file and console.

    Args:
        config: Configuration object with log settings
    """
    # Create log directory if it doesn't exist
    log_file = config.log_file
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.log_level))

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, config.log_level))
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (less verbose)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info("Logging initialized")


class PDFFileHandler(FileSystemEventHandler):
    """
    Handler for file system events.

    Monitors for new PDF files and triggers conversion after debouncing.
    """

    def __init__(self, config: Config, converter: PDFConverter):
        super().__init__()
        self.config = config
        self.converter = converter
        self.logger = logging.getLogger(__name__)
        
        # Track pending conversions for debouncing
        self._pending_conversions: Dict[str, Timer] = {}

    def on_created(self, event: FileSystemEvent):
        """
        Called when a file or directory is created.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process PDF files
        if file_path.suffix.lower() != ".pdf":
            return

        self.logger.info(f"Detected new PDF: {file_path.name}")

        # Cancel any existing pending conversion for this file
        if event.src_path in self._pending_conversions:
            self._pending_conversions[event.src_path].cancel()

        # Schedule conversion after debounce period
        timer = Timer(
            self.config.debounce_seconds,
            self._process_pdf,
            args=(file_path,)
        )
        self._pending_conversions[event.src_path] = timer
        timer.start()

        self.logger.debug(
            f"Scheduled conversion for {file_path.name} "
            f"in {self.config.debounce_seconds} seconds"
        )

    def _process_pdf(self, pdf_path: Path):
        """
        Process a PDF file: convert to markdown and save.

        Args:
            pdf_path: Path to the PDF file to process
        """
        try:
            # Remove from pending conversions
            if str(pdf_path) in self._pending_conversions:
                del self._pending_conversions[str(pdf_path)]

            # Check if file still exists (might have been deleted)
            if not pdf_path.exists():
                self.logger.warning(f"File no longer exists: {pdf_path.name}")
                return

            self.logger.info(f"Processing {pdf_path.name}...")

            # Convert PDF to Markdown
            markdown_content = self.converter.convert(pdf_path)

            # Create output directory if it doesn't exist
            self.config.output_directory.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            output_filename = self._generate_output_filename(pdf_path)
            output_path = self.config.output_directory / output_filename

            # Write markdown file
            output_path.write_text(markdown_content, encoding="utf-8")

            self.logger.info(
                f"✓ Successfully converted {pdf_path.name} -> {output_filename}"
            )

        except Exception as e:
            self.logger.error(f"Failed to process {pdf_path.name}: {e}", exc_info=True)

    def _generate_output_filename(self, pdf_path: Path) -> str:
        """
        Generate output filename for the markdown file.

        If a file with the same name already exists, append a timestamp.

        Args:
            pdf_path: Original PDF path

        Returns:
            Output filename (just the name, not full path)
        """
        base_name = pdf_path.stem
        output_name = f"{base_name}.md"
        output_path = self.config.output_directory / output_name

        # If file already exists, append timestamp
        if output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{base_name}_{timestamp}.md"
            self.logger.debug(
                f"File {output_name} exists, using timestamp: {output_name}"
            )

        return output_name

    def cleanup(self):
        """Cancel all pending conversions."""
        for timer in self._pending_conversions.values():
            timer.cancel()
        self._pending_conversions.clear()


def signal_handler(signum, frame):
    """
    Handle shutdown signals (SIGINT, SIGTERM).

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global shutdown_requested
    logger = logging.getLogger(__name__)
    
    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM",
    }
    signal_name = signal_names.get(signum, f"signal {signum}")
    
    logger.info(f"Received {signal_name}, shutting down gracefully...")
    shutdown_requested = True


def main():
    """Main entry point for the daemon."""
    global shutdown_requested
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("PDF to Markdown Daemon Starting")
    logger.info("=" * 60)
    logger.info(f"Watch directory: {config.watch_directory}")
    logger.info(f"Output directory: {config.output_directory}")
    logger.info(f"Conversion method: {config.conversion_method}")
    logger.info(f"Log file: {config.log_file}")
    logger.info("=" * 60)

    # Validate watch directory exists
    if not config.watch_directory.exists():
        logger.error(f"Watch directory does not exist: {config.watch_directory}")
        sys.exit(1)

    if not config.watch_directory.is_dir():
        logger.error(f"Watch directory is not a directory: {config.watch_directory}")
        sys.exit(1)

    # Initialize converter
    try:
        converter = get_converter(config.conversion_method)
        logger.info(f"Initialized {converter.name} converter")
    except Exception as e:
        logger.error(f"Failed to initialize converter: {e}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    try:
        config.output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {config.output_directory}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        sys.exit(1)

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create event handler and observer
    event_handler = PDFFileHandler(config, converter)
    observer = Observer()
    observer.schedule(event_handler, str(config.watch_directory), recursive=False)

    # Start monitoring
    observer.start()
    logger.info(f"Monitoring {config.watch_directory} for new PDF files...")
    logger.info("Press Ctrl+C to stop")

    try:
        # Keep the daemon running
        while not shutdown_requested:
            time.sleep(1)
    except KeyboardInterrupt:
        # This should be caught by signal handler, but just in case
        logger.info("Interrupted by user")
    finally:
        # Cleanup
        logger.info("Stopping file monitoring...")
        observer.stop()
        observer.join(timeout=5)
        
        logger.info("Cancelling pending conversions...")
        event_handler.cleanup()
        
        logger.info("Daemon stopped")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()

