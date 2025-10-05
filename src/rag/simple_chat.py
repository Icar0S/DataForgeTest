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

        # Extract and organize relevant information
        relevant_info = self._extract_relevant_info(question, context)

        # Create a more structured response
        if "data quality" in question.lower():
            response = f"""Data Quality encompasses several key aspects:

{relevant_info}

These aspects are crucial for maintaining reliable, accurate, and trustworthy data in any system."""
        elif "validation" in question.lower():
            response = f"""Data Validation involves several strategies:

{relevant_info}

These validation techniques help ensure data integrity and catch issues early in the data pipeline."""
        elif "issues" in question.lower() or "problems" in question.lower():
            response = f"""Common data quality issues include:

{relevant_info}

Identifying and addressing these issues is essential for maintaining data reliability."""
        else:
            response = f"""Based on the documentation:

{relevant_info}

This information comes from the knowledge base and should provide guidance for your data quality needs."""

        return response

    def _extract_relevant_info(self, question: str, context: str) -> str:
        """Extract relevant information from context."""
        # Clean up context and split into chunks
        chunks = []
        for citation in context.split("\n\n"):
            if citation.strip() and len(citation.strip()) > 50:
                # Remove citation markers like [1], [2], etc.
                clean_chunk = citation.strip()
                if clean_chunk.startswith("[") and "]" in clean_chunk:
                    clean_chunk = clean_chunk.split("]", 1)[1].strip()
                chunks.append(clean_chunk)

        # Look for key topics
        question_lower = question.lower()
        relevant_chunks = []

        for chunk in chunks[:4]:  # Limit to first 4 chunks
            chunk_lower = chunk.lower()

            # Score relevance based on keyword matches
            relevance_score = 0
            if "data quality" in question_lower and any(
                term in chunk_lower for term in ["quality", "validation", "integrity"]
            ):
                relevance_score += 2
            if "validation" in question_lower and any(
                term in chunk_lower for term in ["validation", "check", "verify"]
            ):
                relevance_score += 2
            if "issues" in question_lower and any(
                term in chunk_lower
                for term in ["error", "problem", "issue", "null", "duplicate"]
            ):
                relevance_score += 2
            if "null" in question_lower and "null" in chunk_lower:
                relevance_score += 3

            # General keyword matching
            question_words = set(question_lower.split())
            chunk_words = set(chunk_lower.split())
            if question_words.intersection(chunk_words):
                relevance_score += 1

            if relevance_score > 0:
                relevant_chunks.append((relevance_score, chunk))

        # Sort by relevance and format
        if relevant_chunks:
            relevant_chunks.sort(key=lambda x: x[0], reverse=True)
            formatted_info = []

            for i, (score, chunk) in enumerate(relevant_chunks[:3]):
                # Format chunk nicely
                sentences = chunk.split(". ")
                if len(sentences) > 3:
                    formatted_chunk = ". ".join(sentences[:3]) + "."
                else:
                    formatted_chunk = chunk

                if not formatted_chunk.endswith("."):
                    formatted_chunk += "."

                formatted_info.append(f"• {formatted_chunk}")

            return "\n\n".join(formatted_info)

        # Fallback: use first chunk
        if chunks:
            first_chunk = chunks[0]
            sentences = first_chunk.split(". ")
            if len(sentences) > 2:
                return f"• {'. '.join(sentences[:2])}."
            return f"• {first_chunk}"

        return "• No specific information found in the knowledge base."

    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []

    def get_history(self) -> List[Dict]:
        """Get chat history."""
        return self.chat_history
