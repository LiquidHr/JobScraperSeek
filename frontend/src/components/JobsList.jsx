import { useState } from 'react';
import JobCard from './JobCard';

function JobsList({ jobs, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLocation, setFilterLocation] = useState('');
  const [filterJobType, setFilterJobType] = useState('');

  // Extract unique locations and job types for filters
  const uniqueLocations = [...new Set(jobs.map(job => job.location))].filter(Boolean).sort();
  const uniqueJobTypes = [...new Set(jobs.map(job => job.job_type))].filter(Boolean).sort();

  // Filter jobs
  const filteredJobs = jobs.filter(job => {
    // Search matches title, company, location, or description
    const matchesSearch = !searchTerm ||
                         job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (job.description && job.description.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesLocation = !filterLocation || job.location === filterLocation;
    const matchesJobType = !filterJobType || job.job_type === filterJobType;

    return matchesSearch && matchesLocation && matchesJobType;
  });

  const handleExport = () => {
    // Export to CSV
    const headers = ['Title', 'Company', 'Location', 'Salary', 'Job Type', 'URL', 'Scraped At'];
    const rows = filteredJobs.map(job => [
      job.title,
      job.company,
      job.location,
      job.salary || 'N/A',
      job.job_type || 'N/A',
      job.job_url,
      new Date(job.scraped_at).toLocaleString()
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `seek-jobs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="jobs-list">
      <div className="jobs-controls">
        <div className="search-filters">
          <input
            type="text"
            placeholder="Search jobs, companies, locations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />

          <select
            value={filterLocation}
            onChange={(e) => setFilterLocation(e.target.value)}
            className="filter-select"
          >
            <option value="">All Locations</option>
            {uniqueLocations.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>

          <select
            value={filterJobType}
            onChange={(e) => setFilterJobType(e.target.value)}
            className="filter-select"
          >
            <option value="">All Job Types</option>
            {uniqueJobTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="action-buttons">
          <button onClick={onRefresh} className="btn btn-secondary">
            Refresh
          </button>
          <button onClick={handleExport} className="btn btn-secondary">
            Export CSV
          </button>
        </div>
      </div>

      <div className="results-info">
        Showing {filteredJobs.length} of {jobs.length} jobs
      </div>

      {filteredJobs.length === 0 ? (
        <div className="empty-state">
          <p>No jobs found. Try adjusting your filters or start a new scrape.</p>
        </div>
      ) : (
        <div className="jobs-grid">
          {filteredJobs.map(job => (
            <JobCard key={job.job_id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}

export default JobsList;
