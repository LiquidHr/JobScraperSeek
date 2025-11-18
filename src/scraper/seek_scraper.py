"""Main Seek scraper using Playwright."""

import time
import logging
from typing import List, Optional
from urllib.parse import urljoin, quote
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

from ..models import Job
from ..utils import Config


class SeekScraper:
    """Scraper for Seek.com.au job listings."""

    def __init__(self, config: Config, logger: logging.Logger):
        """Initialize the scraper.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.base_url = config.get("scraper.base_url")
        self.classification = config.get("scraper.classification")
        self.excluded_subcategories = set(config.get("scraper.excluded_subcategories", []))
        self.excluded_companies = set(config.get("scraper.excluded_companies", []))
        self.max_pages = config.get("scraper.max_pages", 20)
        self.retry_attempts = config.get("scraper.retry_attempts", 3)
        self.retry_delay = config.get("scraper.retry_delay", 5)
        self.headless = config.get("scraper.headless", True)
        self.browser_type = config.get("scraper.browser_type", "chromium")

    def scrape(self) -> List[Job]:
        """Scrape job listings.

        Returns:
            List of Job objects
        """
        self.logger.info("Starting Seek scraper...")

        # Log filtering settings
        subclassification_ids = self.config.get("scraper.subclassification_ids")
        if subclassification_ids:
            num_subcats = len(subclassification_ids.split(','))
            self.logger.info(f"Using subclassification filter: {num_subcats} subcategories (excluding Recruitment - Agency at source)")
        else:
            self.logger.info(f"No subclassification filter (will filter {len(self.excluded_subcategories)} subcategories after scraping)")

        self.logger.info(f"Excluding {len(self.excluded_companies)} recruitment agencies by company name")

        jobs = []

        with sync_playwright() as playwright:
            browser = self._launch_browser(playwright)

            try:
                page = browser.new_page()
                self._set_page_defaults(page)

                # Navigate to search results
                search_url = self._build_search_url()
                self.logger.info(f"Navigating to: {search_url}")

                page.goto(search_url, wait_until="domcontentloaded")
                time.sleep(2)  # Allow page to fully load

                # Scrape multiple pages
                page_num = 1
                while page_num <= self.max_pages:
                    self.logger.info(f"Scraping page {page_num}...")

                    page_jobs = self._scrape_page(page)
                    jobs.extend(page_jobs)

                    self.logger.info(f"Found {len(page_jobs)} jobs on page {page_num}")

                    # Check if there's a next page
                    if not self._goto_next_page(page):
                        self.logger.info("No more pages to scrape")
                        break

                    page_num += 1
                    time.sleep(2)  # Be respectful

            finally:
                browser.close()

        self.logger.info(f"Total jobs scraped: {len(jobs)}")
        return jobs

    def _launch_browser(self, playwright) -> Browser:
        """Launch browser instance.

        Args:
            playwright: Playwright instance

        Returns:
            Browser instance
        """
        if self.browser_type == "firefox":
            browser = playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            browser = playwright.webkit.launch(headless=self.headless)
        else:
            browser = playwright.chromium.launch(headless=self.headless)

        return browser

    def _set_page_defaults(self, page: Page):
        """Set default page configuration.

        Args:
            page: Playwright page
        """
        user_agent = self.config.get("scraper.user_agent")
        if user_agent:
            page.set_extra_http_headers({"User-Agent": user_agent})

        timeout = self.config.get("scraper.request_timeout", 30) * 1000
        page.set_default_timeout(timeout)

    def _build_search_url(self) -> str:
        """Build search URL for HR & Recruitment classification.

        Returns:
            Search URL
        """
        # Seek uses a slug-based URL structure for classifications
        # HR & Recruitment: /jobs-in-human-resources-recruitment
        classification_slug = self.config.get(
            "scraper.classification_slug",
            "jobs-in-human-resources-recruitment"
        )
        base_url = f"{self.base_url}/{classification_slug}"

        # Build query parameters
        params = []

        # Add date range filter if specified
        # daterange=3 means "last 3 days"
        date_range = self.config.get("scraper.date_range")
        if date_range and date_range > 0:
            params.append(f"daterange={date_range}")

        # Add subclassification filter if specified
        # This filters at the source (more efficient)
        # Example: 6323,6322,6321 (all HR subcategories except Recruitment - Agency)
        subclassification_ids = self.config.get("scraper.subclassification_ids")
        if subclassification_ids:
            # URL encode the comma-separated IDs
            from urllib.parse import quote
            encoded_ids = quote(subclassification_ids, safe='')
            params.append(f"subclassification={encoded_ids}")

        # Combine parameters
        if params:
            return f"{base_url}?{'&'.join(params)}"

        return base_url

    def _scrape_page(self, page: Page) -> List[Job]:
        """Scrape jobs from current page.

        Args:
            page: Playwright page

        Returns:
            List of Job objects from this page
        """
        jobs = []

        # Wait for job cards to load
        try:
            page.wait_for_selector('[data-search-sol-meta]', timeout=10000)
        except PlaywrightTimeout:
            self.logger.warning("Timeout waiting for job listings")
            return jobs

        # Find all job cards
        job_cards = page.query_selector_all('[data-search-sol-meta]')

        self.logger.debug(f"Found {len(job_cards)} job cards on page")

        for card in job_cards:
            try:
                job = self._extract_job_data(card, page)
                if job and self._should_include_job(job):
                    jobs.append(job)
                elif job:
                    self.logger.debug(f"Excluded job: {job.title} ({job.subcategory})")
            except Exception as e:
                self.logger.error(f"Error extracting job data: {e}")

        return jobs

    def _extract_job_data(self, card, page: Page) -> Optional[Job]:
        """Extract job data from a job card.

        Args:
            card: Job card element
            page: Playwright page

        Returns:
            Job object or None
        """
        try:
            # Extract title and URL - try multiple selectors
            title_elem = (
                card.query_selector('a[data-job-id]') or
                card.query_selector('a[data-automation="jobTitle"]') or
                card.query_selector('a[href*="/job/"]') or
                card.query_selector('h3 a') or
                card.query_selector('article a')
            )

            if not title_elem:
                self.logger.debug("Could not find title element in card")
                return None

            title = title_elem.inner_text().strip()
            href = title_elem.get_attribute('href')
            if not href:
                self.logger.debug(f"No href found for title: {title}")
                return None

            job_url = urljoin(self.base_url, href)

            # Extract company - try multiple selectors
            company_elem = (
                card.query_selector('[data-automation="jobCompany"]') or
                card.query_selector('[data-automation="advertiser-name"]') or
                card.query_selector('span[data-automation*="company"]') or
                card.query_selector('span[data-automation*="advertiser"]')
            )
            company = company_elem.inner_text().strip() if company_elem else "Unknown"

            # Extract location - try multiple selectors
            location_elem = (
                card.query_selector('[data-automation="jobLocation"]') or
                card.query_selector('[data-automation="job-location"]') or
                card.query_selector('span[data-automation*="location"]')
            )
            location = location_elem.inner_text().strip() if location_elem else "Unknown"

            # Extract salary - try multiple selectors
            salary_elem = (
                card.query_selector('[data-automation="jobSalary"]') or
                card.query_selector('[data-automation="job-salary"]') or
                card.query_selector('span[data-automation*="salary"]')
            )
            salary = salary_elem.inner_text().strip() if salary_elem else None

            # Extract subcategory/classification info - try multiple selectors
            subcategory_elem = (
                card.query_selector('[data-automation="jobClassification"]') or
                card.query_selector('[data-automation="job-classification"]') or
                card.query_selector('span[data-automation*="classification"]')
            )
            subcategory = subcategory_elem.inner_text().strip() if subcategory_elem else "Unknown"

            # Extract posted date - try multiple selectors
            posted_elem = (
                card.query_selector('[data-automation="jobListingDate"]') or
                card.query_selector('[data-automation="job-listing-date"]') or
                card.query_selector('span[data-automation*="date"]') or
                card.query_selector('time')
            )
            # Set default value if posted date is not found
            posted_date = posted_elem.inner_text().strip() if posted_elem else "Recently"

            # Extract description snippet - try multiple selectors
            description_elem = (
                card.query_selector('[data-automation="jobShortDescription"]') or
                card.query_selector('[data-automation="job-short-description"]') or
                card.query_selector('p[data-automation*="description"]') or
                card.query_selector('div[data-automation*="snippet"]')
            )
            description = description_elem.inner_text().strip() if description_elem else None

            return Job(
                title=title,
                company=company,
                location=location,
                classification=self.classification,
                subcategory=subcategory,
                job_url=job_url,
                salary=salary,
                posted_date=posted_date,
                description=description
            )

        except Exception as e:
            self.logger.error(f"Error parsing job card: {e}")
            return None

    def _should_include_job(self, job: Job) -> bool:
        """Check if job should be included based on filters.

        Args:
            job: Job object

        Returns:
            True if job should be included
        """
        # Check if subcategory is in excluded list
        for excluded in self.excluded_subcategories:
            if excluded.lower() in job.subcategory.lower():
                self.logger.debug(f"Excluded by subcategory '{excluded}': {job.title}")
                return False

        # Check if company name contains BOTH "recruitment" AND "agency" (case-insensitive)
        company_lower = job.company.lower()
        if "recruitment" in company_lower and "agency" in company_lower:
            self.logger.debug(f"Excluded by keyword filter (recruitment + agency): {job.title} at {job.company}")
            return False

        # Check if company is in excluded list (case-insensitive partial match)
        for excluded_company in self.excluded_companies:
            if excluded_company.lower() in job.company.lower():
                self.logger.debug(f"Excluded by company '{excluded_company}': {job.title} at {job.company}")
                return False

        return True

    def _goto_next_page(self, page: Page) -> bool:
        """Navigate to next page if available.

        Args:
            page: Playwright page

        Returns:
            True if navigation succeeded
        """
        try:
            # Look for next page button with multiple selectors
            selectors = [
                'a[data-automation="page-next"]',
                'a[aria-label="Next"]',
                'nav[data-automation="pagination"] a:has-text("Next")',
                'button:has-text("Next")',
                'a.next',
                '[rel="next"]'
            ]

            for selector in selectors:
                self.logger.debug(f"Trying selector: {selector}")
                next_button = page.query_selector(selector)

                if next_button:
                    self.logger.debug(f"Found next button with selector: {selector}")
                    is_visible = next_button.is_visible()
                    self.logger.debug(f"Button visible: {is_visible}")

                    if is_visible:
                        self.logger.info(f"Clicking next page button")
                        next_button.click()
                        page.wait_for_load_state("domcontentloaded")
                        time.sleep(2)  # Wait for new content to load
                        return True

            self.logger.debug("No next page button found with any selector")
            return False

        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False
