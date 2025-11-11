function JobCard({ job }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getScrapedBadge = (scrapedAt) => {
    // Show when we scraped this job (badge shows scrape freshness)
    if (!scrapedAt) return { label: 'Unknown', class: 'badge-gray' };

    const scrapedDate = new Date(scrapedAt);
    const now = new Date();
    const daysSinceScraped = Math.floor((now - scrapedDate) / (1000 * 60 * 60 * 24));

    if (daysSinceScraped === 0) return { label: 'Scraped today', class: 'badge-new' };
    if (daysSinceScraped === 1) return { label: 'Scraped yesterday', class: 'badge-recent' };
    if (daysSinceScraped === 2) return { label: 'Scraped 2 days ago', class: 'badge-older' };
    if (daysSinceScraped <= 7) return { label: `Scraped ${daysSinceScraped} days ago`, class: 'badge-old' };

    return { label: `Scraped ${daysSinceScraped} days ago`, class: 'badge-very-old' };
  };

  const getCurrentPostedDate = (scrapedAt, postedDate) => {
    // Calculate what Seek would show RIGHT NOW
    if (!scrapedAt || !postedDate) return postedDate || 'Unknown';

    const scrapedDate = new Date(scrapedAt);
    const now = new Date();
    const hoursSinceScraped = Math.floor((now - scrapedDate) / (1000 * 60 * 60));
    const daysSinceScraped = Math.floor(hoursSinceScraped / 24);

    // Parse the original posted date from Seek (e.g., "18h ago", "2d ago")
    let originalHours = 0;
    let originalDays = 0;

    const hoursMatch = postedDate.match(/(\d+)h ago/);
    const daysMatch = postedDate.match(/(\d+)d ago/);

    if (hoursMatch) {
      originalHours = parseInt(hoursMatch[1]);
    } else if (daysMatch) {
      originalDays = parseInt(daysMatch[1]);
      originalHours = originalDays * 24;
    }

    // Calculate current total hours/days
    const currentTotalHours = originalHours + hoursSinceScraped;
    const currentTotalDays = Math.floor(currentTotalHours / 24);

    // Format like Seek does
    if (currentTotalHours < 24) {
      return `${currentTotalHours}h ago`;
    } else {
      return `${currentTotalDays}d ago`;
    }
  };

  const scrapedBadge = getScrapedBadge(job.scraped_at);
  const currentPostedDate = getCurrentPostedDate(job.scraped_at, job.posted_date);

  return (
    <div className="job-card">
      <div className="job-card-header">
        <h3 className="job-title">
          <a href={job.job_url} target="_blank" rel="noopener noreferrer">
            {job.title}
          </a>
        </h3>
        <div className="job-badges">
          <span className={`job-age-badge ${scrapedBadge.class}`}>{scrapedBadge.label}</span>
          <span className="job-time">Posted: {currentPostedDate}</span>
        </div>
      </div>

      <div className="job-company">
        <strong>{job.company}</strong>
      </div>

      <div className="job-details">
        <span className="job-detail-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0a6 6 0 0 0-6 6c0 3.3 6 10 6 10s6-6.7 6-10a6 6 0 0 0-6-6zm0 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/>
          </svg>
          {job.location}
        </span>

        {job.salary && (
          <span className="job-detail-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm1 12H7V7h2v5zm0-6H7V4h2v2z"/>
            </svg>
            {job.salary}
          </span>
        )}

        {job.job_type && (
          <span className="job-detail-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M14 4h-2V3c0-.55-.45-1-1-1H5c-.55 0-1 .45-1 1v1H2c-1.1 0-2 .9-2 2v7c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM5 3h6v1H5V3z"/>
            </svg>
            {job.job_type}
          </span>
        )}
      </div>

      {job.description && (
        <div className="job-description">
          {job.description.substring(0, 150)}
          {job.description.length > 150 ? '...' : ''}
        </div>
      )}

      <div className="job-card-footer">
        <a
          href={job.job_url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-small btn-primary"
        >
          View on Seek
        </a>
      </div>
    </div>
  );
}

export default JobCard;
