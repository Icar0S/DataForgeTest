"""Simple RAG routes for Flask."""

from pathlib import Path
from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename
import json

from .config_simple import RAGConfig
from .simple_rag import SimpleRAG
from .simple_chat import SimpleChatEngine

# Create blueprint
rag_bp = Blueprint("rag", __name__, url_prefix="/api/rag")

# Initialize RAG system
config = RAGConfig.from_env()
rag_system = SimpleRAG(config)
chat_engine = SimpleChatEngine(rag_system)

# Debug: Print RAG initialization info
print(
    f"RAG System initialized: {len(rag_system.documents)} documents, {len(rag_system.document_chunks)} chunks"
)


@rag_bp.route("/debug", methods=["GET"])
def debug_rag():
    """Debug endpoint to check RAG system state."""
    global rag_system, chat_engine

    return jsonify(
        {
            "documents_count": len(rag_system.documents),
            "chunks_count": len(rag_system.document_chunks),
            "documents": [
                {
                    "id": doc_id[:8] + "...",
                    "filename": doc_data.get("metadata", {}).get("filename", "Unknown"),
                    "content_length": len(doc_data.get("content", "")),
                }
                for doc_id, doc_data in list(rag_system.documents.items())[:5]
            ],
        }
    )


@rag_bp.route("/reload", methods=["POST"])
def reload_rag():
    """Reload RAG system to pick up new documents/chunks."""
    global rag_system, chat_engine

    try:
        # Reinitialize RAG system
        config = RAGConfig.from_env()
        rag_system = SimpleRAG(config)
        chat_engine = SimpleChatEngine(rag_system)

        return jsonify(
            {
                "status": "success",
                "message": "RAG system reloaded",
                "documents_count": len(rag_system.documents),
                "chunks_count": len(rag_system.document_chunks),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests."""
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get response from chat engine
        result = chat_engine.chat(message)

        return jsonify(
            {"response": result["response"], "citations": result["citations"]}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/chat-stream", methods=["POST"])
def chat_stream():
    """Handle streaming chat requests."""
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        def generate():
            try:
                # Get response from chat engine
                result = chat_engine.chat(message)
                response_text = result["response"]

                # Stream response word by word
                words = response_text.split()
                for i, word in enumerate(words):
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

                # Send citations at the end
                yield f"data: {json.dumps({'type': 'citations', 'content': {'citations': result['citations']}})}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/chat", methods=["GET"])
def chat_stream_get():
    """Handle streaming chat requests via GET for EventSource."""
    try:
        message = request.args.get("message", "")

        if not message:
            return (
                "data: "
                + json.dumps({"type": "error", "content": "Message is required"})
                + "\n\n",
                400,
            )

        def generate():
            try:
                # Get response from chat engine
                result = chat_engine.chat(message)
                response_text = result["response"]

                # Stream response word by word
                words = response_text.split()
                for i, word in enumerate(words):
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

                # Send citations at the end
                yield f"data: {json.dumps({'type': 'citations', 'content': {'citations': result['citations']}})}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        return "data: " + json.dumps({"type": "error", "content": str(e)}) + "\n\n", 500


@rag_bp.route("/upload", methods=["POST"])
def upload_document():
    """Handle document upload."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "" or file.filename is None:
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.allowed_file_types:
            return (
                jsonify(
                    {
                        "error": f"File type {file_ext} not allowed. Allowed types: {config.allowed_file_types}"
                    }
                ),
                400,
            )

        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = config.storage_path / "temp" / filename
        temp_path.parent.mkdir(exist_ok=True)
        file.save(temp_path)

        try:
            # Extract text content
            content = _extract_text_from_file(temp_path)

            # Add to RAG system
            metadata = {
                "filename": filename,
                "size": temp_path.stat().st_size,
                "type": file_ext,
            }

            doc_id = rag_system.add_document(content, metadata)

            # Clean up temp file
            temp_path.unlink()

            return jsonify(
                {
                    "message": "Document uploaded successfully",
                    "document_id": doc_id,
                    "filename": filename,
                }
            )

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/sources", methods=["GET"])
def get_sources():
    """Get all document sources."""
    try:
        sources = rag_system.get_sources()
        return jsonify({"sources": sources})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route("/sources/<doc_id>", methods=["DELETE"])
def delete_source(doc_id):
    """Delete a document source."""
    try:
        success = rag_system.delete_document(doc_id)
        if success:
            return jsonify({"message": "Document deleted successfully"})
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _extract_text_from_file(file_path: Path) -> str:
    """Extract text content from a file."""
    suffix = file_path.suffix.lower()

    if suffix in [".txt", ".md"]:
        return file_path.read_text(encoding="utf-8")
    elif suffix == ".pdf":
        try:
            import PyPDF2

            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "PDF processing not available. Please install PyPDF2."
    elif suffix == ".csv":
        try:
            import pandas as pd

            df = pd.read_csv(file_path)
            return df.to_string()
        except ImportError:
            # Fallback: simple CSV reading
            return file_path.read_text(encoding="utf-8")
    elif suffix == ".docx":
        try:
            import docx

            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            return "DOCX processing not available. Please install python-docx."
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


@rag_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "RAG service is running"})
