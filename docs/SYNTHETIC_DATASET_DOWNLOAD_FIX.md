# Synthetic Dataset Download Fix - Janeiro 2026

## Problemas Identificados

### 1. Incompatibilidade de Modelo/Provider
**Problema**: O sistema estava tentando usar modelos incompatíveis com o provider configurado:
- **Local**: Tentando usar `qwen2.5-coder:7b` (modelo Ollama) com Gemini API → erro 404
- **Produção**: Tentando usar `claude-3-haiku-20240307` (modelo Anthropic) com Gemini API → erro 404

**Logs de erro**:
```
ERROR: Gemini API error: 404 models/qwen2.5-coder:7b is not found for API version v1beta
ERROR: Gemini API error: 404 models/claude-3-haiku-20240307 is not found for API version v1beta
```

### 2. Problema de Download HTML
**Problema**: Quando o sistema falhava e usava mock data, o download retornava HTML em vez de CSV, provavelmente devido a URLs mal formadas ou redirecionamentos.

## Correções Implementadas

### 1. Configuração Correta do Provider ([src/synthetic/routes.py](src/synthetic/routes.py#L21-L28))
```python
# Initialize generator with provider
generator = SyntheticDataGenerator(
    api_key=config.llm_api_key,
    model=config.llm_model,
    provider=config.llm_provider,  # ✅ Agora passa o provider explicitamente
)
```

### 2. Detecção de Modelos por Provider ([src/synthetic/config.py](src/synthetic/config.py#L52-L58))
```python
# Determine provider and default model
provider = os.getenv("LLM_PROVIDER", "ollama")
if provider == "ollama":
    default_model = "qwen2.5-coder:7b"
elif provider == "gemini":
    default_model = "gemini-2.0-flash-exp"  # ✅ Modelo correto para Gemini
else:  # anthropic
    default_model = "claude-3-haiku-20240307"
```

### 3. Validação de Compatibilidade Modelo/Provider ([src/synthetic/generator.py](src/synthetic/generator.py#L42-L54))
```python
# Validate model/provider compatibility
if model:
    if provider == "gemini" and (model.startswith("claude") or "qwen" in model or "llama" in model):
        print(f"[ERROR] Model '{model}' is not compatible with Gemini provider. Use a Gemini model like 'gemini-2.0-flash-exp'")
        raise ValueError(f"Model {model} is not compatible with provider {provider}")
    elif provider == "anthropic" and (model.startswith("gemini") or "qwen" in model or "llama" in model):
        print(f"[ERROR] Model '{model}' is not compatible with Anthropic provider. Use a Claude model like 'claude-3-haiku-20240307'")
        raise ValueError(f"Model {model} is not compatible with provider {provider}")
    elif provider == "ollama" and (model.startswith("gemini") or model.startswith("claude")):
        print(f"[ERROR] Model '{model}' is not compatible with Ollama provider. Use an Ollama model like 'qwen2.5-coder:7b'")
        raise ValueError(f"Model {model} is not compatible with provider {provider}")
```

### 4. URLs Absolutas em Produção ([src/synthetic/routes.py](src/synthetic/routes.py#L218-L227))
```python
# Build download URL - make it absolute if we have a host header
download_path = f"/api/synth/download/{session_id}/{output_file.name}"
download_url = download_path

# In production environments, build an absolute URL
if request.host:
    scheme = "https" if request.is_secure else "http"
    download_url = f"{scheme}://{request.host}{download_path}"  # ✅ URL absoluta
```

### 5. Frontend: Tratamento de URLs Absolutas e Relativas ([frontend/src/pages/GenerateDataset.js](frontend/src/pages/GenerateDataset.js#L187-L191))
```javascript
// Check if download URL is already absolute (starts with http/https)
const downloadUrlToUse = data.downloadUrl.startsWith('http') 
  ? data.downloadUrl 
  : getApiUrl(data.downloadUrl);  // ✅ Só processa se for relativa
setDownloadUrl(downloadUrlToUse);
```

## Variáveis de Ambiente Necessárias

### Para Gemini (Produção)
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.0-flash-exp  # ou gemini-2.5-flash
```

### Para Ollama (Local)
```bash
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
```

### Para Anthropic
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=your_anthropic_api_key_here
LLM_MODEL=claude-3-haiku-20240307
```

## Como Testar

### 1. Local com Ollama
```bash
# Certifique-se que o Ollama está rodando
ollama list  # Verifica modelos instalados
ollama pull qwen2.5-coder:7b  # Se necessário

# Configure o .env
echo "LLM_PROVIDER=ollama" >> .env
echo "LLM_MODEL=qwen2.5-coder:7b" >> .env

# Inicie o servidor
.\dev_start.bat
```

### 2. Produção com Gemini
Configure as variáveis de ambiente no Render/Vercel:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=<sua_chave>
LLM_MODEL=gemini-2.0-flash-exp
```

### 3. Teste o Download
1. Acesse a página de geração de dataset sintético
2. Configure as colunas (ex: nome, idade, email)
3. Gere 10-100 linhas
4. Verifique os logs para confirmar que o modelo correto está sendo usado
5. Clique em "Download Dataset"
6. Verifique que o arquivo baixado é um CSV válido, não HTML

## Comportamento Esperado

### Sucesso com LLM
```
[OK] LLM client initialized for synthetic data generation (provider: gemini, model: gemini-2.0-flash-exp)
Generated prompt for 10 rows
Calling LLM (attempt 1/3)...
Received response (1234 chars)
Parsed 10 rows from CSV
Coerced types for 10 records
Enforced uniqueness: 10 unique records
```

### Fallback para Mock Data (se LLM falhar)
```
[WARNING] Could not initialize LLM client: Model qwen2.5-coder:7b is not compatible with provider gemini
Synthetic data generation will use mock data fallback
ERROR: No LLM configured, using mock data
```

## Arquivos Modificados

1. **[src/synthetic/routes.py](src/synthetic/routes.py)**: 
   - Passa provider para o generator
   - Gera URLs absolutas em produção

2. **[src/synthetic/config.py](src/synthetic/config.py)**:
   - Seleciona modelo padrão correto baseado no provider

3. **[src/synthetic/generator.py](src/synthetic/generator.py)**:
   - Valida compatibilidade modelo/provider
   - Melhores mensagens de erro

4. **[frontend/src/pages/GenerateDataset.js](frontend/src/pages/GenerateDataset.js)**:
   - Trata URLs absolutas e relativas corretamente

## Próximos Passos

- [ ] Testar em produção com Gemini
- [ ] Verificar que o CSV baixado está formatado corretamente
- [ ] Adicionar retry logic mais robusto se necessário
- [ ] Considerar adicionar validação de modelo na API `/api/synth/health`
