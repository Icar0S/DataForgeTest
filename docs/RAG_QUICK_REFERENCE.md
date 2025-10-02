# RAG System Quick Reference

## 🚨 Problem: Chat Not Responding

**Symptoms:**
- Support page loads but chat doesn't respond
- No error messages shown
- Messages sent but no reply

**Quick Fix:**

### Option 1: Enable LLM (Recommended for real AI)
```bash
# 1. Get API key from https://console.anthropic.com/
# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your key
LLM_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# 4. Install dependencies
pip install llama-index-llms-anthropic llama-index-embeddings-openai llama-index-core

# 5. Edit src/api.py line 12:
# Change: from rag.routes_simple import rag_bp
# To:     from rag.routes import rag_bp

# 6. Restart backend
```

### Option 2: Use Simple RAG (Current System)
```bash
# 1. Upload a document
curl -X POST http://localhost:5000/api/rag/upload \
  -F "file=@your-document.txt"

# 2. Ask questions about the document content
# Note: Only finds keywords, not AI-powered
```

## 🧪 Quick Tests

### Test if system is working:
```bash
python tests/test_rag_diagnostics.py
```

### Test backend functionality:
```bash
python tests/test_rag_integration.py
```

### Test API endpoints:
```bash
python tests/test_rag_api.py
```

## 📊 System Status

### Check Backend Running:
```bash
curl http://localhost:5000/api/rag/health
```

**Expected Response:**
```json
{"status": "ok", "message": "RAG service is running"}
```

### Check Documents:
```bash
curl http://localhost:5000/api/rag/sources
```

### Test Chat:
```bash
curl -X POST http://localhost:5000/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is data quality?"}'
```

## 🔍 Understanding Current System

| What You Have | What It Does | What It Doesn't Do |
|--------------|--------------|-------------------|
| Simple RAG | Keyword search in documents | ❌ AI understanding |
| Template responses | Extracts matching text | ❌ Generate new text |
| Citation system | Shows sources | ❌ Semantic search |
| EventSource streaming | Streams words | ❌ Context awareness |

## 🎯 Which System Are You Using?

### Check your api.py:
```bash
grep "routes" src/api.py
```

**Output:**
- `from rag.routes_simple import rag_bp` → Simple RAG (no LLM)
- `from rag.routes import rag_bp` → Full LLM RAG

## 🛠️ Common Issues

### Issue: "Connection error"
**Fix:** Backend not running
```bash
cd src
python api.py
```

### Issue: "No response"
**Fix:** No documents (Simple RAG) or no API key (LLM RAG)
```bash
# For Simple RAG:
curl -X POST http://localhost:5000/api/rag/upload -F "file=@doc.txt"

# For LLM RAG:
# Add LLM_API_KEY to .env
```

### Issue: "Module not found"
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "PySpark not installed"
**Fix:** Not needed for RAG (only for data quality testing)
```bash
pip install pyspark  # Only if needed for other features
```

## 📚 Documentation

- 📖 **Full Analysis:** `docs/RAG_ANALYSIS_SUMMARY.md`
- 🔧 **Troubleshooting:** `docs/RAG_TROUBLESHOOTING.md`
- 🧪 **Test Guide:** `tests/README_TESTS.md`
- ⚙️ **Configuration:** `.env.example`

## 🏃 Quick Start Commands

### Start Fresh:
```bash
# 1. Install everything
pip install -r requirements.txt

# 2. Run diagnostics
python tests/test_rag_diagnostics.py

# 3. Start backend
cd src && python api.py

# 4. In another terminal, start frontend
cd frontend/frontend && npm start

# 5. Open http://localhost:3000
```

### Debug Mode:
```bash
# Run all tests
python tests/test_rag_integration.py && \
python tests/test_rag_api.py && \
python tests/test_rag_diagnostics.py
```

## 💰 Cost Estimate (if using LLM)

| Usage | Cost |
|-------|------|
| 10 queries/day | ~$3-5/month |
| 100 queries/day | ~$30-50/month |
| 1000 queries/day | ~$300-500/month |

**Note:** Simple RAG is **FREE** (no API costs)

## ⚡ Performance

### Simple RAG (Current):
- ⚡ Instant responses
- 💾 No API calls
- 📊 Keyword matching only

### LLM RAG (Claude):
- 🤖 1-3 second responses
- 💰 API costs per query
- 🧠 AI understanding

## 🔐 Security

### API Keys:
- ✅ Store in `.env` file
- ✅ Never commit to git
- ✅ Add `.env` to `.gitignore`

### .gitignore check:
```bash
grep ".env" .gitignore || echo ".env" >> .gitignore
```

## 📞 Help

If stuck:
1. Run: `python tests/test_rag_diagnostics.py`
2. Read output carefully
3. Check `docs/RAG_TROUBLESHOOTING.md`
4. Look at backend/frontend console logs

## 🎓 Learning Path

1. ✅ **Understand current system** (Simple RAG)
2. ✅ **Run tests** to verify it works
3. ➡️ **Decide:** Keep Simple or switch to LLM?
4. ➡️ **Follow setup** for chosen option
5. ➡️ **Test** thoroughly
6. ➡️ **Monitor** in production

## 📝 Checklist

Before asking for help, verify:
- [ ] Backend is running (`curl http://localhost:5000/api/rag/health`)
- [ ] Frontend is running (`http://localhost:3000`)
- [ ] Tests pass (`python tests/test_rag_diagnostics.py`)
- [ ] Documents uploaded (Simple RAG) or API key set (LLM)
- [ ] Checked browser console for errors
- [ ] Checked backend terminal for errors
- [ ] Read troubleshooting guide

## 🚀 Production Checklist

Before deploying:
- [ ] All tests pass
- [ ] `.env` configured properly
- [ ] API keys secured
- [ ] Error handling tested
- [ ] Cost monitoring set up (if using LLM)
- [ ] Backup/restore strategy for documents
- [ ] Load testing completed
- [ ] User documentation updated

---

**Quick Summary:**
- Current system = Simple keyword search (NO AI)
- To get AI responses = Add Claude API key + switch routes
- All tests pass = System works correctly
- See full docs for detailed instructions
