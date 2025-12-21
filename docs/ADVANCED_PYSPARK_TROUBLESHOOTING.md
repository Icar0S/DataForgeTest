# Advanced PySpark Generator - Troubleshooting Guide

## Overview

Este documento fornece soluções para problemas comuns ao usar o Advanced PySpark Code Generator com datasets públicos brasileiros.

## Problemas Comuns

### 1. Erro de Encoding com CSVs Governamentais

**Sintoma**: Erro ao fazer upload de CSVs de sites governamentais brasileiros (ex: Portal de Dados Abertos).

**Causa**: Arquivos CSV governamentais frequentemente usam encoding Windows-1252, ISO-8859-1 ou Latin-1 ao invés de UTF-8, resultando em caracteres especiais mal formatados (ñ, É, Á, etc.).

**Solução**:
```javascript
// O sistema detecta automaticamente o encoding, mas você pode especificar:
1. Deixe "Auto-detect" selecionado (recomendado)
2. Se falhar, tente manualmente: latin-1, ISO-8859-1, ou windows-1252
```

**Encodings testados e funcionais**:
- ✓ ISO-8859-1 (padrão brasileiro)
- ✓ Latin-1
- ✓ Windows-1252 (CP1252)
- ✓ UTF-8

### 2. Erro com Delimitadores

**Sintoma**: Apenas uma coluna detectada ou erro de parsing.

**Causa**: CSVs brasileiros frequentemente usam ponto-e-vírgula (;) como delimitador ao invés de vírgula (,).

**Solução**:
```javascript
// O sistema detecta automaticamente, mas pode ser configurado:
- Auto-detect (recomendado) - testa: , ; \t |
- Semicolon (;) - comum em dados BR
- Comma (,) - padrão internacional
```

### 3. Erro de Serialização JSON

**Sintoma**: "Cannot serialize to JSON" ou erro 500.

**Causa**: Valores NaN, Infinity, ou tipos não serializáveis no metadata.

**Status**: ✅ Resolvido - sistema converte automaticamente para tipos JSON-safe.

### 4. Timeout em Grandes Datasets

**Sintoma**: Timeout ao processar arquivos grandes.

**Solução**:
- Limite de 100MB por arquivo
- Use sample_size para reduzir análise
- Para arquivos >100MB, pré-processe localmente

### 5. Nomes de Colunas com Caracteres Especiais

**Sintoma**: Erro ao gerar código PySpark com colunas contendo acentos ou caracteres especiais.

**Status**: ✅ Funcional - testado com colunas como "Mês", "Período", etc.

## Datasets Testados

### ✅ Testado e Funcionando

1. **arrecadacao-estado.csv**
   - Fonte: Dados Abertos Brasil
   - Encoding: ISO-8859-1
   - Delimiter: ; (ponto-e-vírgula)
   - Colunas: 47
   - Linhas: 8,290
   - Caracteres especiais: ã, é, ç, ê, etc.
   - Status: ✅ Completo

2. **ALUNOS-DA-GRADUACAO-2025-1.csv**
   - Fonte: Sistema acadêmico
   - Colunas: 7
   - Linhas: 8,885
   - Status: ✅ Completo

## Fluxo de Testes Realizados

```bash
# Todos os testes passaram:
[✓] 1. Detecção de encoding automática
[✓] 2. Detecção de delimiter automática
[✓] 3. Inspeção de metadata
[✓] 4. Geração de DSL
[✓] 5. Geração de código PySpark
[✓] 6. Serialização JSON
[✓] 7. Integração completa
```

## Como Reportar Problemas

Se você encontrar um erro não listado aqui:

1. **Capture o erro completo** (screenshot ou mensagem)
2. **Informações do arquivo**:
   - Formato (CSV, JSON, Parquet)
   - Tamanho
   - Fonte
   - Primeiras linhas (se possível)
3. **Configurações usadas**:
   - Encoding selecionado
   - Delimiter
   - Opções adicionais
4. **Passo onde ocorreu**:
   - Upload/Inspect
   - Generate DSL
   - Generate PySpark

## Scripts de Diagnóstico

Os seguintes scripts estão disponíveis para diagnosticar problemas:

### `test_csv_encoding.py`
Testa detecção de encoding e delimiters:
```bash
python test_csv_encoding.py
```

### `test_full_workflow.py`
Testa o fluxo completo (inspect → DSL → PySpark):
```bash
python test_full_workflow.py
```

### `test_json_serialization.py`
Testa serialização JSON de todas as etapas:
```bash
python test_json_serialization.py
```

### `test_both_csvs.py`
Testa múltiplos CSVs:
```bash
python test_both_csvs.py
```

## Logs de Backend

Para habilitar logs detalhados no backend:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Os logs mostrarão:
- Encoding detectado
- Delimiter detectado
- Erros de parsing
- Detalhes de cada etapa

## Performance

### Métricas dos Testes

**arrecadacao-estado.csv (8,290 linhas, 47 colunas)**:
- Inspect: ~1-2s
- Generate DSL: <1s
- Generate PySpark: <1s
- Total: ~2-4s

**ALUNOS-DA-GRADUACAO-2025-1.csv (8,885 linhas, 7 colunas)**:
- Inspect: ~1s
- Generate DSL: <1s
- Generate PySpark: <1s
- Total: ~1-2s

## Próximas Melhorias

- [ ] Suporte para múltiplos delimiters na mesma linha
- [ ] Preview com encoding correto no browser
- [ ] Cache de detecção para reuploads
- [ ] Suporte para CSV com multi-line strings
- [ ] Validação mais robusta de tipos de dados

## Contato

Se após seguir este guia você ainda tiver problemas, forneça:
1. Screenshot do erro
2. Arquivo de teste (se possível)
3. Logs do console do navegador (F12)
4. Logs do backend

## Resumo de Status

| Funcionalidade | Status | Notas |
|----------------|--------|-------|
| Auto-detect encoding | ✅ | ISO-8859-1, Latin-1, UTF-8 |
| Auto-detect delimiter | ✅ | , ; \t \| |
| CSVs governamentais BR | ✅ | Testado com dados reais |
| Caracteres especiais | ✅ | Acentos, ç, ñ, etc. |
| JSON serialization | ✅ | Todos os tipos suportados |
| PySpark code gen | ✅ | Colab-ready |
| Arquivos grandes | ⚠️ | Limite: 100MB |
| Multi-file upload | ❌ | Planejado |

**Última atualização**: 2025-12-21
