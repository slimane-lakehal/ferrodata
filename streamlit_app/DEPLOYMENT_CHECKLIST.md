# Streamlit Cloud Deployment Checklist

Use this checklist before deploying to ensure everything is ready.

## Pre-Deployment Checklist

### Files & Configuration
- [ ] `requirements.txt` exists and includes all dependencies
- [ ] `packages.txt` created (even if empty)
- [ ] `.streamlit/config.toml` configured
- [ ] `.streamlit/secrets.toml` NOT committed to git
- [ ] `.streamlit/secrets.toml.example` created as template
- [ ] `.gitignore` updated to exclude secrets and database files
- [ ] `main.py` entry point works locally

### Database Strategy
- [ ] Decided on database approach:
  - [ ] Option A: Include sample database in git
  - [ ] Option B: Download database on startup
  - [ ] Option C: Use external database
- [ ] Database path updated in `database.py` if needed
- [ ] Test data loading works locally

### Code Quality
- [ ] App runs locally without errors: `uv run streamlit run main.py`
- [ ] All imports work correctly
- [ ] No hardcoded secrets or API keys
- [ ] Error handling in place for missing data
- [ ] Loading states for expensive operations

### GitHub
- [ ] Repository is public OR you have Streamlit Teams plan
- [ ] All changes committed to main branch
- [ ] GitHub Actions workflow added (`.github/workflows/streamlit-deploy.yml`)
- [ ] Repository pushed to GitHub

### Testing
- [ ] Test with fresh install using requirements.txt:
  ```bash
  python -m venv test_env
  source test_env/bin/activate
  pip install -r streamlit_app/requirements.txt
  streamlit run streamlit_app/main.py
  ```
- [ ] Verify all pages load
- [ ] Test all features work
- [ ] Check mobile responsiveness

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "feat: ready for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud
- [ ] Go to https://share.streamlit.io/
- [ ] Click "New app"
- [ ] Select repository: `slimane-lakehal/ferrodata`
- [ ] Set branch: `main`
- [ ] Set main file: `streamlit_app/main.py`
- [ ] Choose app URL
- [ ] Click "Deploy!"

### 3. Configure Secrets (if needed)
- [ ] Open app settings
- [ ] Add secrets in TOML format
- [ ] Save and reboot app

### 4. Verify Deployment
- [ ] App loads successfully
- [ ] All pages accessible
- [ ] Data displays correctly
- [ ] No errors in logs
- [ ] Test on different devices

## Post-Deployment

### Monitoring
- [ ] Check logs for errors
- [ ] Monitor performance
- [ ] Test all features in production
- [ ] Verify database connections work

### Documentation
- [ ] Update README with app URL
- [ ] Document any deployment-specific configuration
- [ ] Note any differences from local development

### Sharing
- [ ] Share app URL with stakeholders
- [ ] Add to portfolio/website
- [ ] Update GitHub repo description with live link

## Rollback Plan

If something goes wrong:

1. Check Streamlit Cloud logs for errors
2. Revert to previous commit if needed:
   ```bash
   git revert HEAD
   git push origin main
   ```
3. Streamlit Cloud will auto-redeploy from reverted commit

## Quick Commands

```bash
# Test locally
cd streamlit_app && uv run streamlit run main.py

# Check dependencies are correct
pip install -r streamlit_app/requirements.txt

# Validate app structure
test -f streamlit_app/main.py && echo "✓ main.py exists"
test -f streamlit_app/requirements.txt && echo "✓ requirements.txt exists"
test -d streamlit_app/.streamlit && echo "✓ .streamlit config exists"

# Push to GitHub
git add . && git commit -m "deploy: ready for production" && git push
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Module not found | Add to `requirements.txt` |
| Database not found | Implement data loading strategy |
| Secrets not found | Configure in Streamlit Cloud settings |
| App won't start | Check logs, verify `main.py` path |
| Slow performance | Add `@st.cache_data` decorators |

## Support Resources

- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io/
- Project Issues: https://github.com/slimane-lakehal/ferrodata/issues

---

✅ Once all items are checked, you're ready to deploy!
