"""Configuration loader for the Seek scraper."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class Config:
    """Configuration management class."""

    def __init__(self, config_path: str = None):
        """Initialize configuration loader.

        Args:
            config_path: Path to config file. Defaults to config/config.yaml
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._replace_env_vars()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _replace_env_vars(self):
        """Replace environment variable placeholders in config."""
        def replace_in_dict(d: dict) -> dict:
            for key, value in d.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    d[key] = os.getenv(env_var, value)
                elif isinstance(value, dict):
                    replace_in_dict(value)
            return d

        self._config = replace_in_dict(self._config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'scraper.base_url')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_output_path(self, file_type: str = "json") -> Path:
        """Get output file path with current date.

        Args:
            file_type: Type of file (json or csv)

        Returns:
            Path to output file
        """
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / self.get("storage.output_dir", "data")
        output_dir.mkdir(parents=True, exist_ok=True)

        if file_type == "json":
            filename = self.get("storage.json_file", "jobs_{date}.json")
        else:
            filename = self.get("storage.csv_file", "jobs_{date}.csv")

        # Only replace {date} if it exists in the filename
        if "{date}" in filename:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = filename.replace("{date}", date_str)

        return output_dir / filename

    def get_log_path(self) -> Path:
        """Get log file path with current date.

        Returns:
            Path to log file
        """
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = self.get("logging.file", "scraper_{date}.log")
        filename = filename.replace("{date}", date_str)

        return log_dir / filename

    def get_seen_jobs_path(self) -> Path:
        """Get path to seen jobs file for deduplication.

        Returns:
            Path to seen jobs file
        """
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = self.get("deduplication.seen_jobs_file", "data/seen_jobs.json")
        return project_root / filename

    @property
    def scraper(self) -> Dict[str, Any]:
        """Get scraper configuration."""
        return self._config.get("scraper", {})

    @property
    def storage(self) -> Dict[str, Any]:
        """Get storage configuration."""
        return self._config.get("storage", {})

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config.get("logging", {})

    @property
    def deduplication(self) -> Dict[str, Any]:
        """Get deduplication configuration."""
        return self._config.get("deduplication", {})
