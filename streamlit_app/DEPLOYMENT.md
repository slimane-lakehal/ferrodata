# Streamlit Community Cloud Deployment Guide

This guide explains how to deploy the Ferrodata app to Streamlit Community Cloud with automated CI/CD.

## Prerequisites

- GitHub account with the repository pushed
- Streamlit Community Cloud account (free at https://share.streamlit.io)
- Data pipeline already run (ferrodata.duckdb created)

## Important Note: Database Handling

⚠️ **The DuckDB database file (`ferrodata.duckdb`) is gitignored and will NOT be deployed.**

You have two options:

### Option 1: Include Sample/Static Database (Recommended for Demo)
1. Create a smaller sample database for the deployed app
2. Place it in `streamlit_app/data/ferrodata_sample.duckdb`
3. Update `database.py` to use this path in production

### Option 2: Use External Database (Production)
1. Export your data to a cloud database (PostgreSQL, BigQuery, etc.)
2. Update connection settings in Streamlit secrets
3. Modify `database.py` to connect to external DB

## Deployment Steps

### 1. Prepare Your Repository

Ensure these files are committed:

```bash
streamlit_app/
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── packages.txt                # System dependencies (optional)
├── .streamlit/
│   ├── config.toml            # App configuration
│   └── secrets.toml.example   # Secrets template (don't commit actual secrets!)
└── src/                        # Your app code
```

### 2. Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "feat: prepare Streamlit Cloud deployment"

# Push to main branch
git push origin main
```

### 3. Deploy on Streamlit Community Cloud

1. **Go to https://share.streamlit.io/**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure:**
   - **Repository:** `slimane-lakehal/ferrodata`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/main.py`
   - **App URL:** Choose a custom URL (e.g., `ferrodata-analytics`)

5. **Click "Deploy!"**

### 4. Configure Secrets (if needed)

If your app needs secrets (API keys, database credentials):

1. In your deployed app dashboard, click **"Settings"** (⚙️)
2. Click **"Secrets"** in the left sidebar
3. Add your secrets in TOML format:

```toml
# Example secrets
[database]
host = "your-db-host.com"
username = "your-username"
password = "your-password"

[api]
mapbox_token = "your-mapbox-token"
```

4. Click **"Save"**

### 5. Handle the Database

Since `ferrodata.duckdb` is gitignored, you need to handle data:

**Option A: Create a data loading script**

Create `streamlit_app/src/ferrodata_delays_analysis/utils/load_data.py`:

```python
import streamlit as st
import requests

@st.cache_resource
def download_sample_data():
    """Download sample database from external source."""
    # Upload your duckdb to GitHub Releases, Google Drive, etc.
    url = "https://github.com/slimane-lakehal/ferrodata/releases/download/v1.0/ferrodata_sample.duckdb"
    response = requests.get(url)

    with open("ferrodata_sample.duckdb", "wb") as f:
        f.write(response.content)

    return "ferrodata_sample.duckdb"
```

**Option B: Use static data**

Include a small sample in git by creating an exception in `.gitignore`:

```gitignore
# DuckDB
*.duckdb
!streamlit_app/data/ferrodata_sample.duckdb
```

## CI/CD Workflow

The GitHub Actions workflow (`.github/workflows/streamlit-deploy.yml`) automatically:

1. ✅ **Tests** the app on every push to main
2. ✅ **Lints** code with ruff
3. ✅ **Validates** app structure
4. ✅ **Notifies** when ready to deploy

Streamlit Cloud **automatically redeploys** when you push to the `main` branch.

## Monitoring Your Deployment

### Check Deployment Status
- Go to https://share.streamlit.io/
- Click on your app
- View logs in real-time

### Common Issues

#### App won't start
- Check logs for missing dependencies
- Verify `requirements.txt` includes all packages
- Ensure `main.py` path is correct

#### Database not found
- Remember: `.duckdb` files are gitignored
- Implement data loading strategy (see above)
- Check file paths are correct

#### Import errors
- Verify Python path configuration in `main.py`
- Check that `src/` directory structure is correct
- Ensure all `__init__.py` files exist

### Environment Variables

Access secrets in your code:

```python
import streamlit as st

# Access secrets
db_host = st.secrets["database"]["host"]
api_key = st.secrets["api"]["mapbox_token"]
```

## Update Workflow

To update your deployed app:

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main

# Streamlit Cloud automatically redeploys!
# GitHub Actions runs tests
```

## Custom Domain (Optional)

To use a custom domain:

1. Go to app settings on Streamlit Cloud
2. Click "General"
3. Add your custom domain
4. Update DNS records as instructed

## Performance Optimization

- ✅ Use `@st.cache_data` for expensive computations
- ✅ Use `@st.cache_resource` for database connections
- ✅ Limit data loaded on initial page load
- ✅ Use pagination for large datasets
- ✅ Optimize queries to return only needed columns

## Security Best Practices

- ❌ Never commit `secrets.toml` to git
- ❌ Never hardcode API keys or passwords
- ✅ Use Streamlit secrets for sensitive data
- ✅ Keep `.gitignore` up to date
- ✅ Use environment-specific configurations

## Useful Commands

```bash
# Test locally before deploying
cd streamlit_app
uv run streamlit run main.py

# Check app works with requirements.txt
pip install -r requirements.txt
streamlit run main.py

# Validate GitHub Actions locally (with act)
act push

# View app logs
# Visit: https://share.streamlit.io/ → Your App → View logs
```

## Troubleshooting

### Error: "Module not found"
- Add missing package to `requirements.txt`
- Push changes to trigger redeploy

### Error: "Database connection failed"
- Check secrets are configured correctly
- Verify database is accessible from Streamlit Cloud IPs

### App is slow
- Check query performance
- Add caching where appropriate
- Reduce data loaded on startup

## Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** https://github.com/slimane-lakehal/ferrodata/issues

## Next Steps

After deployment:

1. ✅ Test all features in production
2. ✅ Monitor performance and logs
3. ✅ Set up error tracking (optional)
4. ✅ Share your app URL!
5. ✅ Gather user feedback

Your app will be live at:
`https://share.streamlit.io/slimane-lakehal/ferrodata/main/streamlit_app/main.py`

Or custom URL:
`https://ferrodata-analytics.streamlit.app`
