"""Job data model."""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Job:
    """Job listing data model."""

    title: str
    company: str
    location: str
    classification: str
    subcategory: str
    job_url: str
    posted_date: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, Casual
    description: Optional[str] = None
    scraped_at: str = None

    def __post_init__(self):
        """Set scraped_at timestamp if not provided."""
        if self.scraped_at is None:
            self.scraped_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create job from dictionary."""
        return cls(**data)

    @property
    def job_id(self) -> str:
        """Extract job ID from URL."""
        # Seek URLs typically end with /job/{id}
        if "/job/" in self.job_url:
            return self.job_url.split("/job/")[-1].split("?")[0]
        return self.job_url

    def __hash__(self):
        """Hash based on job URL."""
        return hash(self.job_url)

    def __eq__(self, other):
        """Compare jobs based on URL."""
        if isinstance(other, Job):
            return self.job_url == other.job_url
        return False
