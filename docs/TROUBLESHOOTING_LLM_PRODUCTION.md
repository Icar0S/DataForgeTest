# 🔍 Diagnóstico: LLM não está funcionando em Produção

## ❌ Problema Identificado

As respostas do chat estão usando **templates básicos** em vez da **LLM inteligente**.

## 🔎 Causa Raiz

O sistema tem esta lógica de fallback:

```python
# Em SimpleChatEngine.__init__
self.llm_client = get_default_llm_client()
self.use_llm = self.llm_client is not None  # ← Se None, usa templates

# Em get_default_llm_client()
try:
    return create_llm_client()
except (ValueError, ImportError) as e:
    print(f"⚠️  Could not initialize LLM client: {e}")
    return None  # ← Retorna None se falhar
```

**Quando retorna None:**
1. ✅ Variáveis de ambiente não configuradas
2. ✅ Pacote `google-generativeai` não instalado
3. ✅ API key inválida/expirada
4. ✅ ImportError ao importar o pacote

## 📋 Como Verificar o Problema

### 1. Endpoint de Debug Melhorado

Acesse: `https://dataforgetest-backend.onrender.com/api/simple/debug`

Procure pela seção `llm_status`:
```json
{
  "llm_status": {
    "configured": false,  // ← Se false, está usando fallback!
    "client_type": null,  // ← Deveria ser "GeminiClient"
    "provider": "not set",  // ← Deveria ser "gemini"
    "model": "not set",  // ← Deveria ser "gemini-1.5-flash"
    "gemini_key_set": false,  // ← Deveria ser true
    "anthropic_key_set": false
  }
}
```

### 2. Verificar Logs do Render

No painel do Render:
1. Vá em **Logs**
2. Procure por:
   ```
   ⚠️  Could not initialize LLM client: ...
   ⚠️  No LLM configured. Using simple template responses.
   ```

3. Se encontrar, veja o erro específico:
   - `google-generativeai package not installed` → Problema no build
   - `GEMINI_API_KEY is required` → Variável não configurada
   - `Invalid API key` → Chave incorreta

### 3. Comparar Respostas

**Com LLM (esperado):**
```
"PySpark is a Python library for Apache Spark, which allows for 
distributed data processing and machine learning at scale. It 
provides an API that enables users to write applications in 
Python while leveraging the power of Spark's computational engine..."
```

**Sem LLM (templates - problema atual):**
```
"Based on the documentation:

PySpark is the Python API for Spark. It enables you to write Spark 
applications using Python APIs.

This information comes from the knowledge base and should provide 
guidance for your data quality needs."
```

## ✅ Soluções

### Solução 1: Verificar Variáveis no Render

**No Render Dashboard → Environment:**

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...  # Sua chave real
GEMINI_MODEL=gemini-1.5-flash
```

**Checklist:**
- [ ] `LLM_PROVIDER` está definida?
- [ ] `GEMINI_API_KEY` está definida?
- [ ] `GEMINI_MODEL` está definida?
- [ ] Chave começa com `AIza`?
- [ ] Salvou e fez redeploy?

### Solução 2: Testar API Key Localmente

```bash
# Configure localmente
set GEMINI_API_KEY=AIzaSy...
set LLM_PROVIDER=gemini
set GEMINI_MODEL=gemini-1.5-flash

# Instale o pacote
pip install google-generativeai

# Execute o teste
python test_gemini.py
```

Se funcionar localmente mas não em produção → problema nas variáveis do Render.

### Solução 3: Verificar Build do Render

No Render, vá em **Logs** e procure durante o build:

```
Successfully installed google-generativeai-X.X.X
```

Se não aparecer:
1. Verifique se `requirements.txt` tem `google-generativeai`
2. Force um redeploy: **Manual Deploy → Deploy latest commit**

### Solução 4: Fallback para Ollama (não recomendado)

Se Gemini não funcionar, pode usar templates:
```bash
# Remova as variáveis de LLM
# O sistema usará fallback templates automaticamente
```

⚠️ Mas isso não resolve o problema, apenas aceita o fallback.

## 🧪 Script de Diagnóstico

Execute localmente:
```bash
python diagnose_llm_production.py
```

Cenários testados:
1. ✅ Sem variáveis (default ollama - funciona localmente)
2. ❌ Com Gemini mas sem pacote (simula problema)
3. ✅ Com Ollama mas sem servidor (cria client, mas falha ao gerar)
4. ✅ RAG integration completa

## 📊 Status Atual

Execute este comando no terminal do Render para verificar:

```bash
python -c "import os; print('Provider:', os.getenv('LLM_PROVIDER')); print('Gemini Key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

Ou adicione log temporário em `simple_chat.py`:
```python
print(f"🔍 LLM DEBUG: provider={os.getenv('LLM_PROVIDER')}, key_set={bool(os.getenv('GEMINI_API_KEY'))}")
```

## ✅ Confirmação de Sucesso

Após configurar corretamente, você verá nos logs:
```
✅ LLM initialized with provider: gemini, model: gemini-1.5-flash
```

E o endpoint `/debug` mostrará:
```json
{
  "llm_status": {
    "configured": true,
    "client_type": "GeminiClient",
    "provider": "gemini",
    "gemini_key_set": true
  }
}
```

## 🎯 Ação Imediata

**Passo a passo:**

1. **Verificar endpoint de debug:**
   - Acesse: `https://dataforgetest-backend.onrender.com/api/simple/debug`
   - Anote os valores de `llm_status`

2. **Se `configured: false`:**
   - Vá no Render Dashboard
   - Environment → Adicione as 3 variáveis
   - Save Changes → Aguarde redeploy

3. **Se `configured: true` mas respostas ruins:**
   - Problema pode ser na API key
   - Teste a chave localmente primeiro

4. **Após configurar:**
   - Aguarde deploy (~5-10 min)
   - Teste novamente o chat
   - Verifique `/debug` novamente

---

**Precisa de ajuda?** Compartilhe:
1. Output do `/debug`
2. Logs do Render (últimas 50 linhas)
3. Exemplo de resposta do chat
