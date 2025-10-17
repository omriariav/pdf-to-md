"""
Configuration management for PDF to Markdown daemon.

Loads configuration from YAML file with sensible defaults.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULTS = {
    "watch_directory": "~/Downloads",
    "output_directory": "~/AI_Context/pdfs",
    "conversion_method": "pdfplumber",
    "log_file": "~/Library/Logs/pdf-to-md.log",
    "log_level": "INFO",
    "debounce_seconds": 2,
}


class Config:
    """Configuration container with validation and path expansion."""

    def __init__(self, config_dict: Dict[str, Any]):
        self._config = {**DEFAULTS, **config_dict}
        self._validate()
        self._expand_paths()

    def _validate(self):
        """Validate configuration values."""
        # Validate conversion method
        valid_methods = ["pdfplumber", "marker-pdf"]
        method = self._config["conversion_method"]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid conversion_method: {method}. "
                f"Must be one of: {', '.join(valid_methods)}"
            )

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level = self._config["log_level"].upper()
        if level not in valid_levels:
            raise ValueError(
                f"Invalid log_level: {level}. "
                f"Must be one of: {', '.join(valid_levels)}"
            )
        self._config["log_level"] = level

        # Validate debounce_seconds
        debounce = self._config["debounce_seconds"]
        if not isinstance(debounce, (int, float)) or debounce < 0:
            raise ValueError(
                f"Invalid debounce_seconds: {debounce}. Must be a positive number."
            )

    def _expand_paths(self):
        """Expand ~ and environment variables in path configurations."""
        path_keys = ["watch_directory", "output_directory", "log_file"]
        for key in path_keys:
            if key in self._config:
                self._config[key] = Path(self._config[key]).expanduser().resolve()

    @property
    def watch_directory(self) -> Path:
        """Directory to monitor for new PDF files."""
        return self._config["watch_directory"]

    @property
    def output_directory(self) -> Path:
        """Directory to save converted markdown files."""
        return self._config["output_directory"]

    @property
    def conversion_method(self) -> str:
        """PDF conversion method to use."""
        return self._config["conversion_method"]

    @property
    def log_file(self) -> Path:
        """Path to log file."""
        return self._config["log_file"]

    @property
    def log_level(self) -> str:
        """Logging level."""
        return self._config["log_level"]

    @property
    def debounce_seconds(self) -> float:
        """Seconds to wait before processing a new file (debouncing)."""
        return self._config["debounce_seconds"]

    def __repr__(self) -> str:
        return f"Config({self._config})"


def load_config(config_path: Path = None) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config.yaml file. If None, looks for config.yaml
                    in the current directory.

    Returns:
        Config object with loaded and validated configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If configuration values are invalid
    """
    if config_path is None:
        # Look for config.yaml in same directory as this script
        config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        logger.warning(
            f"Config file not found at {config_path}. Using defaults: {DEFAULTS}"
        )
        return Config({})

    logger.info(f"Loading configuration from {config_path}")

    try:
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse config file: {e}")
        raise

    return Config(config_dict)


def create_example_config(output_path: Path = None):
    """
    Create an example configuration file.

    Args:
        output_path: Where to write the example config. Defaults to config.yaml.example
    """
    if output_path is None:
        output_path = Path(__file__).parent / "config.yaml.example"

    example_content = """# PDF to Markdown Daemon Configuration

# Directory to monitor for new PDF files
# Use ~ for home directory
watch_directory: ~/Downloads

# Directory where converted markdown files will be saved
# This directory will be created if it doesn't exist
output_directory: ~/AI_Context/pdfs

# PDF conversion method to use
# Options:
#   - pdfplumber: Fast, text-based extraction (default)
#   - marker-pdf: High-quality OCR and layout preservation (requires additional dependencies)
conversion_method: pdfplumber

# Path to log file
log_file: ~/Library/Logs/pdf-to-md.log

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_level: INFO

# Seconds to wait after file creation before processing (debouncing)
# Helps ensure the file is fully downloaded before attempting conversion
debounce_seconds: 2
"""

    with open(output_path, "w") as f:
        f.write(example_content)

    logger.info(f"Created example configuration at {output_path}")


if __name__ == "__main__":
    # When run directly, create example config
    create_example_config()
    print("Created config.yaml.example")

