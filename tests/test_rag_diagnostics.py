"""Comprehensive RAG system diagnostics to identify connection issues."""

import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class RAGDiagnostics:
    """Comprehensive diagnostics for RAG system."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []

    def add_issue(self, category, message):
        """Add a critical issue."""
        self.issues.append(f"[{category}] {message}")

    def add_warning(self, category, message):
        """Add a warning."""
        self.warnings.append(f"[{category}] {message}")

    def add_success(self, category, message):
        """Add a success."""
        self.successes.append(f"[{category}] {message}")

    def check_environment(self):
        """Check environment configuration."""
        print("\n1. ENVIRONMENT CONFIGURATION")
        print("-" * 70)

        # Check for .env file
        env_file = Path(".env")
        if env_file.exists():
            self.add_success("ENV", ".env file exists")
            print("✓ .env file found")

            # Try to read it
            try:
                with open(env_file) as f:
                    content = f.read()

                # Check for required variables
                required_vars = ["LLM_API_KEY", "VECTOR_STORE_PATH", "LLM_MODEL"]

                for var in required_vars:
                    if var in content:
                        # Don't print actual values for security
                        if (
                            f"{var}=" in content
                            and f"{var}=\n" not in content
                            and f"{var}= " not in content
                        ):
                            self.add_success("ENV", f"{var} is set")
                            print(f"✓ {var} is configured")
                        else:
                            self.add_warning("ENV", f"{var} is defined but empty")
                            print(f"⚠ {var} is empty")
                    else:
                        self.add_warning("ENV", f"{var} not found in .env")
                        print(f"⚠ {var} not found")

            except Exception as e:
                self.add_warning("ENV", f"Error reading .env: {e}")
        else:
            self.add_warning("ENV", ".env file not found")
            print("⚠ .env file not found")
            print(
                "  Note: Simple RAG system works without LLM API, but won't use Claude"
            )

    def check_dependencies(self):
        """Check Python dependencies."""
        print("\n2. PYTHON DEPENDENCIES")
        print("-" * 70)

        required_packages = {
            "flask": "Flask",
            "flask_cors": "Flask-CORS",
            "pyspark": "PySpark",
        }

        optional_packages = {
            "anthropic": "Anthropic (for Claude)",
            "openai": "OpenAI",
            "llama_index": "LlamaIndex",
            "PyPDF2": "PyPDF2 (for PDF processing)",
            "pandas": "Pandas",
            "python-dotenv": "python-dotenv",
        }

        for package, name in required_packages.items():
            try:
                __import__(package)
                self.add_success("DEP", f"{name} installed")
                print(f"✓ {name} installed")
            except ImportError:
                self.add_issue("DEP", f"{name} not installed")
                print(f"✗ {name} NOT INSTALLED (required)")

        for package, name in optional_packages.items():
            try:
                # Handle special case for python-dotenv
                if package == "python-dotenv":
                    __import__("dotenv")
                else:
                    __import__(package.replace("-", "_"))
                self.add_success("DEP", f"{name} installed")
                print(f"✓ {name} installed")
            except ImportError:
                self.add_warning("DEP", f"{name} not installed")
                print(f"⚠ {name} not installed (optional)")

    def check_rag_modules(self):
        """Check RAG module imports."""
        print("\n3. RAG MODULE IMPORTS")
        print("-" * 70)

        modules = [
            ("src.rag.config_simple", "RAGConfig (Simple)"),
            ("src.rag.simple_rag", "SimpleRAG"),
            ("src.rag.simple_chat", "SimpleChatEngine"),
            ("src.rag.routes_simple", "Routes (Simple)"),
        ]

        for module_path, name in modules:
            try:
                __import__(module_path)
                self.add_success("MODULE", f"{name} imports successfully")
                print(f"✓ {name} imports OK")
            except ImportError as e:
                self.add_issue("MODULE", f"{name} import failed: {e}")
                print(f"✗ {name} import FAILED: {e}")
            except Exception as e:
                self.add_issue("MODULE", f"{name} error: {e}")
                print(f"✗ {name} ERROR: {e}")

    def check_rag_initialization(self):
        """Check RAG system can be initialized."""
        print("\n4. RAG SYSTEM INITIALIZATION")
        print("-" * 70)

        try:
            from src.rag.config_simple import RAGConfig
            from src.rag.simple_rag import SimpleRAG
            from src.rag.simple_chat import SimpleChatEngine

            # Initialize config
            config = RAGConfig.from_env()
            self.add_success("INIT", "Config loaded")
            print("✓ Config loaded")
            print(f"  Storage path: {config.storage_path}")
            print(f"  Chunk size: {config.chunk_size}")
            print(f"  Top K: {config.top_k}")

            # Initialize RAG
            rag_system = SimpleRAG(config)
            self.add_success("INIT", "RAG system initialized")
            print("✓ RAG system initialized")
            print(f"  Documents: {len(rag_system.documents)}")
            print(f"  Chunks: {len(rag_system.document_chunks)}")

            # Initialize chat engine
            chat_engine = SimpleChatEngine(rag_system)
            self.add_success("INIT", "Chat engine initialized")
            print("✓ Chat engine initialized")

            # Test basic functionality
            test_content = "Test document about data quality"
            doc_id = rag_system.add_document(test_content, {"filename": "test.txt"})
            self.add_success("INIT", "Document added successfully")
            print(f"✓ Test document added: {doc_id}")

            # Test search
            results = rag_system.search("data quality")
            self.add_success("INIT", f"Search working ({len(results)} results)")
            print(f"✓ Search working: {len(results)} results")

            # Test chat
            response = chat_engine.chat("What is data quality?")
            if response and "response" in response:
                self.add_success("INIT", "Chat working")
                print("✓ Chat working")
                print(f"  Response length: {len(response['response'])} chars")
                print(f"  Citations: {len(response.get('citations', []))}")
            else:
                self.add_warning("INIT", "Chat returned unexpected format")
                print("⚠ Chat response format unexpected")

        except Exception as e:
            self.add_issue("INIT", f"Initialization failed: {e}")
            print(f"✗ Initialization FAILED: {e}")
            import traceback

            traceback.print_exc()

    def check_api_routes(self):
        """Check API routes configuration."""
        print("\n5. API ROUTES CONFIGURATION")
        print("-" * 70)

        try:
            # Check if Flask is available
            try:

                self.add_success("API", "Flask available")
                print("✓ Flask available")
            except ImportError:
                self.add_issue("API", "Flask not installed")
                print("✗ Flask NOT INSTALLED")
                return

            # Check if routes module loads
            try:

                self.add_success("API", "Routes blueprint loaded")
                print("✓ Routes blueprint loaded")
            except Exception as e:
                self.add_issue("API", f"Routes failed to load: {e}")
                print(f"✗ Routes FAILED: {e}")
                return

            # Check if main API file exists
            api_file = Path("src/api.py")
            if api_file.exists():
                self.add_success("API", "api.py exists")
                print("✓ api.py exists")

                # Check if it registers RAG blueprint
                with open(api_file) as f:
                    content = f.read()
                    if "rag_bp" in content and "register_blueprint" in content:
                        self.add_success("API", "RAG blueprint registered")
                        print("✓ RAG blueprint registered in api.py")
                    else:
                        self.add_warning("API", "RAG blueprint might not be registered")
                        print("⚠ RAG blueprint registration unclear")
            else:
                self.add_issue("API", "api.py not found")
                print("✗ api.py NOT FOUND")

        except Exception as e:
            self.add_issue("API", f"API check failed: {e}")
            print(f"✗ API check FAILED: {e}")

    def check_frontend_config(self):
        """Check frontend configuration."""
        print("\n6. FRONTEND CONFIGURATION")
        print("-" * 70)

        # Check if ChatWindow.js exists
        chat_window = Path("frontend//src/components/ChatWindow.js")
        if chat_window.exists():
            self.add_success("FRONTEND", "ChatWindow.js exists")
            print("✓ ChatWindow.js exists")

            with open(chat_window) as f:
                content = f.read()

                # Check for EventSource usage
                if "EventSource" in content:
                    self.add_success("FRONTEND", "Uses EventSource for streaming")
                    print("✓ Uses EventSource for streaming")

                    # Check API endpoint
                    if "/api/rag/chat" in content:
                        self.add_success("FRONTEND", "Calls /api/rag/chat")
                        print("✓ Calls /api/rag/chat endpoint")
                    else:
                        self.add_warning("FRONTEND", "API endpoint unclear")
                        print("⚠ API endpoint unclear")
                else:
                    self.add_warning("FRONTEND", "EventSource not found")
                    print("⚠ EventSource not found in ChatWindow.js")
        else:
            self.add_issue("FRONTEND", "ChatWindow.js not found")
            print("✗ ChatWindow.js NOT FOUND")

        # Check SupportPage.js
        support_page = Path("frontend//src/pages/SupportPage.js")
        if support_page.exists():
            self.add_success("FRONTEND", "SupportPage.js exists")
            print("✓ SupportPage.js exists")
        else:
            self.add_warning("FRONTEND", "SupportPage.js not found")
            print("⚠ SupportPage.js not found")

    def check_storage(self):
        """Check storage configuration."""
        print("\n7. STORAGE CONFIGURATION")
        print("-" * 70)

        try:
            from src.rag.config_simple import RAGConfig

            config = RAGConfig.from_env()

            storage_path = config.storage_path
            print(f"Storage path: {storage_path}")

            # Check if directory exists or can be created
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
                self.add_success("STORAGE", "Storage directory accessible")
                print("✓ Storage directory accessible")

                # Check write permissions
                test_file = storage_path / ".test_write"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    self.add_success("STORAGE", "Write permissions OK")
                    print("✓ Write permissions OK")
                except Exception as e:
                    self.add_issue("STORAGE", f"Write permission error: {e}")
                    print(f"✗ Write permission ERROR: {e}")

            except Exception as e:
                self.add_issue("STORAGE", f"Cannot create storage directory: {e}")
                print(f"✗ Cannot create storage directory: {e}")

        except Exception as e:
            self.add_issue("STORAGE", f"Storage check failed: {e}")
            print(f"✗ Storage check FAILED: {e}")

    def check_known_issues(self):
        """Check for known issues."""
        print("\n8. KNOWN ISSUES CHECK")
        print("-" * 70)

        # Check if using simple RAG vs full RAG
        try:
            # Read the api.py file directly instead of inspecting the Flask app
            api_file = Path("src/api.py")
            if api_file.exists():
                with open(api_file) as f:
                    source = f.read()
            else:
                self.add_warning("SYSTEM", "api.py file not found")
                print("⚠ api.py file not found")
                return

            if "routes_simple" in source:
                self.add_warning("SYSTEM", "Using Simple RAG (no LLM integration)")
                print("⚠ Using Simple RAG implementation")
                print("  This uses keyword-based search, NOT Claude Sonnet LLM")
                print("  To use Claude, you need:")
                print("    1. Set LLM_API_KEY in .env")
                print("    2. Switch to routes.py (full RAG)")
                print("    3. Install llama-index and anthropic packages")
            elif "routes.py" in source or "rag_bp" in source:
                self.add_success("SYSTEM", "Using full RAG routes")
                print("✓ Using full RAG implementation")
            else:
                self.add_warning("SYSTEM", "RAG route type unclear")
                print("⚠ Cannot determine RAG implementation")

        except Exception as e:
            self.add_warning("SYSTEM", f"Cannot check RAG type: {e}")
            print(f"⚠ Cannot determine RAG type: {e}")

    def generate_report(self):
        """Generate final diagnostic report."""
        print("\n" + "=" * 70)
        print("DIAGNOSTIC REPORT")
        print("=" * 70)

        print(f"\n✓ SUCCESSES: {len(self.successes)}")
        for success in self.successes[:10]:  # Show first 10
            print(f"  {success}")
        if len(self.successes) > 10:
            print(f"  ... and {len(self.successes) - 10} more")

        print(f"\n⚠ WARNINGS: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"  {warning}")

        print(f"\n✗ CRITICAL ISSUES: {len(self.issues)}")
        for issue in self.issues:
            print(f"  {issue}")

        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)

        if len(self.issues) > 0:
            print("\n🔴 CRITICAL: Fix these issues first:")
            for issue in self.issues:
                print(f"  - {issue}")

        if len(self.warnings) > 0:
            print("\n🟡 WARNINGS: Consider addressing these:")
            for warning in self.warnings[:5]:  # Top 5 warnings
                print(f"  - {warning}")

        # Specific recommendations
        print("\n💡 SPECIFIC RECOMMENDATIONS:")

        # Check if using simple RAG
        has_llm_warning = any("Simple RAG" in w for w in self.warnings)
        if has_llm_warning:
            print("\n  The system is using Simple RAG (keyword search) not Claude LLM:")
            print("    1. Create .env file with LLM_API_KEY=your_anthropic_key")
            print(
                "    2. Install: pip install llama-index-llms-anthropic llama-index-embeddings-openai"
            )
            print("    3. Edit src/api.py: change 'routes_simple' to 'routes'")
            print("    4. Restart the backend")

        # Check for missing dependencies
        dep_issues = [i for i in self.issues if "DEP" in i]
        if dep_issues:
            print("\n  Install missing dependencies:")
            print("    pip install -r requirements.txt")

        # Check for API issues
        api_issues = [i for i in self.issues if "API" in i]
        if api_issues:
            print("\n  Fix API configuration:")
            print("    Ensure Flask and Flask-CORS are installed")
            print("    Check src/api.py for correct blueprint registration")

        print("\n" + "=" * 70 + "\n")

    def run_all_checks(self):
        """Run all diagnostic checks."""
        print("=" * 70)
        print("RAG SYSTEM COMPREHENSIVE DIAGNOSTICS")
        print("=" * 70)

        self.check_environment()
        self.check_dependencies()
        self.check_rag_modules()
        self.check_rag_initialization()
        self.check_api_routes()
        self.check_frontend_config()
        self.check_storage()
        self.check_known_issues()
        self.generate_report()


if __name__ == "__main__":
    diagnostics = RAGDiagnostics()
    diagnostics.run_all_checks()
