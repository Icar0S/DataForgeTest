"""Initialize RAG documents if not present."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def ensure_documents():
    """Ensure documents.json exists, create if needed."""

    docs_file = Path("storage/vectorstore/documents.json")

    if docs_file.exists():
        print(f"✅ Documents file exists: {docs_file}")
        import json

        with open(docs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            docs_count = len(data.get("documents", {}))
            chunks_count = sum(len(c) for c in data.get("chunks", {}).values())
            print(f"   📚 {docs_count} documents, 📦 {chunks_count} chunks")
        return True

    print(f"❌ Documents file missing: {docs_file}")
    print("Creating parent directories...")

    docs_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if docs_to_import exists
    import_dir = Path("docs_to_import")
    if not import_dir.exists():
        print("❌ docs_to_import directory not found")
        return False

    print("✅ Found docs_to_import, running import...")

    # Import documents
    os.system("python import_documents.py docs_to_import")
    os.system("python reprocess_documents.py")

    if docs_file.exists():
        print("✅ Documents created successfully!")
        return True
    else:
        print("❌ Failed to create documents")
        return False


if __name__ == "__main__":
    ensure_documents()
