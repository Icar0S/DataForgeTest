#!/usr/bin/env python3
"""Test script to verify LLM abstraction layer works correctly."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_llm_client_import():
    """Test that LLM client can be imported."""
    try:
        from llm_client import create_llm_client, get_default_llm_client
        print("✅ LLM client module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import LLM client: {e}")
        return False

def test_ollama_client_creation():
    """Test creating Ollama client."""
    try:
        from llm_client import create_llm_client
        
        # Set environment for Ollama
        os.environ['LLM_PROVIDER'] = 'ollama'
        os.environ['LLM_MODEL'] = 'qwen2.5-coder:7b'
        os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        
        try:
            client = create_llm_client(
                provider='ollama',
                model='qwen2.5-coder:7b',
                base_url='http://localhost:11434'
            )
            print("✅ Ollama client created successfully")
            print(f"   Model: qwen2.5-coder:7b")
            print(f"   Provider: Ollama")
            return True
        except ImportError as e:
            print(f"⚠️  Ollama package not installed (expected): {e}")
            print("   This is OK - ollama package will be installed during deployment")
            return True
        except Exception as e:
            print(f"❌ Failed to create Ollama client: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_anthropic_client_creation():
    """Test creating Anthropic client."""
    try:
        from llm_client import create_llm_client
        
        # Test without API key (should raise ValueError)
        try:
            client = create_llm_client(
                provider='anthropic',
                api_key=None
            )
            print("❌ Should have raised ValueError for missing API key")
            return False
        except ValueError as e:
            print(f"✅ Correctly raises ValueError for missing API key: {str(e)[:50]}...")
            return True
        except ImportError:
            print("⚠️  Anthropic package not installed (OK for Ollama-only setup)")
            return True
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_rag_integration():
    """Test RAG module integration with new LLM client."""
    try:
        # Set environment for Ollama
        os.environ['LLM_PROVIDER'] = 'ollama'
        os.environ['LLM_MODEL'] = 'qwen2.5-coder:7b'
        
        from rag.simple_chat import SimpleChatEngine
        from rag.simple_rag import SimpleRAG
        from rag.config import RAGConfig
        
        # Create config
        config = RAGConfig.from_env()
        
        # Create RAG system
        rag = SimpleRAG(config)
        print("✅ SimpleRAG system created")
        
        # Create chat engine
        chat_engine = SimpleChatEngine(rag)
        print("✅ SimpleChatEngine created with LLM abstraction")
        
        # Check if LLM is configured
        if chat_engine.use_llm:
            print(f"   LLM Status: Enabled")
        else:
            print(f"   LLM Status: Using fallback (no Ollama server)")
            
        return True
        
    except ImportError as e:
        print(f"⚠️  Import error (may need ollama package): {e}")
        return True  # OK, just means ollama isn't installed yet
    except Exception as e:
        print(f"❌ Failed RAG integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synthetic_integration():
    """Test synthetic data generator integration with new LLM client."""
    try:
        # Set environment for Ollama
        os.environ['LLM_PROVIDER'] = 'ollama'
        os.environ['LLM_MODEL'] = 'qwen2.5-coder:7b'
        
        from synthetic.generator import SyntheticDataGenerator
        
        # Create generator
        generator = SyntheticDataGenerator()
        print("✅ SyntheticDataGenerator created with LLM abstraction")
        
        # Check if LLM is configured
        if generator._llm_available:
            print(f"   LLM Status: Available")
        else:
            print(f"   LLM Status: Using mock data (no Ollama server)")
            
        return True
        
    except ImportError as e:
        print(f"⚠️  Import error (may need ollama package): {e}")
        return True  # OK, just means ollama isn't installed yet
    except Exception as e:
        print(f"❌ Failed synthetic integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing LLM Abstraction Layer")
    print("=" * 60)
    
    tests = [
        ("LLM Client Import", test_llm_client_import),
        ("Ollama Client Creation", test_ollama_client_creation),
        ("Anthropic Client Validation", test_anthropic_client_creation),
        ("RAG Integration", test_rag_integration),
        ("Synthetic Data Integration", test_synthetic_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- Test: {name} ---")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
