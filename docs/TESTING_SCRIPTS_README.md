# 🧪 Scripts de Teste e Diagnóstico

Scripts criados para diagnosticar problemas com o Advanced PySpark Generator.

## 📋 Scripts Disponíveis

### 1. `test_csv_encoding.py`
**Propósito**: Testar detecção de encoding e delimiter

**Uso**:
```bash
python test_csv_encoding.py
```

**O que testa**:
- Auto-detecção de encoding (ISO-8859-1, Latin-1, UTF-8, etc.)
- Auto-detecção de delimiter (`,`, `;`, `\t`, `|`)
- Parsing básico do CSV
- Listagem de primeiras colunas

**Exemplo de saída**:
```
✓ Success! Detected encoding: ISO-8859-1
  Delimiter: ';'
  Rows: 8290, Columns: 47
  First 3 columns:
    - Ano (float64)
    - Mês (object)
    - UF (object)
```

---

### 2. `test_full_workflow.py`
**Propósito**: Testar fluxo completo do backend

**Uso**:
```bash
python test_full_workflow.py
```

**O que testa**:
- [STEP 1] Dataset inspection
- [STEP 2] DSL generation
- [STEP 3] PySpark code generation
- Visualização de primeiras linhas do código gerado

**Exemplo de saída**:
```
[STEP 1] Inspecting dataset...
✓ Inspection successful!
  Encoding: ISO-8859-1
  Delimiter: ';'
  Rows: 8290, Columns: 47

[STEP 2] Generating DSL...
✓ DSL generation successful!
  Rules: 37
  Schema fields: 47

[STEP 3] Generating PySpark code...
✓ PySpark code generation successful!
  Code length: 18673 characters
  Lines of code: 381
```

---

### 3. `test_json_serialization.py`
**Propósito**: Validar serialização JSON em todas as etapas

**Uso**:
```bash
python test_json_serialization.py
```

**O que testa**:
- Serialização de metadata para JSON
- Serialização de DSL para JSON
- Serialização de response (PySpark code) para JSON
- Detecção de valores não serializáveis (NaN, Infinity, etc.)

**Exemplo de saída**:
```
[1] Inspect dataset...
  Rows: 8290, Columns: 47

[2] Testing metadata JSON serialization...
  ✓ Metadata serialization OK (28987 chars)
  ✓ Metadata deserialization OK

[3] Generate DSL...

[4] Testing DSL JSON serialization...
  ✓ DSL serialization OK (10418 chars)
  ✓ DSL deserialization OK
```

---

### 4. `test_both_csvs.py`
**Propósito**: Testar múltiplos CSVs em batch

**Uso**:
```bash
python test_both_csvs.py
```

**O que testa**:
- Processa todos os CSVs listados
- Testa workflow completo para cada um
- Gera resumo de sucessos e falhas

**Exemplo de saída**:
```
Testing: arrecadacao-estado.csv
[1] Inspecting...
✓ Rows: 8290, Columns: 47
[2] Generating DSL...
✓ Rules: 37
[3] Generating PySpark code...
✓ Code: 18673 chars, 381 lines

✓✓✓ SUCCESS for arrecadacao-estado.csv ✓✓✓
```

---

### 5. `test_api_integration.py` ⭐ Mais Completo
**Propósito**: Simular exatamente o que o frontend faz (chamadas HTTP)

**Uso**:
```bash
python test_api_integration.py
```

**O que testa**:
- POST /api/datasets/inspect (com multipart/form-data)
- POST /api/datasets/generate-dsl (com JSON)
- POST /api/datasets/generate-pyspark (com JSON)
- Status codes HTTP
- Estrutura das respostas JSON

**Exemplo de saída**:
```
[1] POST /api/datasets/inspect
    Status: 200
    ✓ Rows: 8290, Columns: 47
    Encoding: ISO-8859-1
    Delimiter: ';'

[2] POST /api/datasets/generate-dsl
    Status: 200
    ✓ DSL generated
    Rules: 37

[3] POST /api/datasets/generate-pyspark
    Status: 200
    ✓ PySpark code generated
    Filename: generated_dataset.py
    Code length: 18673 chars

✓✓✓ COMPLETE SUCCESS ✓✓✓
```

---

## 🔧 Como Personalizar os Testes

### Adicionar Seu Próprio CSV

Edite o arquivo de teste e modifique o caminho:

```python
# Exemplo: test_both_csvs.py
test_files = [
    r"C:\Users\Icaro\Downloads\arrecadacao-estado.csv",
    r"C:\Users\Icaro\Downloads\ALUNOS-DA-GRADUACAO-2025-1.csv",
    r"C:\SEU\CAMINHO\PARA\seu_arquivo.csv",  # ← Adicione aqui
]
```

### Testar com Diferentes Encodings

```python
# Exemplo: test_csv_encoding.py
encodings_to_test = ["utf-8", "latin-1", "iso-8859-1", "windows-1252", "cp1252"]
# Adicione mais encodings se necessário
```

---

## 🚨 Quando Usar Cada Script

| Situação | Script Recomendado |
|----------|-------------------|
| Erro "encoding não detectado" | `test_csv_encoding.py` |
| Erro "delimiter incorreto" | `test_csv_encoding.py` |
| Erro em qualquer etapa do workflow | `test_full_workflow.py` |
| Erro "cannot serialize to JSON" | `test_json_serialization.py` |
| Testar vários arquivos de uma vez | `test_both_csvs.py` |
| Erro HTTP 500 ou problemas de API | `test_api_integration.py` ⭐ |
| Problema desconhecido | Executar todos os 5 scripts |

---

## 📊 Interpretando os Resultados

### ✅ Sucesso
Todos os scripts devem mostrar:
```
✓✓✓ SUCCESS ✓✓✓
ou
✓✓✓ ALL STEPS COMPLETED SUCCESSFULLY! ✓✓✓
```

### ❌ Erro
Se um script falhar, ele mostrará:
```
✗✗✗ ERROR ✗✗✗
Error: [mensagem de erro]
Type: [tipo do erro]

Full traceback:
[stack trace completo]
```

Use o traceback para:
1. Identificar em que linha o erro ocorreu
2. Ver qual função causou o problema
3. Entender a causa raiz

---

## 🛠️ Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Instale as dependências:
pip install -r requirements.txt
```

### Erro: "File not found"
```bash
# Verifique o caminho do arquivo no script
# Exemplo de caminho correto:
# Windows: r"C:\Users\Usuario\Downloads\arquivo.csv"
# Linux/Mac: "/home/usuario/downloads/arquivo.csv"
```

### Erro: "Permission denied"
```bash
# Verifique permissões do arquivo
# Windows: Clique direito → Propriedades → Segurança
# Linux/Mac: chmod 644 arquivo.csv
```

---

## 📝 Logs e Debug

Para habilitar logs detalhados, adicione no início do script:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🎯 Quick Start

Para testar tudo rapidamente:

```bash
# 1. Verifique as dependências
pip install -r requirements.txt

# 2. Execute o teste mais completo
python test_api_integration.py

# 3. Se passar, tudo está funcionando!
# 4. Se falhar, execute os outros scripts para diagnóstico específico
```

---

## 📚 Documentação Relacionada

- [`docs/ADVANCED_PYSPARK_TROUBLESHOOTING.md`](./ADVANCED_PYSPARK_TROUBLESHOOTING.md) - Guia completo de troubleshooting
- [`docs/ANALISE_CSV_PUBLICOS_2025-12-21.md`](./ANALISE_CSV_PUBLICOS_2025-12-21.md) - Análise dos testes realizados
- [`docs/RESUMO_INVESTIGACAO.md`](./RESUMO_INVESTIGACAO.md) - Resumo da investigação

---

**Última atualização**: 2025-12-21
