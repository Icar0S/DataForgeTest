# Frontend-Backend Connection Guide

This guide explains how to connect the deployed frontend (https://data-forge-test.vercel.app/) to your deployed backend.

## Current Frontend Setup

The frontend is already deployed on Vercel at:
- **URL**: https://data-forge-test.vercel.app/

## Backend Deployment

Choose one of these deployment options for the backend:

### Recommended: Render.com (Easiest)

1. **Create a Render account** at https://render.com
2. **Create a new Web Service**
   - Connect your GitHub repository
   - Render will automatically detect the Dockerfile
3. **Configure Environment Variables**
   - Go to Environment tab
   - Add `LLM_API_KEY` with your Anthropic API key (if needed)
   - Other variables will use defaults from `.env.example`
4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Note your backend URL (e.g., `https://dataforgetest-backend.onrender.com`)

### Alternative: Railway.app

1. **Create a Railway account** at https://railway.app
2. **Create a new Project**
   - Select "Deploy from GitHub repo"
   - Connect your repository
   - Railway will detect the Dockerfile automatically
3. **Add Environment Variables**
   - Click on your service → Variables
   - Add variables from `.env.example`
   - Set `LLM_API_KEY` if using AI features
4. **Generate Domain**
   - Go to Settings → Generate Domain
   - Note your backend URL (e.g., `https://your-app.up.railway.app`)

### Alternative: Google Cloud Run

```bash
# Configure gcloud
gcloud config set project YOUR_PROJECT_ID

# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/dataforgetest-backend

# Deploy
gcloud run deploy dataforgetest-backend \
  --image gcr.io/YOUR_PROJECT_ID/dataforgetest-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_API_KEY=your-key

# Note the service URL from output
```

## Connecting Frontend to Backend

After deploying the backend, you need to update the frontend configuration on Vercel.

### Method 1: Environment Variables (Recommended if frontend uses REACT_APP_API_URL)

1. **Go to Vercel Dashboard**
   - Navigate to your project: https://vercel.com/dashboard
   - Select the "data-forge-test" project

2. **Add Environment Variable**
   - Go to Settings → Environment Variables
   - Add new variable:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://your-backend-url.com` (without trailing slash)
   - Select all environments (Production, Preview, Development)
   - Click "Save"

3. **Redeploy Frontend**
   - Go to Deployments tab
   - Find the latest deployment
   - Click the three dots menu → Redeploy
   - Select "Redeploy"

### Method 2: Update Package.json Proxy (If frontend uses proxy)

If the frontend relies on the `proxy` setting in `package.json`:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Icar0S/DataForgeTest.git
   cd DataForgeTest/frontend
   ```

2. **Update package.json**
   ```json
   {
     "proxy": "https://your-backend-url.com"
   }
   ```

3. **Commit and push changes**
   ```bash
   git add package.json
   git commit -m "Update backend URL"
   git push
   ```

4. **Vercel will auto-deploy** the changes

### Method 3: Update Frontend Code Directly

If API calls are hardcoded in the frontend:

1. **Find API configuration file**
   - Usually in `frontend/src/config.js` or similar
   - Or search for `localhost:5000` in the codebase

2. **Update the API URL**
   ```javascript
   // Before
   const API_URL = 'http://localhost:5000';
   
   // After
   const API_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.com';
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Configure production backend URL"
   git push
   ```

## Verify the Connection

After updating the frontend:

1. **Visit the frontend**: https://data-forge-test.vercel.app/

2. **Open browser DevTools** (F12)

3. **Check Network tab**
   - Look for API requests
   - Verify they're going to your backend URL
   - Check for CORS errors

4. **Test a feature**
   - Try the PySpark code generation
   - Or upload a file for data accuracy check
   - Verify the backend responds correctly

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

The backend already has CORS enabled for all origins. If you want to restrict it:

1. Edit `src/api.py` on the backend:
   ```python
   from flask_cors import CORS
   
   CORS(app, resources={
       r"/*": {
           "origins": ["https://data-forge-test.vercel.app"]
       }
   })
   ```

2. Redeploy the backend

### Frontend can't connect to backend

1. **Check backend is running**
   ```bash
   curl https://your-backend-url.com/
   # Should return: {"status": "Backend is running", ...}
   ```

2. **Check environment variables on Vercel**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Verify `REACT_APP_API_URL` is set correctly

3. **Check browser console**
   - Open DevTools → Console
   - Look for error messages
   - Check Network tab for failed requests

### API requests timeout

1. **Increase timeout on backend**
   - Edit `Dockerfile` and increase `--timeout` value
   - Default is 120 seconds

2. **Check backend logs**
   ```bash
   # Render.com: View logs in dashboard
   # Railway: Check Deployments → Logs
   # Cloud Run: Use Google Cloud Console
   ```

## Environment Variables Reference

### Frontend (Vercel)
| Variable | Value | Required |
|----------|-------|----------|
| `REACT_APP_API_URL` | Your backend URL | Yes* |

*Required if frontend uses environment variables for API URL

### Backend (Render/Railway/Cloud Run)
| Variable | Default | Required |
|----------|---------|----------|
| `LLM_API_KEY` | - | No** |
| `FLASK_ENV` | production | No |
| `FLASK_DEBUG` | False | No |
| `SYNTH_MAX_ROWS` | 1000000 | No |
| `ACCURACY_MAX_UPLOAD_MB` | 50 | No |

**Some features work without API key

## Testing the Deployment

### 1. Test Backend Health

```bash
# Main health check
curl https://your-backend-url.com/

# Module health checks
curl https://your-backend-url.com/api/synth/health
curl https://your-backend-url.com/api/accuracy/health
curl https://your-backend-url.com/api/rag/health
```

### 2. Test Frontend

1. Visit https://data-forge-test.vercel.app/
2. Navigate to different pages
3. Try generating synthetic data
4. Upload a file for accuracy check
5. Test the chatbot interface

### 3. Check Logs

**Frontend (Vercel)**
- Vercel Dashboard → Deployments → View Function Logs

**Backend (Render.com)**
- Render Dashboard → Your Service → Logs

**Backend (Railway)**
- Railway Dashboard → Deployments → Logs

## Next Steps

After successful connection:

1. **Monitor performance**
   - Check response times
   - Monitor memory usage
   - Set up alerts for errors

2. **Configure custom domain** (optional)
   - Frontend: Vercel → Settings → Domains
   - Backend: Your platform's custom domain settings

3. **Set up SSL certificates**
   - Most platforms handle this automatically
   - Verify HTTPS is working

4. **Enable monitoring**
   - Set up uptime monitoring (e.g., UptimeRobot)
   - Configure error tracking (e.g., Sentry)

## Support

For issues:
- **GitHub Issues**: https://github.com/Icar0S/DataForgeTest/issues
- **Documentation**: See `/docs` directory
- **Deployment Guide**: See `docs/DEPLOYMENT.md`

## Summary Checklist

- [ ] Backend deployed to Render/Railway/Cloud Run
- [ ] Backend URL noted and accessible
- [ ] Frontend environment variable set on Vercel
- [ ] Frontend redeployed with new configuration
- [ ] Connection tested and working
- [ ] All features functioning correctly
- [ ] Monitoring and alerts configured
