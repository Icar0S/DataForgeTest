# Docker Quick Start Guide

This guide provides quick steps to get the DataForgeTest backend running using Docker.

## Prerequisites

- Docker Desktop or Docker Engine installed
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### Option 1: Docker Run (Simple)

```bash
# Build the image
docker build -t dataforgetest-backend .

# Run the container
docker run -d \
  --name dataforgetest-backend \
  -p 5000:5000 \
  -v $(pwd)/storage:/app/storage \
  dataforgetest-backend

# Check if it's running
curl http://localhost:5000/
```

### Option 2: Docker Compose (Recommended)

```bash
# Start the backend
docker compose up -d

# View logs
docker compose logs -f backend

# Stop the backend
docker compose down
```

## Verify Deployment

Test the API endpoints:

```bash
# Main health check
curl http://localhost:5000/

# Synthetic data service
curl http://localhost:5000/api/synth/health

# Data accuracy service
curl http://localhost:5000/api/accuracy/health

# RAG service
curl http://localhost:5000/api/rag/health
```

## Environment Variables

To configure the backend, create a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your configuration
nano .env
```

Key variables:
- `LLM_API_KEY` - Your Anthropic API key (optional for basic features)
- `FLASK_ENV` - Set to `production` for deployment
- `SYNTH_MAX_ROWS` - Maximum rows for synthetic data generation

## Connecting Frontend

After deploying the backend, update your frontend configuration:

1. **Vercel Deployment**: Add environment variable `REACT_APP_API_URL=https://your-backend-url.com`
2. **Local Development**: Update `frontend/package.json` proxy to your backend URL

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs dataforgetest-backend

# Check if port 5000 is already in use
lsof -i :5000
```

### API returns errors
```bash
# Check container logs
docker compose logs backend

# Verify environment variables
docker compose config
```

### High memory usage
- Reduce `SYNTH_MAX_ROWS` in environment variables
- Decrease number of workers in Dockerfile (default is 4)

## Next Steps

- See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for cloud deployment options
- See [README.md](README.md) for full documentation
- Configure environment variables for production use

## Support

For issues or questions:
- GitHub Issues: https://github.com/Icar0S/DataForgeTest/issues
- Documentation: `/docs` directory
