# Troubleshooting Guide

## Backend Startup Issues

### OSError: [Errno 22] Invalid argument when importing anthropic

**Symptom:**
```
OSError: [Errno 22] Invalid argument
```
Error occurs during `import anthropic` when starting the backend.

**Root Cause:**
This is a Windows-specific issue related to reading `entry_points.txt` from package metadata. It can occur due to:
- Corrupted package installation
- Encoding issues in metadata files
- Compatibility issues between pydantic and anthropic versions

**Solution:**
The codebase has been updated to handle this gracefully:

1. **Lazy Import**: The `anthropic` library is now imported only when needed, inside the `SyntheticDataGenerator.__init__()` method.

2. **Error Handling**: Import errors (including `OSError`) are caught and logged, but don't prevent the backend from starting.

3. **Fallback Mode**: When anthropic cannot be imported, the synthetic data generation falls back to mock data mode.

**What This Means:**
- ✅ Backend starts successfully even if anthropic has import issues
- ✅ All other features (RAG, accuracy, chatbot) work normally
- ✅ Synthetic data generation works with mock data
- ⚠️ Real LLM-based synthetic data generation requires fixing anthropic installation

**To Fix Anthropic Import (Optional):**
If you want to use real LLM-based synthetic data generation:

1. Reinstall anthropic and pydantic:
   ```bash
   pip uninstall anthropic pydantic -y
   pip install anthropic pydantic --no-cache-dir
   ```

2. If the issue persists, try installing in a fresh virtual environment:
   ```bash
   python -m venv .venv_new
   .venv_new\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set your Anthropic API key in `.env`:
   ```
   LLM_API_KEY=your-api-key-here
   ```

## Startup Script Improvements

All startup scripts (`start_app.bat`, `setup_start.bat`, `dev_start.bat`) have been improved:

### Before:
- Used simple timeout (5-10 seconds)
- Started frontend immediately after timeout
- No verification that backend was actually ready

### After:
- Checks backend health endpoint every second
- Waits up to 30 seconds for backend to be ready
- Only starts frontend after backend confirms it's running
- Provides progress feedback during startup

**Benefits:**
- ✅ Frontend doesn't start before backend is ready
- ✅ More reliable startup sequence
- ✅ Better error messages if backend fails to start
- ✅ No race conditions between backend and frontend

## Running the Application

Use any of these scripts to start the application:

1. **First Time Setup:**
   ```bash
   setup_start.bat
   ```
   - Installs all dependencies
   - Waits for backend health check
   - Opens browser when everything is ready

2. **Quick Start (Development):**
   ```bash
   dev_start.bat
   ```
   - Skips dependency checks
   - Faster startup
   - Waits for backend health check

3. **Standard Start:**
   ```bash
   start_app.bat
   ```
   - Checks and installs missing dependencies
   - Waits for backend health check
   - Opens browser

All scripts now ensure the backend is fully initialized before starting the frontend.
