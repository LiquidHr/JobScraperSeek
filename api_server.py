#!/usr/bin/env python3
"""
API Server Entry Point for Render.com Deployment

This file serves as the main entry point for the API server when deployed to Render.
It imports and runs the FastAPI application with Uvicorn.
"""

import argparse
import sys
import os
import uvicorn

# Add the project root to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.app import app


def main():
    """Run the API server with command-line arguments."""
    parser = argparse.ArgumentParser(description="Seek Job Scraper API Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    # Print startup information
    print(f"Starting Seek Job Scraper API Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Data Directory: {os.path.join(os.getcwd(), 'data')}")

    # Check if data directory exists
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir):
        print(f"WARNING: Data directory not found at {data_dir}")
        print("Creating data directory...")
        os.makedirs(data_dir, exist_ok=True)

    # Check if jobs.json exists
    jobs_file = os.path.join(data_dir, "jobs.json")
    if not os.path.exists(jobs_file):
        print(f"WARNING: jobs.json not found at {jobs_file}")
        print("Creating empty jobs.json file...")
        with open(jobs_file, 'w') as f:
            f.write('[]')

    # Run the server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
