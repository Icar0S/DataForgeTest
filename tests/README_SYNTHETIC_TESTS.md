# Testes de Integração - Correções de Download de Dataset Sintético

Este diretório contém testes de integração para validar as correções dos problemas de download de datasets sintéticos.

## Problemas Corrigidos

1. **Mixed Content / HTTPS**: Erro de mixed content ao baixar arquivos em produção HTTPS
2. **Download retorna HTML**: Download retornando HTML em vez de CSV quando LLM falha
3. **Compatibilidade Modelo/Provider**: Tentativa de usar modelos incompatíveis com providers errados
4. **URLs de Download**: Formato incorreto de URLs em produção vs desenvolvimento

## Arquivos de Teste

### `test_synthetic_download_integration.py`
Suite completa de testes de integração usando pytest.

**Testes incluídos:**
- ✅ Health endpoint expõe provider e model
- ✅ Geração de URLs HTTPS com headers de proxy
- ✅ URLs HTTP para localhost
- ✅ Download retorna CSV, não HTML
- ✅ Headers de segurança presentes
- ✅ Validação de compatibilidade modelo/provider
- ✅ Auto-detecção de provider pelo nome do modelo
- ✅ URLs relativas vs absolutas (dev vs prod)

**Como executar:**
```bash
# Com pytest
pytest tests/test_synthetic_download_integration.py -v

# Modo manual (sem pytest)
python tests/test_synthetic_download_integration.py --manual
```

### `test_synthetic_download_quick.py`
Teste rápido de validação sem dependências externas.

**Testes incluídos:**
- ✅ Geração de URLs HTTPS
- ✅ Download CSV (não HTML)
- ✅ Compatibilidade modelo/provider
- ✅ Headers de segurança
- ✅ Health endpoint

**Como executar:**
```bash
python tests/test_synthetic_download_quick.py
```

Saída esperada:
```
======================================================================
QUICK VALIDATION: Synthetic Dataset Download Fixes
======================================================================

[1/5] Testing HTTPS URL generation...
   ✓ PASS: https://dataforgetest-backend.onrender.com/api/synth/...

[2/5] Testing CSV download (not HTML)...
   ✓ PASS: Downloaded 156 bytes of CSV

[3/5] Testing model/provider compatibility...
   ✓ PASS: Gemini model + Gemini provider accepted
   ✓ PASS: Claude model + Gemini provider correctly rejected

[4/5] Testing security headers...
   ✓ PASS: All 4 security headers present

[5/5] Testing health endpoint...
   ✓ PASS: Provider=gemini, Model=gemini-2.0-flash-exp

======================================================================
RESULTS: 5/5 tests passed
✓ ALL TESTS PASSED - Fixes are working correctly!
======================================================================
```

## Executando Todos os Testes

### Opção 1: Teste Rápido (Recomendado)
```bash
python tests/test_synthetic_download_quick.py
```
⚡ **Rápido**: ~2-5 segundos  
📋 **Cobertura**: Valida todas as correções principais

### Opção 2: Suite Completa com pytest
```bash
pytest tests/test_synthetic_download_integration.py -v
```
🔍 **Completo**: Todos os casos de teste  
⏱️ **Duração**: ~10-20 segundos

### Opção 3: Todos os Testes de Synthetic
```bash
pytest tests/test_synthetic*.py -v
```
📦 **Cobertura Total**: Backend + Integração + Downloads

## Validando as Correções em Produção

Após fazer deploy no Render, valide manualmente:

### 1. Verificar Health Endpoint
```bash
curl https://dataforgetest-backend.onrender.com/api/synth/health
```

Deve retornar:
```json
{
  "status": "ok",
  "provider": "gemini",
  "model": "gemini-2.0-flash-exp",
  "max_rows": 1000000
}
```

✅ **Validação**: `provider` deve ser "gemini" e `model` deve ser um modelo Gemini válido.

### 2. Verificar Logs de Inicialização
No Render Dashboard > Logs, procure por:
```
[SYNTHETIC CONFIG] Provider: gemini
[SYNTHETIC CONFIG] Model: gemini-2.0-flash-exp
[SYNTHETIC CONFIG] API Key configured: Yes
[OK] LLM client initialized for synthetic data generation (provider: gemini, model: gemini-2.0-flash-exp)
```

✅ **Validação**: Provider e model devem ser "gemini".

### 3. Testar Geração e Download
1. Acesse https://data-forge-test.vercel.app/
2. Vá para "Generate Synthetic Dataset"
3. Configure:
   - 2-3 colunas simples (id, name, email)
   - 50-100 linhas
   - Formato: CSV
4. Clique em "Generate Dataset"
5. Verifique os logs:
   - ✅ Não deve mostrar "ERROR on attempt 1: Gemini API error: 404"
   - ✅ Deve mostrar "Received response (XXX chars)"
6. Clique em "Download Dataset"
7. Verifique:
   - ✅ Nenhum erro de Mixed Content no console do browser
   - ✅ Arquivo .csv baixado corretamente
   - ✅ Conteúdo é CSV válido (não HTML)

### 4. Verificar URL de Download
No console do browser (F12 > Network):
- Procure pela requisição de download
- URL deve ser: `https://dataforgetest-backend.onrender.com/api/synth/download/...`
- ✅ Deve usar HTTPS (não HTTP)
- ✅ Status: 200 OK
- ✅ Content-Type: text/csv

## Estrutura dos Testes

```
tests/
├── test_synthetic_download_integration.py  # Suite completa (pytest)
├── test_synthetic_download_quick.py        # Validação rápida
├── test_synthetic_backend.py               # Testes existentes de backend
└── README_SYNTHETIC_TESTS.md               # Esta documentação
```

## Casos de Teste Detalhados

### 1. HTTPS URL Generation
**O que testa**: URLs de download usam HTTPS em produção  
**Problema original**: Mixed content error no browser  
**Validação**: URL deve começar com `https://` quando `X-Forwarded-Proto: https`

### 2. CSV Download (not HTML)
**O que testa**: Download retorna CSV válido, não HTML  
**Problema original**: Fallback para mock data retornava HTML  
**Validação**: Content-Type é `text/csv` e conteúdo não começa com `<!DOCTYPE` ou `<html>`

### 3. Model/Provider Compatibility
**O que testa**: Validação de compatibilidade modelo/provider  
**Problema original**: Tentava usar claude/qwen com Gemini API → 404  
**Validação**: 
- ✅ `gemini-*` + `provider=gemini` → OK
- ❌ `claude-*` + `provider=gemini` → ValueError
- ❌ `qwen*` + `provider=gemini` → ValueError

### 4. Security Headers
**O que testa**: Headers de segurança no download  
**Problema original**: Possíveis problemas de CORS e mixed content  
**Validação**: Presença de headers:
- `X-Content-Type-Options: nosniff`
- `Access-Control-Allow-Origin: *`
- `Content-Disposition: attachment`

### 5. Health Endpoint
**O que testa**: Endpoint expõe configuração atual  
**Problema original**: Difícil diagnosticar configuração em produção  
**Validação**: `/api/synth/health` retorna `provider` e `model`

## Troubleshooting

### Teste Falha: "URL doesn't start with https://"
**Causa**: ProxyFix middleware não aplicado ou headers de proxy não detectados  
**Solução**: Verificar que `app.wsgi_app = ProxyFix(...)` está em `src/api.py`

### Teste Falha: "Content is HTML"
**Causa**: LLM não configurado, fallback para mock data falhando  
**Solução**: 
1. Verificar variáveis de ambiente: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL`
2. Verificar logs para erros de inicialização do LLM

### Teste Falha: "Claude+Gemini should be rejected"
**Causa**: Validação de compatibilidade não está funcionando  
**Solução**: Verificar implementação em `src/synthetic/generator.py` linha ~42-54

### Teste Falha: "Missing headers"
**Causa**: Headers de segurança não adicionados no endpoint de download  
**Solução**: Verificar `src/synthetic/routes.py` endpoint `/download/<session_id>/<filename>`

## Integração Contínua (CI)

Para adicionar ao CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Synthetic Download Tests
  run: |
    python tests/test_synthetic_download_quick.py
    pytest tests/test_synthetic_download_integration.py -v
```

## Métricas de Sucesso

✅ **100% dos testes passando**
- 8 testes de integração completa
- 5 testes de validação rápida
- 0 falhas

✅ **Produção funcionando**
- Health endpoint retorna provider e model corretos
- Download funciona sem erro de Mixed Content
- CSV baixado corretamente (não HTML)
- Logs não mostram erros 404 de modelo

## Suporte

Se algum teste falhar:
1. Execute o teste rápido: `python tests/test_synthetic_download_quick.py`
2. Revise os logs detalhados
3. Verifique as variáveis de ambiente no Render
4. Consulte `docs/RENDER_ENV_CONFIG.md` para configuração
5. Consulte `docs/SYNTHETIC_DATASET_DOWNLOAD_FIX.md` para detalhes das correções
