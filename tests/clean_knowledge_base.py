"""Script para limpar documentos rasos da base de conhecimento."""

import json
import os
from datetime import datetime
from pathlib import Path


def clean_knowledge_base():
    """Remove documentos de teste e mantém apenas conteúdo substancial."""

    storage_path = Path("storage/vectorstore")
    documents_file = storage_path / "documents.json"

    if not documents_file.exists():
        print("❌ Arquivo documents.json não encontrado!")
        return

    # Carregar documentos existentes
    with open(documents_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = data.get("documents", {})

    print("=" * 70)
    print("LIMPEZA DA BASE DE CONHECIMENTO")
    print("=" * 70)
    print(f"📚 Documentos atuais: {len(documents)}")

    # Analisar documentos
    to_remove = []
    to_keep = []

    for doc_id, doc_data in documents.items():
        content = doc_data.get("content", "")
        metadata = doc_data.get("metadata", {})
        filename = metadata.get("filename", "Unknown")
        content_length = len(content)

        # Critérios para remoção
        should_remove = False
        reason = ""

        # 1. Documentos de teste muito pequenos
        if content_length < 100 and "test" in filename.lower():
            should_remove = True
            reason = "Documento de teste muito pequeno"

        # 2. Conteúdo genérico/raso
        elif content_length < 100:
            should_remove = True
            reason = "Conteúdo muito pequeno"

        # 3. Documentos duplicados (mesmo conteúdo)
        elif content.strip() == "Test document about data quality":
            should_remove = True
            reason = "Documento de teste genérico"

        if should_remove:
            to_remove.append(
                {
                    "id": doc_id,
                    "filename": filename,
                    "length": content_length,
                    "reason": reason,
                }
            )
        else:
            to_keep.append(
                {
                    "id": doc_id,
                    "filename": filename,
                    "length": content_length,
                    "title": metadata.get("title", "Sem título"),
                }
            )

    print(f"\n🗑️  DOCUMENTOS PARA REMOÇÃO ({len(to_remove)}):")
    for doc in to_remove:
        print(f"   ❌ {doc['filename']} ({doc['length']} chars)")
        print(f"      ID: {doc['id'][:8]}... - {doc['reason']}")

    print(f"\n✅ DOCUMENTOS PARA MANTER ({len(to_keep)}):")
    for doc in to_keep:
        print(f"   📄 {doc['filename']} ({doc['length']} chars)")
        print(f"      ID: {doc['id'][:8]}... - {doc['title']}")

    # Confirmar remoção
    if to_remove:
        print(f"\n⚠️  Isso irá remover {len(to_remove)} documentos da base!")
        confirm = input("Digite 'CONFIRMAR' para continuar: ")

        if confirm == "CONFIRMAR":
            # Remover documentos
            cleaned_documents = {}
            for doc_id, doc_data in documents.items():
                if not any(doc["id"] == doc_id for doc in to_remove):
                    cleaned_documents[doc_id] = doc_data

            # Salvar base limpa
            cleaned_data = {
                "documents": cleaned_documents,
                "last_updated": datetime.now().isoformat(),
                "cleanup_performed": True,
                "cleanup_date": datetime.now().isoformat(),
                "removed_documents": len(to_remove),
                "remaining_documents": len(cleaned_documents),
            }

            # Backup da versão original
            backup_file = (
                storage_path
                / f"documents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📦 Backup salvo em: {backup_file}")

            # Salvar versão limpa
            with open(documents_file, "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

            print(f"\n✅ LIMPEZA CONCLUÍDA!")
            print(f"   📚 Documentos restantes: {len(cleaned_documents)}")
            print(f"   🗑️  Documentos removidos: {len(to_remove)}")
            print(f"   💾 Base salva em: {documents_file}")

            print(f"\n🔄 Para aplicar as mudanças, reinicie o backend:")
            print(f"   cd src && python api.py")
        else:
            print("❌ Limpeza cancelada")
    else:
        print(f"\n✅ Nenhum documento precisa ser removido!")
        print(f"   Todos os {len(documents)} documentos têm conteúdo substancial.")


if __name__ == "__main__":
    clean_knowledge_base()
