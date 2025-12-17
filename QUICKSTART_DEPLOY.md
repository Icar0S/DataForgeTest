# Quick Deployment Guide for DataForgeTest

This guide provides step-by-step instructions to deploy both frontend and backend.

## 📊 Current Status

- ✅ **Frontend**: Already deployed on Vercel
  - URL: https://data-forge-test.vercel.app/
  - Status: Running
  
- ⚙️ **Backend**: Needs deployment
  - Docker configuration: ✅ Ready
  - Deployment options: Multiple platforms supported

## 🚀 Deploy Backend (Choose One Method)

### Method 1: Render.com (Easiest - Recommended)

1. **Sign up at Render.com** (free tier available)
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `Icar0S/DataForgeTest`
   - Render automatically detects the Dockerfile ✨

3. **Configure Service**
   - Name: `dataforgetest-backend`
   - Region: Choose closest to your users
   - Branch: `main` (or your preferred branch)
   - Dockerfile path should be auto-detected

4. **Set Environment Variables** (optional but recommended)
   - Click "Advanced"
   - Add environment variable:
     - Key: `LLM_API_KEY`
     - Value: Your Anthropic API key
   - Note: Backend works without API key for basic features

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build and deployment
   - **Copy your backend URL**: `https://dataforgetest-backend.onrender.com`

### Method 2: Railway.app (Also Easy)

1. **Sign up at Railway.app**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `Icar0S/DataForgeTest`

3. **Configure**
   - Railway auto-detects Dockerfile
   - Add variables if needed (Variables tab)
   - Generate domain (Settings → Generate Domain)

4. **Deploy**
   - Railway builds and deploys automatically
   - **Copy your backend URL**: `https://dataforgetest-backend.up.railway.app`

### Method 3: Docker (Self-Hosted)

If you have a server or VPS:

```bash
# Clone repository
git clone https://github.com/Icar0S/DataForgeTest.git
cd DataForgeTest

# Build and run with Docker Compose
docker compose up -d

# Or with Docker directly
docker build -t dataforgetest-backend .
docker run -d -p 5000:5000 dataforgetest-backend
```

Access at: `http://your-server-ip:5000`

## 🔗 Connect Frontend to Backend

After deploying the backend, you need to connect the Vercel frontend to it.

### Quick Method: Vercel Rewrites

1. **Create `vercel.json` in frontend directory**

```bash
cd frontend
cp vercel.json.example vercel.json
```

2. **Edit `vercel.json`** and replace `REPLACE_WITH_YOUR_BACKEND_URL`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://dataforgetest-backend.onrender.com/api/:path*"
    },
    {
      "source": "/ask",
      "destination": "https://dataforgetest-backend.onrender.com/ask"
    }
  ]
}
```

3. **Commit and push**

```bash
git add vercel.json
git commit -m "Connect frontend to deployed backend"
git push
```

Vercel will automatically redeploy! ✨

## ✅ Verify Deployment

### Test Backend

```bash
# Health check
curl https://your-backend-url.com/

# Expected response:
# {"status": "Backend is running", "message": "Data Quality Chatbot API"}

# Test individual services
curl https://your-backend-url.com/api/synth/health
curl https://your-backend-url.com/api/accuracy/health
curl https://your-backend-url.com/api/rag/health
```

### Test Frontend

1. Visit https://data-forge-test.vercel.app/
2. Open Browser DevTools (F12) → Network tab
3. Try a feature (e.g., "Generate Dataset")
4. Verify API requests go to your backend URL
5. Check Console tab for errors

## 🐛 Troubleshooting

### Backend won't start

**Check logs:**
- Render: Dashboard → Logs
- Railway: Deployments → View Logs

**Common issues:**
- Build timeout: Increase timeout in platform settings
- Out of memory: Upgrade to paid tier or reduce workers

### Frontend can't connect

**CORS errors:**
- Backend already has CORS enabled
- Make sure you're using HTTPS (not HTTP)
- Check backend URL is correct in `vercel.json`

**404 errors:**
- Verify backend is running
- Check `vercel.json` syntax
- Ensure Vercel redeployed after changes

### API requests timeout

**Solutions:**
- Increase timeout in backend Dockerfile (default: 120s)
- Check backend logs for errors
- Verify backend has adequate resources

## 📚 Additional Resources

- **Full Deployment Guide**: `docs/DEPLOYMENT.md`
- **Docker Guide**: `DOCKER.md`
- **Frontend API Config**: `docs/FRONTEND_API_CONFIG.md`
- **Frontend-Backend Connection**: `docs/FRONTEND_BACKEND_CONNECTION.md`

## 🎯 Summary Checklist

Backend Deployment:
- [ ] Backend deployed to Render/Railway/other platform
- [ ] Backend URL accessible and returns health check
- [ ] Environment variables configured (if using LLM features)

Frontend Connection:
- [ ] Created `frontend/vercel.json` with backend URL
- [ ] Committed and pushed changes
- [ ] Vercel redeployed automatically
- [ ] API requests working from frontend
- [ ] No CORS or connection errors

Testing:
- [ ] Frontend loads correctly
- [ ] Can generate synthetic data
- [ ] Can upload files for accuracy check
- [ ] Chatbot/RAG features work
- [ ] All health endpoints return OK

## 🆘 Need Help?

- **Issues**: https://github.com/Icar0S/DataForgeTest/issues
- **Documentation**: Check `/docs` directory
- **Platform Support**:
  - Render: https://render.com/docs
  - Railway: https://docs.railway.app
  - Vercel: https://vercel.com/docs

## 🎉 You're Done!

Your DataForgeTest application should now be fully deployed and operational!

- Frontend: https://data-forge-test.vercel.app/
- Backend: https://your-backend-url.com/

Enjoy your deployed application! 🚀
