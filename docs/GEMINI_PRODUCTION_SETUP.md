# 🚀 Configuração Gemini API para Produção

## ✅ Sistema Híbrido Configurado

### 🏠 Local (Desenvolvimento)
- **Provider:** Ollama
- **Modelo:** qwen2.5-coder:7b
- **Custo:** ✅ Grátis
- **Configuração:** Automática (já funcionando)

### ☁️ Produção (Render)
- **Provider:** Gemini
- **Modelo:** gemini-1.5-flash (recomendado)
- **Custo:** 💰 Pay-as-you-go (muito barato)
- **Configuração:** Manual no Render

---

## 📋 Passos para Configurar no Render

### 1️⃣ Obter API Key do Gemini

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada

### 2️⃣ Configurar no Render

No painel do Render (https://dashboard.render.com):

1. Vá para seu serviço **dataforgetest-backend**
2. Clique em **"Environment"** (menu lateral)
3. Adicione as seguintes variáveis:

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-1.5-flash
```

4. Clique em **"Save Changes"**
5. O deploy será automaticamente reiniciado

### 3️⃣ Verificar Funcionamento

Após o deploy:

1. Acesse: https://dataforgetest-backend.onrender.com/rag/debug
2. Verifique se aparece:
   ```
   ✅ LLM initialized with provider: gemini, model: gemini-1.5-flash
   ```

3. Teste o chat: https://data-forge-test.vercel.app
4. Faça uma pergunta e veja a resposta inteligente!

---

## 🧪 Testar Localmente com Gemini (Opcional)

Se quiser testar o Gemini localmente antes do deploy:

```bash
# Configure as variáveis
set GEMINI_API_KEY=sua-chave-aqui
set LLM_PROVIDER=gemini
set GEMINI_MODEL=gemini-1.5-flash

# Instale o pacote
pip install google-generativeai

# Execute o teste
python test_gemini.py
```

---

## 💰 Preços do Gemini (Dezembro 2024)

### Gemini 1.5 Flash (Recomendado)
- **Input:** $0.075 / 1M tokens
- **Output:** $0.30 / 1M tokens
- **Contexto:** 1M tokens
- **Melhor para:** Produção (rápido e barato)

### Gemini 1.5 Pro
- **Input:** $1.25 / 1M tokens  
- **Output:** $5.00 / 1M tokens
- **Contexto:** 2M tokens
- **Melhor para:** Tarefas complexas

**Estimativa de custo:**
- 1000 perguntas/mês ≈ $0.50 - $2.00
- Muito mais barato que Claude! 🎉

---

## 🔄 Alternância Entre Providers

### Desenvolvimento Local
```bash
# .env (local)
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
```

### Produção Render
```bash
# Render Environment Variables
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-1.5-flash
```

### Para Voltar ao Ollama
```bash
# Render Environment Variables
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```
⚠️ Mas isso NÃO funcionará no Render (Ollama é local)

---

## ✅ Checklist de Deploy

- [ ] Obter API key do Gemini
- [ ] Adicionar variáveis no Render:
  - [ ] `LLM_PROVIDER=gemini`
  - [ ] `GEMINI_API_KEY=sua-chave`
  - [ ] `GEMINI_MODEL=gemini-1.5-flash`
- [ ] Aguardar deploy automático
- [ ] Testar endpoint: `/rag/debug`
- [ ] Testar chat no frontend
- [ ] Verificar logs no Render

---

## 🆘 Troubleshooting

### Erro: "GEMINI_API_KEY is required"
✅ Verifique se a variável foi adicionada no Render

### Erro: "google-generativeai package not installed"
✅ O `requirements.txt` já tem o pacote, aguarde o deploy

### Chat retorna templates básicos
✅ Verifique se `LLM_PROVIDER=gemini` está configurado

### Erro 429: "Quota exceeded"
✅ Você atingiu o limite gratuito, adicione billing no Google Cloud

---

## 📊 Comparação de Providers

| Provider | Custo | Velocidade | Qualidade | Disponibilidade |
|----------|-------|------------|-----------|-----------------|
| **Ollama** | ✅ Grátis | 🟡 Média | 🟡 Boa | 🔴 Local apenas |
| **Gemini** | ✅ Muito barato | ✅ Rápida | ✅ Excelente | ✅ Cloud |
| **Claude** | 🔴 Caro | ✅ Rápida | ✅ Excelente | ✅ Cloud |

---

## 🎯 Conclusão

Com essa configuração:

✅ **Local:** Ollama (grátis, para desenvolvimento)  
✅ **Produção:** Gemini (barato, alta qualidade)  
✅ **Fallback:** Templates simples (se LLM falhar)  

**Sistema 100% pronto para produção!** 🚀
