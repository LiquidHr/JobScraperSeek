import { useState } from 'react';
import JobCard from './JobCard';

function JobsList({ jobs, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLocation, setFilterLocation] = useState('');
  const [filterJobType, setFilterJobType] = useState('');

  // Helper function to extract state/region from location
  const getLocationRegion = (location) => {
    if (!location) return 'Unknown';

    // Check if location already contains state abbreviation
    const stateMatch = location.match(/\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b/i);
    if (stateMatch) {
      return stateMatch[1].toUpperCase();
    }

    // Map common cities to states
    const cityToState = {
      'Sydney': 'NSW', 'Melbourne': 'VIC', 'Brisbane': 'QLD',
      'Adelaide': 'SA', 'Perth': 'WA', 'Hobart': 'TAS',
      'Darwin': 'NT', 'Canberra': 'ACT'
    };

    for (const [city, state] of Object.entries(cityToState)) {
      if (location.toLowerCase().includes(city.toLowerCase())) {
        return state;
      }
    }

    // Return 'Other' if we can't determine state
    return 'Other';
  };

  // Extract unique regions/states for location filter
  const locationRegions = [...new Set(jobs.map(job => getLocationRegion(job.location)))].filter(Boolean).sort();

  // Extract unique job types for filter
  const uniqueJobTypes = [...new Set(jobs.map(job => job.job_type))].filter(Boolean).sort();

  // Filter jobs
  const filteredJobs = jobs.filter(job => {
    // Search matches title, company, location, or description
    const matchesSearch = !searchTerm ||
                         job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (job.location && job.location.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         (job.description && job.description.toLowerCase().includes(searchTerm.toLowerCase()));

    // Location filter: match by region/state only
    const matchesLocation = !filterLocation ||
                           getLocationRegion(job.location) === filterLocation;

    // Job type filter: exact match
    const matchesJobType = !filterJobType || job.job_type === filterJobType;

    return matchesSearch && matchesLocation && matchesJobType;
  });

  // Debug logging
  console.log('Filter state:', { filterLocation, filterJobType, searchTerm });
  console.log('Total jobs:', jobs.length, '| Filtered jobs:', filteredJobs.length);

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
            {locationRegions.map(region => (
              <option key={region} value={region}>{region}</option>
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
          {filteredJobs.map((job, index) => {
            if (index < 3) console.log(`Rendering job ${index}:`, job.title, job.location, job.job_type);
            return <JobCard key={job.job_id} job={job} />;
          })}
        </div>
      )}
    </div>
  );
}

export default JobsList;
