"""JSON file storage backend."""

import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

from ..models import Job
from .base_storage import BaseStorage


class JSONStorage(BaseStorage):
    """JSON file-based storage."""

    def __init__(self, output_path: Path, seen_jobs_path: Path, retention_days: int = 30):
        """Initialize JSON storage.

        Args:
            output_path: Path to output JSON file
            seen_jobs_path: Path to seen jobs tracking file
            retention_days: Number of days to track seen jobs
        """
        self.output_path = output_path
        self.seen_jobs_path = seen_jobs_path
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.seen_jobs_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, jobs: List[Job]) -> None:
        """Save jobs to JSON file (merges with existing jobs).

        Args:
            jobs: List of NEW Job objects to add
        """
        # Load existing jobs
        existing_jobs = self.load()

        # Merge new jobs with existing jobs
        all_jobs = existing_jobs + jobs

        # Convert to dict for saving
        jobs_data = [job.to_dict() for job in all_jobs]

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved {len(jobs)} new jobs (total: {len(all_jobs)} jobs in database)")

        # Update seen jobs
        self._update_seen_jobs(jobs)

    def load(self) -> List[Job]:
        """Load jobs from JSON file.

        Returns:
            List of Job objects
        """
        if not self.output_path.exists():
            return []

        with open(self.output_path, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)

        return [Job.from_dict(data) for data in jobs_data]

    def exists(self, job: Job) -> bool:
        """Check if job already exists in seen jobs.

        Args:
            job: Job to check

        Returns:
            True if job was seen before
        """
        seen_jobs = self._load_seen_jobs()
        return job.job_url in seen_jobs

    def _load_seen_jobs(self) -> dict:
        """Load seen jobs tracking data.

        Returns:
            Dictionary of job_url -> timestamp
        """
        if not self.seen_jobs_path.exists():
            return {}

        with open(self.seen_jobs_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _update_seen_jobs(self, jobs: List[Job]) -> None:
        """Update seen jobs tracking file.

        Args:
            jobs: List of newly scraped jobs
        """
        seen_jobs = self._load_seen_jobs()

        # Add new jobs
        current_time = datetime.now().isoformat()
        for job in jobs:
            seen_jobs[job.job_url] = current_time

        # Clean up old entries
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        seen_jobs = {
            url: timestamp
            for url, timestamp in seen_jobs.items()
            if datetime.fromisoformat(timestamp) > cutoff_date
        }

        # Save updated tracking
        with open(self.seen_jobs_path, "w", encoding="utf-8") as f:
            json.dump(seen_jobs, f, indent=2)

        self.logger.debug(f"Updated seen jobs. Total tracked: {len(seen_jobs)}")

    def cleanup_old_jobs(self) -> int:
        """Remove jobs older than retention_days from the database.

        Returns:
            Number of jobs removed
        """
        jobs = self.load()

        if not jobs:
            return 0

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # Filter out old jobs
        original_count = len(jobs)
        recent_jobs = [
            job for job in jobs
            if datetime.fromisoformat(job.scraped_at) > cutoff_date
        ]

        removed_count = original_count - len(recent_jobs)

        if removed_count > 0:
            # Save filtered jobs back to file
            self.save(recent_jobs)
            self.logger.info(f"Cleaned up {removed_count} jobs older than {self.retention_days} days")
        else:
            self.logger.info(f"No jobs older than {self.retention_days} days to clean up")

        return removed_count
