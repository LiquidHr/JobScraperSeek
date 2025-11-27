import { useState } from 'react';
import JobCard from './JobCard';

function JobsList({ jobs, onRefresh }) {
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

  // Extract unique job types for filter (normalize by trimming whitespace)
  const uniqueJobTypes = [...new Set(jobs.map(job => job.job_type?.trim()).filter(Boolean))].sort();

  // Filter jobs
  const filteredJobs = jobs.filter(job => {
    // Location filter: match by region/state only
    const matchesLocation = !filterLocation ||
                           getLocationRegion(job.location) === filterLocation;

    // Job type filter: exact match (with whitespace normalization)
    const matchesJobType = !filterJobType || job.job_type?.trim() === filterJobType;

    return matchesLocation && matchesJobType;
  });

  // Debug logging
  console.log('=== FILTER DEBUG ===');
  console.log('Filter state:', { filterLocation, filterJobType });
  console.log('Total jobs:', jobs.length, '| Filtered jobs:', filteredJobs.length);
  console.log('Available locations:', locationRegions);
  console.log('Available job types:', uniqueJobTypes);

  // Log first 3 jobs to verify data
  if (jobs.length > 0) {
    console.log('Sample jobs data:');
    jobs.slice(0, 3).forEach((job, i) => {
      console.log(`  Job ${i + 1}:`, {
        title: job.title,
        location: job.location,
        locationRegion: getLocationRegion(job.location),
        job_type: job.job_type,
        job_type_trimmed: job.job_type?.trim(),
        job_type_length: job.job_type?.length,
        job_type_charCodes: job.job_type ? Array.from(job.job_type).map(c => c.charCodeAt(0)) : []
      });
    });
  }

  // When filtering by job type, show which jobs match
  if (filterJobType) {
    console.log(`\n🔍 Filtering by job type: "${filterJobType}"`);
    console.log('Filter job type length:', filterJobType.length);
    console.log('Filter job type char codes:', Array.from(filterJobType).map(c => c.charCodeAt(0)));

    const matchingJobs = jobs.filter(job => job.job_type?.trim() === filterJobType);
    console.log(`Found ${matchingJobs.length} matching jobs for "${filterJobType}"`);

    if (matchingJobs.length > 0) {
      console.log('First 3 matching jobs:');
      matchingJobs.slice(0, 3).forEach((job, i) => {
        console.log(`  Match ${i + 1}:`, {
          title: job.title,
          job_type: job.job_type,
          job_type_trimmed: job.job_type?.trim(),
          matches: job.job_type?.trim() === filterJobType
        });
      });
    }

    // Show jobs that don't match and why
    const nonMatchingJobs = jobs.filter(job => {
      const trimmed = job.job_type?.trim();
      return trimmed && trimmed !== filterJobType;
    });
    console.log(`\nJobs that don't match "${filterJobType}":`);
    const uniqueNonMatching = [...new Set(nonMatchingJobs.map(j => j.job_type?.trim()))];
    uniqueNonMatching.slice(0, 5).forEach(type => {
      console.log(`  - "${type}" (length: ${type?.length})`);
    });
  }

  console.log('==================');

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
        <div>
          Showing {filteredJobs.length} of {jobs.length} jobs
          {(filterLocation || filterJobType) && (
            <span style={{ marginLeft: '10px', color: '#666' }}>
              (Filters active:
              {filterLocation && ` Location: ${filterLocation}`}
              {filterJobType && ` | Type: ${filterJobType}`}
              )
            </span>
          )}
        </div>
        {(filterLocation || filterJobType) && (
          <button
            onClick={() => {
              setFilterLocation('');
              setFilterJobType('');
            }}
            className="btn btn-small"
            style={{ marginLeft: '10px' }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {filteredJobs.length === 0 ? (
        <div className="empty-state">
          <p>No jobs found. Try adjusting your filters or start a new scrape.</p>
        </div>
      ) : (
        <div className="jobs-grid" key={`grid-${filterJobType}-${filterLocation}`}>
          {filteredJobs.map((job, index) => {
            if (index < 5) {
              console.log(`📋 Rendering job ${index}:`, {
                job_id: job.job_id,
                title: job.title,
                company: job.company,
                location: job.location,
                job_type: job.job_type,
                job_type_trimmed: job.job_type?.trim(),
                passed_filter: !filterJobType || job.job_type?.trim() === filterJobType
              });
            }
            // Use combination of job_id and index to ensure unique keys
            return <JobCard key={`${job.job_id}-${index}`} job={job} />;
          })}
        </div>
      )}
    </div>
  );
}

export default JobsList;
