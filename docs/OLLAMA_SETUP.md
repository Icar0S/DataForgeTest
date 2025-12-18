# Ollama Setup Guide

This guide explains how to configure DataForgeTest to use Ollama for LLM-powered features (RAG Support and Synthetic Data Generation) without costs.

## Overview

DataForgeTest now supports two LLM providers:
- **Ollama** (default): Open-source LLMs running locally - **NO COSTS**
- **Anthropic Claude**: Cloud-based LLM - requires API credits

## Quick Start with Ollama

### 1. Using Docker Compose (Recommended for Production)

The easiest way to get started is using Docker Compose, which automatically sets up Ollama:

```bash
# Start all services including Ollama
docker-compose up -d

# Pull the Qwen2.5-Coder model (or any other model)
docker-compose exec ollama ollama pull qwen2.5-coder:7b

# Verify Ollama is running
docker-compose exec ollama ollama list
```

The backend will automatically connect to Ollama at `http://ollama:11434`.

### 2. Local Development Setup

For local development, you can run Ollama separately:

#### Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [ollama.com/download](https://ollama.com/download)

#### Start Ollama and Pull a Model

```bash
# Start Ollama (runs on port 11434 by default)
ollama serve

# In another terminal, pull a model
ollama pull qwen2.5-coder:7b

# Or try other models:
# ollama pull llama3
# ollama pull codellama
# ollama pull mistral
```

#### Configure Environment Variables

Create or update your `.env` file:

```env
# LLM Provider Configuration
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434

# Other RAG settings
VECTOR_STORE_PATH=./storage/vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=4
```

## Recommended Models

### For Code Generation (PySpark, Synthetic Data):
- **qwen2.5-coder:7b** (Recommended) - Great for code, 7B parameters
- **codellama:7b** - Specialized for code generation
- **deepseek-coder:6.7b** - Alternative code-focused model

### For RAG/Chat:
- **qwen2.5-coder:7b** (Recommended) - Works well for both code and chat
- **llama3:8b** - Good general-purpose model
- **mistral:7b** - Fast and efficient

### Model Size Considerations:
- **7B models**: Good balance of performance and speed (4-8GB RAM)
- **13B models**: Better quality but slower (8-16GB RAM)
- **70B+ models**: Best quality but requires significant resources (40GB+ RAM)

## Switching Between Providers

### Switch to Ollama (Default):
```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
```

### Switch to Anthropic Claude:
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku-20240307
LLM_API_KEY=your-api-key-here
```

## Testing the Setup

### Test RAG System:
```bash
cd src
python -c "from rag.simple_rag import SimpleRAG; rag = SimpleRAG(); print(rag.chat('What is data quality?'))"
```

### Test Synthetic Data Generation:
Use the frontend at `http://localhost:3000` and navigate to "Synthetic Data Generation"

## Troubleshooting

### Ollama Connection Issues:

**Problem**: `Connection refused` or `Failed to connect to Ollama`

**Solutions**:
1. Verify Ollama is running: `ollama list`
2. Check the correct URL in `.env`:
   - Local: `http://localhost:11434`
   - Docker: `http://ollama:11434`
3. For Docker, ensure the backend service `depends_on: ollama`

### Model Not Found:

**Problem**: `Model 'qwen2.5-coder:7b' not found`

**Solution**: Pull the model first:
```bash
# Local
ollama pull qwen2.5-coder:7b

# Docker
docker-compose exec ollama ollama pull qwen2.5-coder:7b
```

### Slow Response Times:

**Solutions**:
1. Use a smaller model (e.g., `qwen2.5-coder:7b` instead of `qwen2.5-coder:72b`)
2. Ensure sufficient RAM is available
3. Use CPU/GPU acceleration if available

### Memory Issues:

**Solutions**:
1. Use smaller models (7B or 13B parameters)
2. Close other applications
3. Increase Docker memory limits in Docker Desktop settings

## Production Deployment on Render

For deploying on Render.com or similar platforms:

1. **Use Docker Compose** deployment option
2. **Set environment variables** in Render dashboard:
   ```
   LLM_PROVIDER=ollama
   LLM_MODEL=qwen2.5-coder:7b
   OLLAMA_BASE_URL=http://ollama:11434
   ```
3. **Resource requirements**: Choose a plan with at least 4GB RAM for 7B models

Note: Some cloud providers may not support running Ollama due to resource constraints. In such cases, you can:
- Use Anthropic Claude as a fallback
- Deploy Ollama on a separate server/VM and connect via URL
- Use managed LLM services like OpenAI with adapter code

## Performance Comparison

| Provider | Cost | Speed | Quality | Setup Complexity |
|----------|------|-------|---------|------------------|
| Ollama (7B) | Free | Medium | Good | Easy |
| Ollama (13B) | Free | Slow | Better | Easy |
| Claude Haiku | $$$ | Fast | Excellent | Very Easy |

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.com/library)
- [Qwen2.5-Coder Model](https://ollama.com/library/qwen2.5-coder)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
