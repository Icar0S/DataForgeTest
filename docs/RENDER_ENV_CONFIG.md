# Configuração de Variáveis de Ambiente no Render

## Problema Identificado

O sistema em produção está tentando usar o modelo `claude-3-haiku-20240307` (Anthropic) ao invés do modelo Gemini configurado. Isso acontece porque as variáveis de ambiente não estão sendo lidas corretamente no Render.

## ⚠️ Erro Atual

```
ERROR: Gemini API error: 404 models/claude-3-haiku-20240307 is not found
```

Isso indica que o sistema está caindo no fallback para Anthropic, o que significa que `LLM_PROVIDER` não está definido como `gemini` em produção.

## ✅ Configuração Correta no Render

Acesse o painel do Render e configure as seguintes **Environment Variables**:

### 1. Configuração LLM (OBRIGATÓRIA)

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAn1gGblIgQfuIdDGZKkjiNZM7ddYWIPKE
GEMINI_MODEL=gemini-2.0-flash-exp
```

**IMPORTANTE**: Use `gemini-2.0-flash-exp` ou `gemini-2.5-flash-lite`, NÃO use apenas `gemini-2.5-flash-lite` se não funcionar.

### 2. Modelos Gemini Disponíveis (Janeiro 2026)

Teste nesta ordem:
1. `gemini-2.0-flash-exp` ✅ Recomendado
2. `gemini-2.5-flash-lite` 
3. `gemini-1.5-flash`
4. `gemini-1.5-pro`

### 3. Outras Variáveis de Ambiente

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Storage Paths (usar caminhos relativos)
SYNTH_STORAGE_PATH=./storage/synth
ACCURACY_STORAGE_PATH=./storage/accuracy
GOLD_STORAGE_PATH=./storage/gold
VECTOR_STORE_PATH=./storage/vectorstore

# Synthetic Dataset Configuration
SYNTH_MAX_ROWS=1000000
SYNTH_REQUEST_TIMEOUT=300
SYNTH_MAX_MEM_MB=2048
SYNTH_RATE_LIMIT=60

# CORS (se necessário)
# CORS_ORIGINS=https://data-forge-test.vercel.app
```

## 📋 Passos para Configurar no Render

### Opção 1: Via Dashboard (Recomendado)

1. Acesse seu projeto no Render: https://dashboard.render.com/
2. Clique no seu Web Service (backend)
3. Vá em **Environment** (menu lateral esquerdo)
4. Clique em **Add Environment Variable**
5. Adicione as variáveis uma por uma:
   - Key: `LLM_PROVIDER` → Value: `gemini`
   - Key: `GEMINI_API_KEY` → Value: `AIzaSyAn1gGblIgQfuIdDGZKkjiNZM7ddYWIPKE`
   - Key: `GEMINI_MODEL` → Value: `gemini-2.0-flash-exp`
6. Clique em **Save Changes**
7. O Render fará redeploy automático

### Opção 2: Via render.yaml

Edite o arquivo `render.yaml` na raiz do projeto:

```yaml
services:
  - type: web
    name: data-quality-chatbot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn src.api:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: LLM_PROVIDER
        value: gemini
      - key: GEMINI_API_KEY
        value: AIzaSyAn1gGblIgQfuIdDGZKkjiNZM7ddYWIPKE
      - key: GEMINI_MODEL
        value: gemini-2.0-flash-exp
      - key: SYNTH_STORAGE_PATH
        value: ./storage/synth
```

⚠️ **ATENÇÃO**: Não commite o `render.yaml` com a API key! Use Secrets do Render para chaves sensíveis.

### Opção 3: Secrets (Mais Seguro)

1. No Render Dashboard, vá em **Environment**
2. Para `GEMINI_API_KEY`, marque como **Secret**
3. Isso oculta o valor da API key no dashboard

## 🔍 Como Verificar se Funcionou

Após configurar e fazer redeploy:

1. **Acesse os logs do Render**:
   - No dashboard, clique em **Logs**
   - Procure por: `[OK] LLM client initialized for synthetic data generation (provider: gemini`

2. **Teste a geração de dataset**:
   - Acesse o frontend em produção
   - Vá em "Generate Synthetic Dataset"
   - Configure algumas colunas e gere 10-50 linhas
   - Verifique os logs de geração

3. **Logs esperados de SUCESSO**:
   ```
   [OK] LLM client initialized for synthetic data generation (provider: gemini, model: gemini-2.0-flash-exp)
   Generated prompt for 10 rows
   Calling LLM (attempt 1/3)...
   Received response (1234 chars)
   Parsed 10 rows from CSV
   ```

4. **Se ainda usar mock data**:
   ```
   ERROR: No LLM configured, using mock data
   ```
   Isso significa que as variáveis ainda não estão corretas.

## 🐛 Troubleshooting

### Problema: Ainda mostra erro 404 do Claude

**Causa**: `LLM_PROVIDER` não está definido como `gemini` em produção.

**Solução**:
1. Verifique se a variável está EXATAMENTE como `LLM_PROVIDER=gemini` (sem espaços)
2. Certifique-se de que fez redeploy após adicionar as variáveis
3. Verifique os logs do Render para ver qual provider está sendo usado

### Problema: API key inválida

**Erro**: `GEMINI_API_KEY is not set or is invalid`

**Solução**:
1. Gere uma nova API key em: https://aistudio.google.com/app/apikey
2. Atualize a variável `GEMINI_API_KEY` no Render
3. Faça redeploy

### Problema: Modelo não encontrado

**Erro**: `404 models/gemini-2.5-flash-lite is not found`

**Solução**:
Tente outros modelos disponíveis:
```bash
# Tente cada um até funcionar:
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MODEL=gemini-1.5-pro
```

### Problema: Download retorna HTML

**Causa**: URL de download mal formada ou erro de CORS.

**Solução**:
1. Verifique se o backend está rodando corretamente
2. Teste o endpoint diretamente: `GET https://seu-backend.onrender.com/api/synth/download/{session_id}/dataset.csv`
3. Verifique os logs do Render para erros no endpoint de download

## 📊 Verificação Rápida

Execute este comando para verificar as variáveis no Render (via API):

```bash
curl -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  https://api.render.com/v1/services/YOUR_SERVICE_ID/env-vars
```

Ou use a CLI do Render:

```bash
render env get -s YOUR_SERVICE_ID LLM_PROVIDER
render env get -s YOUR_SERVICE_ID GEMINI_MODEL
```

## 🎯 Checklist Final

- [ ] `LLM_PROVIDER=gemini` configurado no Render
- [ ] `GEMINI_API_KEY` configurado com chave válida
- [ ] `GEMINI_MODEL=gemini-2.0-flash-exp` ou similar
- [ ] Redeploy realizado após adicionar variáveis
- [ ] Logs mostram: `[OK] LLM client initialized ... (provider: gemini`
- [ ] Teste de geração de dataset funciona
- [ ] Download retorna CSV válido, não HTML

## 🔐 Segurança

**NUNCA** commite arquivos `.env` com API keys reais para o repositório!

Adicione ao `.gitignore`:
```
.env
.env.local
.env.production
*.key
```

Use apenas variáveis de ambiente do Render para valores sensíveis em produção.
