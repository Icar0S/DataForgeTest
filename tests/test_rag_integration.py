"""Integration tests for RAG functionality to diagnose connection issues."""
import sys
import os
import unittest
import json
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.config_simple import RAGConfig
from src.rag.simple_rag import SimpleRAG
from src.rag.simple_chat import SimpleChatEngine


class TestRAGConfiguration(unittest.TestCase):
    """Test RAG configuration and initialization."""

    def test_config_loads_from_env(self):
        """Test that RAG configuration can be loaded."""
        try:
            config = RAGConfig.from_env()
            self.assertIsNotNone(config)
            self.assertIsInstance(config.storage_path, Path)
            self.assertGreater(config.chunk_size, 0)
            self.assertGreater(config.top_k, 0)
            print(f"✓ Config loaded: storage={config.storage_path}, chunk_size={config.chunk_size}")
        except Exception as e:
            self.fail(f"Failed to load config: {str(e)}")

    def test_storage_path_creation(self):
        """Test that storage path can be created."""
        config = RAGConfig.from_env()
        try:
            config.storage_path.mkdir(parents=True, exist_ok=True)
            self.assertTrue(config.storage_path.exists())
            print(f"✓ Storage path created: {config.storage_path}")
        except Exception as e:
            self.fail(f"Failed to create storage path: {str(e)}")


class TestRAGSystemInitialization(unittest.TestCase):
    """Test RAG system initialization."""

    def setUp(self):
        """Set up test environment."""
        self.config = RAGConfig.from_env()

    def test_rag_system_initializes(self):
        """Test that RAG system can be initialized."""
        try:
            rag_system = SimpleRAG(self.config)
            self.assertIsNotNone(rag_system)
            self.assertIsNotNone(rag_system.documents)
            self.assertIsNotNone(rag_system.document_chunks)
            print("✓ RAG system initialized successfully")
        except Exception as e:
            self.fail(f"Failed to initialize RAG system: {str(e)}")

    def test_chat_engine_initializes(self):
        """Test that chat engine can be initialized."""
        try:
            rag_system = SimpleRAG(self.config)
            chat_engine = SimpleChatEngine(rag_system)
            self.assertIsNotNone(chat_engine)
            self.assertIsNotNone(chat_engine.rag)
            self.assertIsInstance(chat_engine.chat_history, list)
            print("✓ Chat engine initialized successfully")
        except Exception as e:
            self.fail(f"Failed to initialize chat engine: {str(e)}")


class TestRAGDocumentOperations(unittest.TestCase):
    """Test RAG document operations."""

    def setUp(self):
        """Set up test environment."""
        self.config = RAGConfig.from_env()
        self.rag_system = SimpleRAG(self.config)

    def test_add_document(self):
        """Test adding a document to RAG system."""
        test_content = "This is a test document about data quality testing."
        test_metadata = {"filename": "test.txt", "size": len(test_content)}
        
        try:
            doc_id = self.rag_system.add_document(test_content, test_metadata)
            self.assertIsNotNone(doc_id)
            self.assertIn(doc_id, self.rag_system.documents)
            print(f"✓ Document added successfully with ID: {doc_id}")
        except Exception as e:
            self.fail(f"Failed to add document: {str(e)}")

    def test_search_documents(self):
        """Test searching documents."""
        # Add a test document first
        test_content = "Data quality is essential for accurate analytics and reporting."
        test_metadata = {"filename": "quality.txt", "size": len(test_content)}
        self.rag_system.add_document(test_content, test_metadata)
        
        try:
            results = self.rag_system.search("data quality", top_k=5)
            self.assertIsInstance(results, list)
            print(f"✓ Search returned {len(results)} results")
            
            if len(results) > 0:
                result = results[0]
                self.assertIn('text', result)
                self.assertIn('score', result)
                self.assertIn('metadata', result)
                print(f"✓ Search result structure is valid")
        except Exception as e:
            self.fail(f"Failed to search documents: {str(e)}")

    def test_get_sources(self):
        """Test getting document sources."""
        try:
            sources = self.rag_system.get_sources()
            self.assertIsInstance(sources, list)
            print(f"✓ Retrieved {len(sources)} document sources")
        except Exception as e:
            self.fail(f"Failed to get sources: {str(e)}")


class TestChatEngineOperations(unittest.TestCase):
    """Test chat engine operations."""

    def setUp(self):
        """Set up test environment."""
        self.config = RAGConfig.from_env()
        self.rag_system = SimpleRAG(self.config)
        self.chat_engine = SimpleChatEngine(self.rag_system)
        
        # Add a test document
        test_content = """
        Data quality testing ensures that data meets the required standards.
        It includes validation of accuracy, completeness, consistency, and reliability.
        Testing should be performed regularly to maintain data integrity.
        """
        test_metadata = {"filename": "test_guide.txt", "size": len(test_content)}
        self.rag_system.add_document(test_content, test_metadata)

    def test_chat_basic_query(self):
        """Test basic chat query."""
        try:
            response = self.chat_engine.chat("What is data quality testing?")
            self.assertIsInstance(response, dict)
            self.assertIn('response', response)
            self.assertIn('citations', response)
            self.assertIsInstance(response['response'], str)
            self.assertIsInstance(response['citations'], list)
            print(f"✓ Chat query successful")
            print(f"  Response length: {len(response['response'])} chars")
            print(f"  Citations count: {len(response['citations'])}")
        except Exception as e:
            self.fail(f"Failed to execute chat query: {str(e)}")

    def test_chat_with_no_context(self):
        """Test chat query with no relevant context."""
        try:
            response = self.chat_engine.chat("What is quantum computing?")
            self.assertIsInstance(response, dict)
            self.assertIn('response', response)
            # Should return a message about no specific information
            print(f"✓ Chat handles queries without context")
        except Exception as e:
            self.fail(f"Failed to handle query without context: {str(e)}")

    def test_chat_history(self):
        """Test chat history tracking."""
        try:
            self.chat_engine.chat("First question")
            self.chat_engine.chat("Second question")
            
            history = self.chat_engine.get_history()
            self.assertEqual(len(history), 2)
            print(f"✓ Chat history tracked correctly: {len(history)} entries")
        except Exception as e:
            self.fail(f"Failed to track chat history: {str(e)}")

    def test_clear_history(self):
        """Test clearing chat history."""
        try:
            self.chat_engine.chat("Test question")
            self.chat_engine.clear_history()
            
            history = self.chat_engine.get_history()
            self.assertEqual(len(history), 0)
            print("✓ Chat history cleared successfully")
        except Exception as e:
            self.fail(f"Failed to clear chat history: {str(e)}")


class TestRAGEndpointCompatibility(unittest.TestCase):
    """Test RAG endpoint compatibility with frontend expectations."""

    def setUp(self):
        """Set up test environment."""
        self.config = RAGConfig.from_env()
        self.rag_system = SimpleRAG(self.config)
        self.chat_engine = SimpleChatEngine(self.rag_system)

    def test_response_format_matches_frontend(self):
        """Test that response format matches what frontend expects."""
        # Add test document
        test_content = "Test content about data validation"
        self.rag_system.add_document(test_content, {"filename": "test.txt"})
        
        response = self.chat_engine.chat("test query")
        
        # Frontend expects 'response' and 'citations' keys
        self.assertIn('response', response)
        self.assertIn('citations', response)
        
        # Check citations format
        if len(response['citations']) > 0:
            citation = response['citations'][0]
            self.assertIn('id', citation)
            self.assertIn('text', citation)
            self.assertIn('metadata', citation)
            print("✓ Response format matches frontend expectations")

    def test_streaming_response_format(self):
        """Test that response can be formatted for streaming."""
        try:
            response = self.chat_engine.chat("test query")
            
            # Simulate streaming format
            words = response['response'].split()
            for word in words[:5]:  # Test first 5 words
                stream_chunk = {
                    'type': 'token',
                    'content': word + ' '
                }
                json_str = json.dumps(stream_chunk)
                self.assertIsInstance(json_str, str)
            
            # Test citations format
            citation_chunk = {
                'type': 'citations',
                'content': {'citations': response['citations']}
            }
            json_str = json.dumps(citation_chunk)
            self.assertIsInstance(json_str, str)
            
            print("✓ Streaming response format is valid")
        except Exception as e:
            self.fail(f"Failed to format streaming response: {str(e)}")


class TestRAGDiagnostics(unittest.TestCase):
    """Diagnostic tests to identify common issues."""

    def test_storage_permissions(self):
        """Test that storage directory has proper permissions."""
        config = RAGConfig.from_env()
        storage_path = config.storage_path
        
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
            # Try to write a test file
            test_file = storage_path / "test_write.txt"
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            print(f"✓ Storage directory has write permissions: {storage_path}")
        except Exception as e:
            self.fail(f"Storage permission issue: {str(e)}")

    def test_document_persistence(self):
        """Test that documents persist across instances."""
        config = RAGConfig.from_env()
        
        # First instance - add document
        rag1 = SimpleRAG(config)
        test_content = "Persistence test content"
        doc_id = rag1.add_document(test_content, {"filename": "persist.txt"})
        
        # Second instance - should load the document
        rag2 = SimpleRAG(config)
        self.assertIn(doc_id, rag2.documents)
        print("✓ Documents persist across instances")

    def test_empty_query_handling(self):
        """Test handling of empty queries."""
        config = RAGConfig.from_env()
        rag_system = SimpleRAG(config)
        chat_engine = SimpleChatEngine(rag_system)
        
        try:
            response = chat_engine.chat("")
            self.assertIsNotNone(response)
            print("✓ Empty query handled gracefully")
        except Exception as e:
            print(f"⚠ Empty query causes error: {str(e)}")


def run_diagnostic_suite():
    """Run all diagnostic tests and provide summary."""
    print("\n" + "="*70)
    print("RAG SYSTEM DIAGNOSTIC TEST SUITE")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRAGConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGSystemInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGDocumentOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestChatEngineOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGEndpointCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGDiagnostics))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70 + "\n")
    
    return result


if __name__ == "__main__":
    run_diagnostic_suite()
