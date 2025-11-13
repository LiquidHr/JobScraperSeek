# Quick Reference Card

**LiquidHR Job Scraper - One-Page Cheat Sheet**

---

## 🔗 Essential Links

```
📊 Dashboard:  https://jobscraper-frontend-7bm6.onrender.com
📚 API Docs:   https://seek-scraper-api.onrender.com/api/docs
🔧 GitHub:     https://github.com/JixuanYU0/JobScraperSeek
☁️ Render:     https://dashboard.render.com
```

---

## ⚡ Quick Commands

### Check System Health
```bash
curl https://seek-scraper-api.onrender.com/api/v1/health
```

### Get Latest Jobs
```bash
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/latest?limit=5"
```

### Deploy Changes
```bash
git add .
git commit -m "Your changes"
git push origin main
# Auto-deploys in 5-10 min
```

### Run Scraper Manually
```bash
# On Render: Dashboard → seek-scraper-api → Shell
python main.py

# Locally:
./run_scraper.sh
```

---

## 📁 Key Files

| File | What It Does |
|------|--------------|
| `config/config.yaml` | Scraping rules & filters |
| `data/jobs.json` | Job database (622 jobs) |
| `render.yaml` | Deployment config |
| `src/api/app.py` | API endpoints |
| `frontend/src/App.jsx` | Dashboard UI |

---

## 🔧 Common Tasks

### 1. Add Excluded Company
```yaml
# Edit config/config.yaml
excluded_companies:
  - "New Company Name"
```
Then: `git add . && git commit -m "Exclude New Company" && git push`

### 2. Change Scrape Frequency
```yaml
# Edit config/config.yaml
scheduler:
  frequency_hours: 48  # Every 2 days
```

### 3. Adjust Job Retention
```yaml
# Edit config/config.yaml
deduplication:
  retention_days: 60  # Keep jobs for 60 days
```

### 4. Export Jobs
- **Via UI:** Dashboard → Export CSV button
- **Via API:** `curl "API_URL/api/v1/jobs/latest?limit=1000" > export.json`

---

## 🚨 Troubleshooting

### Dashboard shows 0 jobs
```bash
# Check API
curl "https://seek-scraper-api.onrender.com/api/v1/jobs/latest?limit=1"

# If empty, run scraper
# Render Dashboard → seek-scraper-api → Shell → python main.py
```

### Site is slow
**Cause:** Free tier sleeps after 15 min
**Fix:** Wait 60 sec for wake-up OR upgrade to paid ($7/mo)

### Deployment failed
```bash
# Check logs: Render Dashboard → Service → Logs
# Rollback: Render Dashboard → Manual Deploy → Previous commit
```

---

## 💰 Costs

| Plan | Cost | Status |
|------|------|--------|
| **Current (Free)** | $0/mo | ✅ Active |
| Services sleep after 15 min | - | ⚠️ Limitation |
| **Recommended (Paid)** | $7/mo | Always-on |

**Upgrade:** Render Dashboard → Service → Upgrade

---

## 📊 Stats

- **Current Jobs:** 622
- **Retention:** 30 days
- **Scrape Frequency:** Every 3 days (manual trigger)
- **Excluded Companies:** 58+
- **Storage:** JSON file (~5 MB)

---

## 🆘 Need Help?

| Question | See Document |
|----------|--------------|
| How to use dashboard? | USER_GUIDE.md |
| How does it work? | TECHNICAL_GUIDE.md |
| How to deploy? | DEPLOYMENT_GUIDE.md |
| Complete handover? | TEAM_HANDOVER.md |
| This page! | QUICK_REFERENCE.md |

---

## ✅ Health Check Checklist

- [ ] Dashboard loads: https://jobscraper-frontend-7bm6.onrender.com
- [ ] Jobs display (should see 622+)
- [ ] Search works
- [ ] CSV export works
- [ ] API health: `curl API_URL/api/v1/health`

---

## 🔐 Access Needed

- [ ] GitHub: https://github.com/JixuanYU0/JobScraperSeek
- [ ] Render: https://dashboard.render.com

---

**Print this page and keep it handy!**

**Last Updated:** Nov 14, 2025
