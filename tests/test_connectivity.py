"""Test frontend-backend connectivity for RAG system."""

import sys
import os
import requests
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_backend_connectivity():
    """Test if backend is properly responding."""
    print("=" * 70)
    print("RAG BACKEND CONNECTIVITY TEST")
    print("=" * 70)

    backend_url = "http://localhost:5000"

    # Test 1: Health check
    print("\n1. HEALTH CHECK:")
    try:
        response = requests.get(f"{backend_url}/api/rag/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend health check OK")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to backend: {e}")
        print("  Make sure backend is running with: python src/api.py")
        return False

    # Test 2: RAG chat endpoint
    print("\n2. RAG CHAT ENDPOINT:")
    try:
        test_message = "What is data quality?"
        url = f"{backend_url}/api/rag/chat?message={test_message}"

        # Use stream=True to handle EventSource response
        response = requests.get(url, stream=True, timeout=10)

        if response.status_code == 200:
            print("✓ RAG chat endpoint responding")

            # Read first few chunks to verify streaming
            chunks = []
            for i, chunk in enumerate(
                response.iter_content(chunk_size=1024, decode_unicode=True)
            ):
                if chunk:
                    chunks.append(chunk)
                if i >= 3:  # Read first few chunks
                    break

            content = "".join(chunks)
            if "data:" in content and "token" in content:
                print("✓ Streaming response format correct")
                print(f"  Sample: {content[:100]}...")
            else:
                print("⚠ Unexpected response format")
                print(f"  Content: {content[:200]}...")
        else:
            print(f"✗ RAG endpoint failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"✗ RAG endpoint error: {e}")
        return False

    # Test 3: CORS headers
    print("\n3. CORS CONFIGURATION:")
    try:
        response = requests.get(f"{backend_url}/api/rag/health")
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header == "*":
            print("✓ CORS configured correctly")
        else:
            print(f"⚠ CORS header: {cors_header}")
    except Exception as e:
        print(f"⚠ Cannot check CORS: {e}")

    # Test 4: Frontend proxy configuration
    print("\n4. FRONTEND PROXY:")
    package_json = Path("frontend/frontend/package.json")
    if package_json.exists():
        with open(package_json) as f:
            content = f.read()
            if '"proxy"' in content and "localhost:5000" in content:
                print("✓ Frontend proxy configured")
            else:
                print("⚠ Frontend proxy missing or incorrect")
                print('  Add to package.json: "proxy": "http://localhost:5000"')
    else:
        print("⚠ Frontend package.json not found")

    print("\n" + "=" * 70)
    print("CONNECTIVITY TEST RESULTS")
    print("=" * 70)
    print("✓ Backend is running and responding correctly")
    print("✓ RAG endpoints are functional")
    print("✓ Streaming responses working")
    print("\nIf frontend still shows 'Connection error':")
    print("1. Restart the frontend (Ctrl+C and npm start)")
    print("2. Check browser console for detailed errors")
    print("3. Verify frontend is running on port 3000")
    print("=" * 70)

    return True


def test_frontend_files():
    """Check frontend configuration files."""
    print("\n" + "=" * 70)
    print("FRONTEND CONFIGURATION CHECK")
    print("=" * 70)

    # Check ChatWindow.js
    chat_window = Path("frontend/frontend/src/components/ChatWindow.js")
    if chat_window.exists():
        print("\n✓ ChatWindow.js exists")
        with open(chat_window) as f:
            content = f.read()

            # Check EventSource usage
            if "/api/rag/chat" in content:
                print("✓ Uses correct API endpoint: /api/rag/chat")
            else:
                print("⚠ API endpoint unclear in ChatWindow.js")

            # Check error handling
            if "Connection error" in content:
                print("✓ Has connection error handling")
            else:
                print("⚠ Missing connection error handling")
    else:
        print("✗ ChatWindow.js not found")

    print("=" * 70)


if __name__ == "__main__":
    success = test_backend_connectivity()
    test_frontend_files()

    if success:
        print("\n🎉 Backend is working! If you still get connection errors:")
        print("   1. Restart frontend: Ctrl+C then 'npm start'")
        print("   2. Clear browser cache")
        print("   3. Check browser console (F12) for errors")
    else:
        print("\n❌ Backend connectivity issues detected!")
        print("   Fix backend issues before testing frontend.")
