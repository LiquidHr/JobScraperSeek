"""FastAPI application for Seek Job Scraper."""

import asyncio
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .models import (
    ScrapeRequest, ScrapeResponse, ScrapeStatusResponse,
    JobResponse, JobsListResponse, WebhookRegistration,
    WebhookResponse, HealthResponse, ErrorResponse, JobStatus
)
from .job_manager import job_manager
from ..storage import JSONStorage
from ..utils import Config


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Seek Job Scraper API",
        description="""
        # Seek Job Scraper REST API

        Enterprise-grade API for scraping job listings from Seek.com.au

        ## Features
        - Asynchronous job scraping with status tracking
        - Automatic deduplication
        - Webhook notifications (n8n integration)
        - OpenAPI documentation
        - Rate limiting ready

        ## Agent Architecture
        This API implements an AI Agent pattern:
        - **Perception**: Scrapes job listings from Seek
        - **Memory**: Tracks seen jobs to avoid duplicates
        - **Action**: Saves results and triggers webhooks
        - **Tools**: Playwright browser automation, JSON/CSV storage

        ## Common Workflows

        ### 1. Trigger & Poll Pattern
        ```
        POST /api/v1/scrape -> Get job_id
        GET /api/v1/scrape/{job_id} -> Poll until completed
        GET /api/v1/jobs/latest -> Retrieve results
        ```

        ### 2. Webhook Pattern (n8n)
        ```
        POST /api/v1/webhooks -> Register n8n webhook
        POST /api/v1/scrape -> Scraping completes -> n8n receives data
        ```
        """,
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # CORS middleware for web integrations
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.detail,
                timestamp=datetime.now()
            ).model_dump(mode='json')
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred",
                detail=str(exc),
                timestamp=datetime.now()
            ).model_dump(mode='json')
        )

    # Health check endpoint
    @app.get(
        "/api/v1/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Health check",
        description="Check API health and component status"
    )
    async def health_check():
        """Health check endpoint for monitoring."""
        try:
            # Check if config can be loaded
            config = Config()
            output_path = config.get_output_path("json")
            storage_path = output_path.parent
            storage_available = storage_path.exists() or storage_path.parent.exists()

            # Check if jobs.json file exists
            import os
            jobs_file_exists = output_path.exists()
            jobs_file_size = output_path.stat().st_size if jobs_file_exists else 0
            cwd = os.getcwd()

            components = {
                "config": "loaded",
                "storage": "available" if storage_available else "unavailable",
                "scraper": "ready",
                "job_queue": "operational",
                "jobs_file": f"{'exists' if jobs_file_exists else 'MISSING'} ({jobs_file_size} bytes)",
                "jobs_path": str(output_path),
                "working_dir": cwd
            }

            return HealthResponse(
                status="healthy",
                version="1.0.0",
                timestamp=datetime.now(),
                components=components
            )
        except Exception as e:
            return HealthResponse(
                status="degraded",
                version="1.0.0",
                timestamp=datetime.now(),
                components={"error": str(e)}
            )

    # Scrape endpoints
    @app.post(
        "/api/v1/scrape",
        response_model=ScrapeResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["Scraping"],
        summary="Trigger async scraping job",
        description="""
        Start a new scraping job that runs in the background.

        Returns immediately with a job_id for status tracking.
        Use GET /api/v1/scrape/{job_id} to check progress.
        """
    )
    async def trigger_scrape(
        request: ScrapeRequest,
        background_tasks: BackgroundTasks
    ):
        """Trigger an asynchronous scraping job."""
        try:
            # Create job
            job_id = job_manager.create_job(request)

            # Schedule background task
            background_tasks.add_task(job_manager.run_scrape_job, job_id)

            return ScrapeResponse(
                job_id=job_id,
                status=JobStatus.PENDING,
                message="Scraping job queued successfully",
                created_at=datetime.now()
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create scraping job: {str(e)}"
            )

    @app.get(
        "/api/v1/scrape/{job_id}",
        response_model=ScrapeStatusResponse,
        tags=["Scraping"],
        summary="Get scraping job status",
        description="Check the status and results of a scraping job"
    )
    async def get_scrape_status(job_id: str):
        """Get the status of a scraping job."""
        job = job_manager.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )

        # Convert Job objects to JobResponse
        results = None
        if job.results:
            results = [
                JobResponse(
                    **j.to_dict(),
                    job_id=j.job_id
                ) for j in job.results
            ]

        return ScrapeStatusResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            jobs_found=job.jobs_found,
            jobs_new=job.jobs_new,
            error=job.error,
            results=results
        )

    @app.get(
        "/api/v1/scrape",
        response_model=List[ScrapeStatusResponse],
        tags=["Scraping"],
        summary="List all scraping jobs",
        description="Get a list of all scraping jobs with optional status filter"
    )
    async def list_scrape_jobs(
        status: Optional[JobStatus] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return")
    ):
        """List all scraping jobs."""
        jobs = job_manager.list_jobs(status=status, limit=limit)

        return [
            ScrapeStatusResponse(
                job_id=job.job_id,
                status=job.status,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                jobs_found=job.jobs_found,
                jobs_new=job.jobs_new,
                error=job.error,
                results=None  # Don't include results in list view
            ) for job in jobs
        ]

    # Jobs endpoints
    @app.get(
        "/api/v1/jobs",
        response_model=JobsListResponse,
        tags=["Jobs"],
        summary="List all scraped jobs",
        description="Retrieve all scraped jobs with pagination"
    )
    async def list_jobs(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=200, description="Items per page"),
        company: Optional[str] = Query(None, description="Filter by company name"),
        location: Optional[str] = Query(None, description="Filter by location")
    ):
        """List all scraped jobs from storage."""
        try:
            config = Config()
            storage = JSONStorage(
                output_path=config.get_output_path("json"),
                seen_jobs_path=config.get_seen_jobs_path()
            )

            # Load all jobs
            jobs = storage.load()

            # Apply filters
            if company:
                jobs = [j for j in jobs if company.lower() in j.company.lower()]
            if location:
                jobs = [j for j in jobs if location.lower() in j.location.lower()]

            # Sort by scraped_at descending
            jobs.sort(key=lambda x: x.scraped_at, reverse=True)

            # Pagination
            total = len(jobs)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_jobs = jobs[start_idx:end_idx]

            # Convert to response models
            job_responses = [
                JobResponse(
                    **j.to_dict(),
                    job_id=j.job_id
                ) for j in page_jobs
            ]

            return JobsListResponse(
                total=total,
                page=page,
                page_size=page_size,
                jobs=job_responses
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve jobs: {str(e)}"
            )

    @app.get(
        "/api/v1/jobs/latest",
        response_model=List[JobResponse],
        tags=["Jobs"],
        summary="Get latest scraped jobs",
        description="Retrieve the most recently scraped jobs"
    )
    async def get_latest_jobs(
        limit: int = Query(1000, ge=1, le=5000, description="Number of jobs to return")
    ):
        """Get the latest scraped jobs."""
        try:
            config = Config()
            storage = JSONStorage(
                output_path=config.get_output_path("json"),
                seen_jobs_path=config.get_seen_jobs_path()
            )

            jobs = storage.load()
            jobs.sort(key=lambda x: x.scraped_at, reverse=True)

            latest_jobs = jobs[:limit]

            return [
                JobResponse(
                    **j.to_dict(),
                    job_id=j.job_id
                ) for j in latest_jobs
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve latest jobs: {str(e)}"
            )

    @app.get(
        "/api/v1/jobs/{job_id}",
        response_model=JobResponse,
        tags=["Jobs"],
        summary="Get job by ID",
        description="Retrieve a specific job by its ID"
    )
    async def get_job(job_id: str):
        """Get a specific job by ID."""
        try:
            config = Config()
            storage = JSONStorage(
                output_path=config.get_output_path("json"),
                seen_jobs_path=config.get_seen_jobs_path()
            )

            jobs = storage.load()

            for job in jobs:
                if job.job_id == job_id:
                    return JobResponse(
                        **job.to_dict(),
                        job_id=job.job_id
                    )

            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve job: {str(e)}"
            )

    # Webhook endpoints
    @app.post(
        "/api/v1/webhooks",
        response_model=WebhookResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Webhooks"],
        summary="Register a webhook",
        description="""
        Register a webhook URL to receive notifications when scraping jobs complete.

        Perfect for n8n integration!

        Events:
        - scrape.completed: Called when a scraping job finishes successfully
        - scrape.failed: Called when a scraping job fails
        """
    )
    async def register_webhook(webhook: WebhookRegistration):
        """Register a webhook for job events."""
        webhook_id = job_manager.register_webhook(
            webhook_url=str(webhook.webhook_url),
            events=webhook.events,
            description=webhook.description
        )

        return WebhookResponse(
            webhook_id=webhook_id,
            webhook_url=str(webhook.webhook_url),
            events=webhook.events,
            created_at=datetime.now()
        )

    @app.get(
        "/api/v1/webhooks",
        response_model=List[WebhookResponse],
        tags=["Webhooks"],
        summary="List all webhooks",
        description="Get all registered webhooks"
    )
    async def list_webhooks():
        """List all registered webhooks."""
        webhooks = job_manager.get_webhooks()

        return [
            WebhookResponse(
                webhook_id=wid,
                webhook_url=w["url"],
                events=w["events"],
                created_at=w["created_at"]
            ) for wid, w in webhooks.items()
        ]

    @app.delete(
        "/api/v1/webhooks/{webhook_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["Webhooks"],
        summary="Delete a webhook",
        description="Remove a registered webhook"
    )
    async def delete_webhook(webhook_id: str):
        """Delete a webhook."""
        success = job_manager.delete_webhook(webhook_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Webhook {webhook_id} not found"
            )

        return None

    # Serve static frontend files
    static_dir = Path(__file__).parent.parent.parent / "static"
    index_file = static_dir / "index.html"

    # Mount static assets directory
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    # Root and SPA routes - these catch all non-API requests
    if index_file.exists():
        # Import at function level to avoid circular imports
        from fastapi.responses import HTMLResponse

        # Root route
        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        async def read_root():
            return index_file.read_text()

        # Serve vite.svg
        @app.get("/vite.svg", include_in_schema=False)
        async def get_vite_svg():
            svg_file = static_dir / "vite.svg"
            if svg_file.exists():
                return FileResponse(svg_file)
            raise HTTPException(status_code=404)

        # SPA catch-all for client-side routing
        @app.get("/{catchall:path}", response_class=HTMLResponse, include_in_schema=False)
        async def spa_catchall(catchall: str):
            # Don't catch API routes
            if catchall.startswith("api"):
                raise HTTPException(status_code=404)
            # Serve index.html for all other routes
            return index_file.read_text()

    return app


# Create app instance
app = create_app()
