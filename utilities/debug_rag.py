"""Debug the RAG system to see what's happening with the knowledge base."""

import requests
import json


def debug_rag_system():
    """Debug the current state of the RAG system."""
    print("=" * 70)
    print("DEBUGGING RAG SYSTEM STATE")
    print("=" * 70)

    base_url = "http://localhost:5000"

    # Test simple direct call to see the response structure
    print("\n📋 TESTING DIRECT RAG RESPONSE:")
    try:
        response = requests.post(
            f"{base_url}/api/rag/chat",
            json={"message": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")

    except Exception as e:
        print(f"Error: {e}")

    # Test specific data quality question
    print(f"\n🧪 TESTING SPECIFIC QUESTION:")
    try:
        response = requests.post(
            f"{base_url}/api/rag/chat",
            json={"message": "data quality"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', '')[:200]}...")
            print(f"Citations: {len(data.get('citations', []))}")

            if data.get("citations"):
                print("Citation sources:")
                for i, citation in enumerate(data["citations"][:3]):
                    print(f"  {i+1}. {citation.get('source', 'unknown')}")
        else:
            print(f"Error status: {response.status_code}")
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    debug_rag_system()
