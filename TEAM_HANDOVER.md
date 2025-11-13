# Team Handover Document

**LiquidHR Job Scraper - Complete Handover Guide**

---

## 🎯 Quick Access

| Resource | URL | Purpose |
|----------|-----|---------|
| **Live Dashboard** | https://jobscraper-frontend-7bm6.onrender.com | View jobs (public) |
| **API Backend** | https://seek-scraper-api.onrender.com | API endpoints |
| **API Docs** | https://seek-scraper-api.onrender.com/api/docs | Interactive API documentation |
| **GitHub Repo** | https://github.com/JixuanYU0/JobScraperSeek | Source code |
| **Render Dashboard** | https://dashboard.render.com | Deployment management |

---

## 🚀 What Is This System?

An automated job scraper that:
- ✅ Scrapes HR & Recruitment jobs from Seek.com.au
- ✅ Filters out 58+ recruitment agencies
- ✅ Removes duplicate jobs
- ✅ Displays jobs on a clean web dashboard
- ✅ Runs automatically (currently needs manual trigger on Render)
- ✅ Stores 622 jobs currently

---

## 📊 Current Status (as of Nov 14, 2025)

### ✅ Working:
- Frontend dashboard displaying 622 jobs
- API returning job data correctly
- Search, filter, and export features
- Mobile-responsive design
- Automatic deduplication

### ⚠️ Known Limitations:
- **Render Free Tier**: Services sleep after 15 minutes of inactivity
  - First page load takes 30-60 seconds to wake up
  - Solution: Upgrade to Render paid tier ($7/month per service) for always-on
- **Automatic Scraping**: Not yet configured on Render
  - Currently requires manual trigger
  - See "How to Run Scraper" section below

### 🔄 Next Steps (Optional):
- Set up Render Cron Job for automatic scraping (requires paid plan)
- Or: Manually trigger scraper every 3 days
- Consider PostgreSQL for persistent data storage

---

## 📖 Documentation Structure

| Document | Purpose | Audience |
|----------|---------|----------|
| **README.md** | Project overview, quick start | Everyone |
| **USER_GUIDE.md** | How to use dashboard | End users |
| **TECHNICAL_GUIDE.md** | Architecture, API, deployment | Developers/IT |
| **INSTALLATION_GUIDE.md** | Local setup instructions | Developers |
| **DEPLOYMENT_GUIDE.md** | Cloud deployment options | DevOps |
| **RENDER_SETUP_GUIDE.md** | Render-specific deployment | DevOps |
| **WORKFLOW_GUIDE.md** | How automation works | Everyone |
| **DATA_STORAGE_GUIDE.md** | Data management, backups | IT/Admins |
| **TEAM_HANDOVER.md** | This document | New team members |

---

## 🔑 Key Information

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                       │
│              https://jobscraper-frontend                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                      │
│              Render Static Site Service                 │
│                  - Search & Filter UI                   │
│                  - Job Display                          │
│                  - CSV Export                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  API BACKEND (FastAPI)                  │
│               Render Web Service (Python)               │
│                  - Job data endpoints                   │
│                  - Health checks                        │
│                  - CORS handling                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA STORAGE (JSON)                    │
│                  data/jobs.json (622 jobs)              │
│                  data/seen_jobs.json (tracking)         │
└─────────────────────────────────────────────────────────┘
```

### Key Configuration Files

| File | Purpose | Modify For |
|------|---------|------------|
| `config/config.yaml` | Main configuration | Scraping settings, filters, frequency |
| `render.yaml` | Render deployment | Service configuration, URLs |
| `.dockerignore` | Deployment files | What files to include/exclude |
| `frontend/src/App.jsx` | Frontend logic | UI changes, API URL |
| `src/api/app.py` | API endpoints | New endpoints, CORS |

### Important Data Files

| File | Purpose | Size | Location |
|------|---------|------|----------|
| `data/jobs.json` | Main job database | 622 jobs | Git-tracked |
| `data/seen_jobs.json` | Deduplication tracker | ~300 URLs | Gitignored |
| `logs/scraper_*.log` | Scraper execution logs | Variable | Gitignored |

---

## 🛠️ Common Tasks

### 1. How to Update the Live Site

**When:** After code changes, config updates, or new features

```bash
# 1. Make your changes locally
# 2. Test locally
./start.sh  # Test dashboard at http://localhost:8001

# 3. Commit and push to GitHub
git add .
git commit -m "Description of changes"
git push origin main

# 4. Render auto-deploys in 5-10 minutes
# Check: https://dashboard.render.com
```

### 2. How to Run the Scraper Manually

**When:** To get fresh jobs, test scraping, or run on-demand

**Option A: On Render (via SSH):**
```bash
# Go to Render Dashboard → liquidhr-api service → Shell
python main.py
```

**Option B: Locally:**
```bash
# SSH or local terminal
cd /path/to/JobScraperSeek
./run_scraper.sh

# Push updated data
git add data/jobs.json
git commit -m "Manual scrape: Added X new jobs"
git push origin main
```

### 3. How to Check System Health

**Frontend:**
- Visit: https://jobscraper-frontend-7bm6.onrender.com
- Should see job listings
- Search should work
- Export CSV should work

**API:**
```bash
# Health check
curl https://seek-scraper-api.onrender.com/api/v1/health

# Get latest jobs
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/latest?limit=5"

# Job count
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/stats"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "config": "loaded",
    "storage": "available",
    "scraper": "ready"
  }
}
```

### 4. How to Update Configuration

**Example: Change scrape frequency or add excluded company**

```bash
# 1. Edit config/config.yaml
vim config/config.yaml

# Example changes:
# - Add to excluded_companies list
# - Change date_range: 7 (for last 7 days)
# - Update retention_days: 60

# 2. Commit and push
git add config/config.yaml
git commit -m "Config: Added XYZ company to exclusion list"
git push origin main

# 3. Render auto-deploys with new config
```

### 5. How to Export Job Data

**Via Dashboard:**
1. Go to https://jobscraper-frontend-7bm6.onrender.com
2. Click "Export CSV" button
3. Opens in new window → Save file

**Via API:**
```bash
# Export all jobs
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/latest?limit=1000" > jobs_export.json

# Export as CSV (if endpoint exists)
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/export/csv" > jobs_export.csv
```

**Via GitHub:**
```bash
# Clone repo and access data file directly
git clone https://github.com/JixuanYU0/JobScraperSeek.git
cd JobScraperSeek
cat data/jobs.json
```

---

## 🔧 Troubleshooting

### Issue: Dashboard shows 0 jobs

**Symptoms:** Frontend loads but displays "0 jobs scraped"

**Diagnosis:**
```bash
# 1. Check API is responding
curl https://seek-scraper-api.onrender.com/api/v1/health

# 2. Check jobs endpoint
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/latest?limit=1"

# 3. Check GitHub data file
git pull
cat data/jobs.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)))"
```

**Solutions:**
- If API returns empty array → Run manual scrape (see Task #2)
- If API is down → Check Render dashboard for errors
- If frontend can't reach API → Check CORS settings in `src/api/app.py`

### Issue: Site is slow or times out

**Cause:** Render free tier sleeps after 15 minutes inactivity

**Solutions:**
- **Temporary:** Wait 30-60 seconds for service to wake up
- **Permanent:** Upgrade to Render paid tier ($7/month per service)
  - Go to Render Dashboard → Service → Upgrade

### Issue: Scraper fails or finds no jobs

**Diagnosis:**
```bash
# Check logs
tail -f logs/scraper_*.log

# Test Seek website is accessible
curl https://www.seek.com.au/jobs-in-human-resources-recruitment
```

**Common Causes:**
- Seek changed their HTML structure → Update scraper selectors in `src/scraper/seek_scraper.py`
- Rate limiting → Increase delays in `config/config.yaml`
- Network issues → Check internet connection

**Solutions:**
- Review `logs/scraper_*.log` for error messages
- Test locally with `./run_scraper.sh`
- Update scraper code if Seek site changed

### Issue: New deployment breaks site

**Rollback:**
```bash
# 1. Go to Render Dashboard
# 2. Service → Manual Deploy
# 3. Choose previous successful commit
# 4. Click "Deploy"

# OR via Git:
git revert HEAD
git push origin main
```

---

## 🔐 Access & Credentials

### GitHub
- **Repository:** https://github.com/JixuanYU0/JobScraperSeek
- **Access:** Your team GitHub account
- **Branch:** `main`

### Render
- **Dashboard:** https://dashboard.render.com
- **Login:** Your team Render account
- **Services:**
  - `seek-scraper-api` (backend)
  - `jobscraper-frontend-7bm6` (frontend)

### Deployment
- **Auto-deploys:** Yes, on every `git push` to `main`
- **Manual deploy:** Render Dashboard → Service → Manual Deploy
- **Environment Variables:** Set in Render Dashboard → Service → Environment

---

## 💰 Cost Breakdown

### Current Setup (Free Tier)
- **Render Web Service (API):** FREE
- **Render Static Site (Frontend):** FREE
- **GitHub:** FREE
- **Total:** $0/month

**Limitations:**
- Services sleep after 15 min inactivity
- 750 hours/month (enough for 24/7)
- Cold start: 30-60 seconds

### Recommended Upgrade (Paid Tier)
- **Render Web Service (API):** $7/month
- **Render Static Site (Frontend):** FREE (static sites don't sleep)
- **Total:** $7/month

**Benefits:**
- Always-on (no sleep)
- Instant response
- 1 GB RAM
- Cron jobs available

### Future Scaling Options
- **PostgreSQL Database:** $7/month (for better data persistence)
- **Cron Job Worker:** Included in paid plan
- **Custom Domain:** ~$12/year

---

## 📈 Usage Patterns

### Expected Traffic
- **Internal use:** 5-20 users
- **Frequency:** Daily checks by HR team
- **Peak times:** Morning (9-11 AM)
- **Data size:** ~1000 jobs max

### Data Growth
- **New jobs per scrape:** ~50-150 jobs (every 3 days)
- **Total database:** Capped at 30 days retention = ~600-800 jobs
- **Storage:** < 5 MB total

### Recommended Scrape Schedule
- **Current:** Every 3 days at 9:00 AM
- **Optimal:** Every 2-3 days (to catch new listings)
- **Off-hours:** Run at 2:00 AM to avoid peak traffic

---

## 🚀 Future Enhancements (Roadmap)

### High Priority
- [ ] Set up Render Cron Job for automatic scraping
- [ ] Add email notifications for new jobs
- [ ] PostgreSQL database for better persistence

### Medium Priority
- [ ] Slack integration (post new jobs to channel)
- [ ] Save job searches (user preferences)
- [ ] Job matching/recommendations

### Low Priority
- [ ] Multiple job boards (LinkedIn, Indeed)
- [ ] Advanced analytics dashboard
- [ ] Mobile app

---

## 📞 Support & Contacts

### Technical Issues
- **GitHub Issues:** https://github.com/JixuanYU0/JobScraperSeek/issues
- **Render Support:** https://render.com/docs
- **Documentation:** See docs/ folder in repo

### Code Questions
- **Architecture:** See `TECHNICAL_GUIDE.md`
- **API Reference:** https://seek-scraper-api.onrender.com/api/docs
- **User Guide:** See `USER_GUIDE.md`

### Business Questions
- **Requirements:** Review `config/config.yaml`
- **Excluded Companies:** Lines 40-106 in `config/config.yaml`
- **Filters:** Lines 16-32 in `config/config.yaml`

---

## ✅ Handover Checklist

Before considering handover complete, verify:

- [ ] All team members have access to:
  - [ ] GitHub repository
  - [ ] Render dashboard
  - [ ] Live frontend URL
  - [ ] API documentation

- [ ] Team has reviewed:
  - [ ] This handover document
  - [ ] USER_GUIDE.md (for end users)
  - [ ] TECHNICAL_GUIDE.md (for developers)

- [ ] Team can perform:
  - [ ] Access live dashboard
  - [ ] Run manual scrape
  - [ ] Update configuration
  - [ ] Deploy code changes
  - [ ] Check system health
  - [ ] Export job data

- [ ] Team understands:
  - [ ] System architecture
  - [ ] Deployment process
  - [ ] Common troubleshooting
  - [ ] Cost structure
  - [ ] Data storage location

- [ ] System is verified working:
  - [ ] Frontend loads
  - [ ] API responds
  - [ ] Jobs display correctly
  - [ ] Search/filter works
  - [ ] CSV export works

---

## 🎓 Getting Started (New Team Member)

**Day 1 - Access:**
1. Get GitHub access → https://github.com/JixuanYU0/JobScraperSeek
2. Get Render access → https://dashboard.render.com
3. Bookmark live site → https://jobscraper-frontend-7bm6.onrender.com
4. Read USER_GUIDE.md

**Day 2 - Understand:**
1. Read this TEAM_HANDOVER.md
2. Read TECHNICAL_GUIDE.md (sections 1-4)
3. Explore API docs → https://seek-scraper-api.onrender.com/api/docs
4. Review config/config.yaml

**Day 3 - Practice:**
1. Clone repository locally
2. Run `./start.sh` (local testing)
3. Make a config change (add excluded company)
4. Deploy to Render (git push)

**Day 4 - Maintain:**
1. Run manual scrape
2. Export job data
3. Check system health
4. You're ready to maintain the system!

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| Nov 14, 2025 | Fixed Render deployment issues | Claude |
| Nov 13, 2025 | Deployed to Render | Team |
| Nov 11, 2025 | Created frontend dashboard | Team |
| Nov 8, 2025 | Initial scraper development | Team |

---

## 🔗 Quick Links Summary

| Resource | URL |
|----------|-----|
| **Live Dashboard** | https://jobscraper-frontend-7bm6.onrender.com |
| **API Docs** | https://seek-scraper-api.onrender.com/api/docs |
| **GitHub Repo** | https://github.com/JixuanYU0/JobScraperSeek |
| **Render Dashboard** | https://dashboard.render.com |

---

**Version:** 1.0.0
**Last Updated:** November 14, 2025
**Document Owner:** LiquidHR Technical Team
**Next Review:** December 14, 2025

---

**Questions?** Review the documentation guides or check the troubleshooting section above.

**Ready to take over?** Complete the handover checklist and you're good to go!
