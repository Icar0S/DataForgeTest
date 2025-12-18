"""Compare responses with and without Claude API."""

import sys
import os

sys.path.insert(0, "src")

from rag.config_simple import RAGConfig
from rag.simple_rag import SimpleRAG
from rag.simple_chat import SimpleChatEngine

# Load RAG
config = RAGConfig.from_env()
rag = SimpleRAG(config)
chat = SimpleChatEngine(rag)

print("=" * 70)
print("🔬 COMPARAÇÃO: Respostas COM vs SEM Claude API")
print("=" * 70)

question = "o que é validação de dados?"

# Get response
result = chat.chat(question)

print(f"\n❓ Pergunta: {question}")
print(f"\n{'=' * 70}")
print("📝 RESPOSTA ATUAL (sem Claude API - modo template):")
print("=" * 70)
print(result["response"][:500])
print(f"\n... (total: {len(result['response'])} caracteres)")
print(f"\n📚 Citações: {len(result['citations'])}")

print("\n" + "=" * 70)
print("✨ COM CLAUDE API (quando tiver créditos):")
print("=" * 70)
print(
    """A validação de dados é um processo essencial para garantir a qualidade
e integridade das informações em sistemas de big data. 

De acordo com a documentação [1], a validação envolve várias dimensões:

1. **Acurácia**: Os dados representam corretamente os valores do mundo real
2. **Completude**: Todos os dados necessários estão presentes
3. **Consistência**: Os dados são uniformes entre diferentes sistemas
4. **Validade**: Os dados seguem formatos e regras definidas

Técnicas comuns incluem [2]:
- Validação de schema e tipos de dados
- Verificação de ranges e formatos
- Detecção de duplicatas
- Validação cruzada entre campos relacionados

Em ambientes de big data, desafios específicos surgem devido à escala 
(bilhões de registros), velocidade (streaming em tempo real), e variedade 
de formatos. Por isso, é recomendado validar dados o mais cedo possível 
no pipeline e usar amostragem para verificações preliminares em grandes 
volumes."""
)

print("\n" + "=" * 70)
print("🎯 DIFERENÇAS:")
print("=" * 70)
print(
    """
SEM Claude (atual):
❌ Respostas em formato template fixo
❌ Menos contexto e explicação
❌ Não adapta ao nível da pergunta
✅ Instantâneo (0 delay)
✅ Grátis (sem custos)

COM Claude (com créditos):
✅ Respostas naturais e didáticas
✅ Explicações estruturadas e completas
✅ Adapta linguagem à pergunta
✅ Cita fontes de forma clara
🐌 ~2-3 segundos de delay
💰 ~$0.001 por pergunta

RECOMENDAÇÃO: Adicione $5 de créditos no Claude para respostas
muito mais úteis e didáticas! A experiência do usuário melhora 
significativamente.
"""
)
