"""Simple chat functionality."""

from typing import Dict, List


class SimpleChatEngine:
    """Simple chat engine with RAG context."""

    def __init__(self, rag_system):
        """Initialize chat engine."""
        self.rag = rag_system
        self.chat_history = []

    def chat(self, message: str) -> Dict:
        """Process a chat message with RAG context."""
        # Search for relevant context
        search_results = self.rag.search(message)

        # Build context from search results
        context_parts = []
        citations = []

        for i, result in enumerate(search_results):
            citation_id = i + 1
            context_parts.append(f"[{citation_id}] {result['text']}")
            citations.append(
                {
                    "id": citation_id,
                    "text": result["text"][:200] + "...",
                    "metadata": result["metadata"],
                }
            )

        context_str = "\n\n".join(context_parts)

        # Simple response generation (without external API)
        response = self._generate_simple_response(message, context_str)

        # Store in history
        self.chat_history.append(
            {"message": message, "response": response, "citations": citations}
        )

        return {"response": response, "citations": citations, "sources": search_results}

    def _generate_simple_response(self, question: str, context: str) -> str:
        """Generate a simple response based on context."""
        if not context.strip():
            return (
                "I don't have specific information about that in my knowledge base. "
                "Could you try rephrasing your question or provide more context?"
            )

        # Simple template-based response
        response = f"""Based on the available documentation, here's what I found:

{self._extract_relevant_info(question, context)}

Please note: This response is based on the documents in the knowledge base. You can refer to the citations for more detailed information."""

        return response

    def _extract_relevant_info(self, question: str, context: str) -> str:
        """Extract relevant information from context."""
        # Simple extraction - take first few sentences that might be relevant
        sentences = context.split(". ")

        # Look for sentences that contain question keywords
        question_words = set(question.lower().split())
        relevant_sentences = []

        for sentence in sentences[:5]:  # Limit to first 5 sentences
            sentence_words = set(sentence.lower().split())
            if question_words.intersection(sentence_words):
                relevant_sentences.append(sentence.strip())

        if relevant_sentences:
            return ". ".join(relevant_sentences[:3])  # Max 3 sentences
        else:
            # Fallback: return first part of context
            return (
                sentences[0][:300] + "..."
                if sentences
                else "No specific information found."
            )

    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []

    def get_history(self) -> List[Dict]:
        """Get chat history."""
        return self.chat_history
