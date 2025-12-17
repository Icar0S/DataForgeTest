# Frontend API Configuration Update Guide

This guide explains how to update the frontend code to use the centralized API configuration.

## Overview

The frontend has been configured to work seamlessly in both development and production:

- **Development**: Uses proxy in `package.json` → `http://localhost:5000`
- **Production**: Uses environment variable `REACT_APP_API_URL` → Your deployed backend

## Configuration Files

### 1. API Configuration (`src/config/api.js`)

This file provides helper functions to generate API URLs:

```javascript
import { getApiUrl } from './config/api';

// Before
const response = await fetch('/api/synth/health');

// After (recommended)
const response = await fetch(getApiUrl('api/synth/health'));
```

### 2. Environment Variables (`.env.example`)

Copy this file to create your local `.env`:

```bash
cd frontend
cp .env.example .env
```

For production (Vercel), set:
```
REACT_APP_API_URL=https://your-backend-url.com
```

## Current State

The frontend already uses relative URLs (`/api/...`), which works with:
- **Development**: `package.json` proxy routes to `localhost:5000`
- **Production on Vercel**: Needs backend URL configuration

## Deployment Options

### Option 1: Use Vercel Environment Variables (Recommended)

This is the easiest option - no code changes needed!

1. **Deploy backend** (Render, Railway, etc.)
2. **Configure Vercel**:
   - Go to https://vercel.com/dashboard
   - Select your project → Settings → Environment Variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.com`
   - Redeploy the frontend

**How it works**: Since the frontend uses relative URLs and Vercel doesn't have a proxy, you need to configure the backend URL. However, the current setup might require code changes to use the environment variable.

### Option 2: Update Frontend Code to Use API Config

To make the frontend use the API configuration system, update the fetch calls:

**Example Update for `GenerateDataset.js`:**

```javascript
// Add this import at the top
import { getApiUrl } from '../config/api';

// Update fetch calls
// Before:
const response = await fetch('/api/synth/preview', {

// After:
const response = await fetch(getApiUrl('api/synth/preview'), {
```

**Files to update** (for maximum compatibility):
- `src/pages/AdvancedPySparkGenerator.js`
- `src/pages/ChecklistPage.js`
- `src/pages/DatasetMetrics.js`
- `src/pages/GenerateDataset.js`
- `src/pages/TestDatasetGold.js`
- `src/components/ChatWindow.js`

### Option 3: Configure Vercel Rewrites (Alternative)

Instead of changing code, configure Vercel to proxy API requests:

1. Create `vercel.json` in the frontend directory:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/api/:path*"
    }
  ]
}
```

2. Commit and push to deploy

This way, the frontend code doesn't need changes, and `/api/*` requests are automatically routed to your backend.

## Recommended Approach

**For the current situation** (frontend already deployed on Vercel):

1. **Deploy the backend** to Render/Railway/Cloud Run
2. **Create `vercel.json`** with rewrites configuration (Option 3 above)
3. **Commit and push** to trigger Vercel redeploy
4. **Test** that everything works

This approach requires minimal changes and keeps the frontend code environment-agnostic.

## Step-by-Step Implementation

### Step 1: Deploy Backend

Follow the instructions in `DOCKER.md` or `docs/DEPLOYMENT.md` to deploy the backend. Note the URL.

### Step 2: Create Vercel Configuration

Create `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-BACKEND-URL.com/api/:path*"
    },
    {
      "source": "/ask",
      "destination": "https://YOUR-BACKEND-URL.com/ask"
    }
  ]
}
```

Replace `YOUR-BACKEND-URL.com` with your actual backend URL.

### Step 3: Update .gitignore (if needed)

Ensure `.env` is in `.gitignore`:

```bash
# In frontend/.gitignore
.env
.env.local
.env.production.local
```

### Step 4: Commit and Deploy

```bash
cd frontend
git add vercel.json
git commit -m "Configure Vercel to proxy API requests to backend"
git push
```

Vercel will automatically redeploy with the new configuration.

### Step 5: Test

1. Visit https://data-forge-test.vercel.app/
2. Open DevTools → Network tab
3. Try a feature (e.g., generate synthetic data)
4. Verify API requests are going to your backend URL
5. Check for errors in Console

## Troubleshooting

### API calls fail with 404

**Issue**: Vercel can't find the API endpoint

**Solution**: 
- Verify `vercel.json` has correct backend URL
- Check backend is running: `curl https://your-backend-url.com/`
- Redeploy Vercel after changes

### CORS errors

**Issue**: Backend rejects requests from frontend domain

**Solution**: The backend already has CORS enabled for all origins. If you still see errors:
1. Check backend logs
2. Verify the request is reaching the backend
3. Ensure HTTPS is used (not HTTP)

### Environment variable not working

**Issue**: `REACT_APP_API_URL` is not being used

**Solution**: 
- Use `vercel.json` rewrites instead (easier)
- Or update code to use `getApiUrl()` helper
- Remember: Environment variables must start with `REACT_APP_`

### Requests timeout

**Issue**: API requests take too long

**Solution**:
- Increase timeout in backend (Dockerfile)
- Check backend logs for errors
- Verify backend has enough resources

## Testing Locally

To test the configuration locally:

1. **Set up local environment**:
```bash
cd frontend
cp .env.example .env
# Leave REACT_APP_API_URL empty for development
```

2. **Start backend** (in one terminal):
```bash
cd src
python api.py
```

3. **Start frontend** (in another terminal):
```bash
cd frontend
npm start
```

4. **Test**: Visit http://localhost:3000 and try features

## Vercel Configuration Reference

### Basic Rewrites

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://backend.com/api/:path*"
    }
  ]
}
```

### With Environment Variables

```json
{
  "env": {
    "REACT_APP_API_URL": "@api-url"
  },
  "build": {
    "env": {
      "REACT_APP_API_URL": "@api-url"
    }
  }
}
```

Then set `@api-url` in Vercel dashboard.

## Next Steps

After successful deployment:

1. **Monitor performance**
   - Check Vercel Analytics
   - Monitor backend response times

2. **Set up error tracking**
   - Consider Sentry or similar
   - Monitor API errors

3. **Configure custom domain**
   - Both frontend and backend
   - Use same domain with subdomains (optional)

4. **Enable caching**
   - Configure Vercel edge caching
   - Add cache headers on backend

## Summary

**Quick deployment checklist**:

- [ ] Backend deployed and URL noted
- [ ] Created `frontend/vercel.json` with rewrites
- [ ] Committed and pushed changes
- [ ] Vercel automatically redeployed
- [ ] Tested all features work
- [ ] No CORS errors
- [ ] API requests successful

## Support

For issues:
- **GitHub Issues**: https://github.com/Icar0S/DataForgeTest/issues
- **Vercel Docs**: https://vercel.com/docs/configuration
- **Deployment Guide**: See `docs/DEPLOYMENT.md`
