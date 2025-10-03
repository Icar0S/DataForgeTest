"""Script para importar arquivos PDF e TXT para o sistema RAG."""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class DocumentImporter:
    """Classe para importar documentos PDF e TXT para o sistema RAG."""

    def __init__(self, storage_path: str = "storage/vectorstore"):
        """Inicializar o importador de documentos."""
        self.storage_path = Path(storage_path)
        self.documents_file = self.storage_path / "documents.json"

        # Criar diretório se não existir
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Carregar documentos existentes
        self.documents = self._load_existing_documents()

    def _load_existing_documents(self) -> Dict:
        """Carregar documentos existentes do arquivo JSON."""
        if self.documents_file.exists():
            try:
                with open(self.documents_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("documents", {})
            except Exception as e:
                print(f"⚠️  Erro ao carregar documentos existentes: {e}")
                return {}
        return {}

    def _save_documents(self):
        """Salvar documentos no arquivo JSON."""
        try:
            data = {
                "documents": self.documents,
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.documents_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Erro ao salvar documentos: {e}")
            raise

    def _read_txt_file(self, file_path: Path) -> Optional[str]:
        """Ler conteúdo de arquivo TXT."""
        try:
            # Tentar diferentes encodings
            encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read().strip()
                        if content:
                            print(f"   ✓ Lido com encoding {encoding}")
                            return content
                except UnicodeDecodeError:
                    continue

            print(f"   ❌ Não foi possível ler o arquivo com nenhum encoding")
            return None

        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo TXT: {e}")
            return None

    def _read_pdf_file(self, file_path: Path) -> Optional[str]:
        """Ler conteúdo de arquivo PDF."""
        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            print(
                f"   ❌ Nenhuma biblioteca PDF disponível. Instale: pip install pdfplumber PyPDF2"
            )
            return None

        # Tentar pdfplumber primeiro (melhor para texto)
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber

                text_content = []

                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            text_content.append(f"[Página {page_num}]\n{text.strip()}")

                if text_content:
                    content = "\n\n".join(text_content)
                    print(f"   ✓ Extraído com pdfplumber ({len(pdf.pages)} páginas)")
                    return content

            except Exception as e:
                print(f"   ⚠️  pdfplumber falhou: {e}")

        # Fallback para PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                import PyPDF2

                text_content = []

                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)

                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text:
                            text_content.append(f"[Página {page_num}]\n{text.strip()}")

                if text_content:
                    content = "\n\n".join(text_content)
                    print(f"   ✓ Extraído com PyPDF2 ({len(pdf_reader.pages)} páginas)")
                    return content

            except Exception as e:
                print(f"   ❌ PyPDF2 também falhou: {e}")

        return None

    def import_files_from_folder(
        self, folder_path: str, file_patterns: List[str] = None
    ) -> Dict:
        """Importar arquivos de uma pasta."""
        if file_patterns is None:
            file_patterns = ["*.pdf", "*.txt", "*.md"]

        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")

        print("=" * 70)
        print(f"IMPORTANDO DOCUMENTOS DE: {folder.absolute()}")
        print("=" * 70)

        # Encontrar arquivos
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(folder.glob(pattern))

        if not files_to_process:
            print(f"❌ Nenhum arquivo encontrado com os padrões: {file_patterns}")
            return {"imported": 0, "failed": 0, "skipped": 0}

        print(f"📁 Encontrados {len(files_to_process)} arquivos para processar")
        print("-" * 50)

        results = {"imported": 0, "failed": 0, "skipped": 0}

        for file_path in files_to_process:
            print(f"\n📄 Processando: {file_path.name}")

            # Verificar se já foi importado
            existing_doc = self._find_existing_document(file_path.name)
            if existing_doc:
                print(f"   ⏭️  Arquivo já importado (ID: {existing_doc[:8]}...)")
                results["skipped"] += 1
                continue

            # Ler conteúdo baseado na extensão
            content = None
            if file_path.suffix.lower() == ".pdf":
                content = self._read_pdf_file(file_path)
            elif file_path.suffix.lower() in [".txt", ".md"]:
                content = self._read_txt_file(file_path)

            if not content:
                print(f"   ❌ Falha ao ler conteúdo")
                results["failed"] += 1
                continue

            # Criar documento
            doc_id = str(uuid.uuid4())
            metadata = {
                "filename": file_path.name,
                "file_path": str(file_path.absolute()),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix.lower(),
                "imported_at": datetime.now().isoformat(),
                "content_length": len(content),
            }

            # Adicionar título se for markdown
            if file_path.suffix.lower() == ".md":
                metadata["type"] = "markdown"
                # Tentar extrair título da primeira linha
                first_line = content.split("\n")[0].strip()
                if first_line.startswith("#"):
                    metadata["title"] = first_line.lstrip("#").strip()

            self.documents[doc_id] = {
                "id": doc_id,
                "content": content,
                "metadata": metadata,
            }

            print(f"   ✅ Importado ({len(content)} caracteres)")
            print(f"   🆔 ID: {doc_id}")
            results["imported"] += 1

        # Salvar documentos
        if results["imported"] > 0:
            try:
                self._save_documents()
                print(f"\n💾 Documentos salvos em: {self.documents_file}")
            except Exception as e:
                print(f"\n❌ Erro ao salvar: {e}")
                return results

        # Mostrar resumo
        print(f"\n" + "=" * 70)
        print("📊 RESUMO DA IMPORTAÇÃO:")
        print(f"   ✅ Importados: {results['imported']}")
        print(f"   ❌ Falharam: {results['failed']}")
        print(f"   ⏭️  Ignorados: {results['skipped']}")
        print(f"   📚 Total na base: {len(self.documents)}")
        print("=" * 70)

        return results

    def _find_existing_document(self, filename: str) -> Optional[str]:
        """Encontrar documento existente pelo nome do arquivo."""
        for doc_id, doc_data in self.documents.items():
            if doc_data.get("metadata", {}).get("filename") == filename:
                return doc_id
        return None

    def list_documents(self):
        """Listar todos os documentos na base."""
        print("=" * 70)
        print(f"DOCUMENTOS NA BASE DE CONHECIMENTO ({len(self.documents)} documentos)")
        print("=" * 70)

        if not self.documents:
            print("❌ Nenhum documento encontrado")
            return

        for i, (doc_id, doc_data) in enumerate(self.documents.items(), 1):
            metadata = doc_data.get("metadata", {})
            content_length = len(doc_data.get("content", ""))

            print(f"\n{i}. 📄 {metadata.get('filename', 'Sem nome')}")
            print(f"   🆔 ID: {doc_id[:8]}...")
            print(f"   📏 Tamanho: {content_length} caracteres")

            if "file_type" in metadata:
                print(f"   📋 Tipo: {metadata['file_type']}")

            if "imported_at" in metadata:
                import_date = metadata["imported_at"][:10]  # YYYY-MM-DD
                print(f"   📅 Importado: {import_date}")

            if "title" in metadata:
                print(f"   📖 Título: {metadata['title']}")

    def clear_documents(self):
        """Limpar todos os documentos (usar com cuidado!)."""
        print("⚠️  ATENÇÃO: Isso irá remover TODOS os documentos da base!")
        confirm = input("Digite 'CONFIRMAR' para continuar: ")

        if confirm == "CONFIRMAR":
            self.documents = {}
            self._save_documents()
            print("✅ Todos os documentos foram removidos")
        else:
            print("❌ Operação cancelada")


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("📚 IMPORTADOR DE DOCUMENTOS PARA RAG")
        print("=" * 70)
        print("\nUso:")
        print("  python import_documents.py <pasta_com_arquivos>")
        print("  python import_documents.py --list")
        print("  python import_documents.py --clear")
        print("\nExemplos:")
        print("  python import_documents.py docs/")
        print("  python import_documents.py C:/Users/João/Documentos/PDFs/")
        print("\nFormatos suportados: PDF, TXT, MD")
        print("\nPara PDFs, instale: pip install pdfplumber PyPDF2")
        print("=" * 70)
        return

    importer = DocumentImporter()

    if sys.argv[1] == "--list":
        importer.list_documents()
    elif sys.argv[1] == "--clear":
        importer.clear_documents()
    else:
        folder_path = sys.argv[1]
        try:
            results = importer.import_files_from_folder(folder_path)

            if results["imported"] > 0:
                print(f"\n🔄 Para aplicar as mudanças, reinicie o backend:")
                print(f"   cd src && python api.py")
        except Exception as e:
            print(f"❌ Erro durante importação: {e}")


if __name__ == "__main__":
    main()
