"""Quick test of improved RAG responses."""

import requests
import time


def test_improved_chat():
    """Test the improved chat with real questions."""
    print("=" * 70)
    print("TESTING IMPROVED RAG CHAT RESPONSES")
    print("=" * 70)

    base_url = "http://localhost:5000"

    # Test if backend is running
    try:
        health_response = requests.get(f"{base_url}/", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return
        print("✅ Backend is running")

        # Also test RAG endpoint availability
        test_rag = requests.post(
            f"{base_url}/api/rag/chat",
            json={"message": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if test_rag.status_code == 200:
            print("✅ RAG endpoint is accessible")
        else:
            print(f"⚠️  RAG endpoint status: {test_rag.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return

    # Test questions that should now have good responses
    test_questions = [
        "What is data quality testing?",
        "How do I check for null values in PySpark?",
        "What are the main data quality dimensions?",
        "How does DataForgeTest work?",
        "Show me PySpark code to find duplicates",
    ]

    print(f"\n🧪 TESTING {len(test_questions)} QUESTIONS:")
    print("-" * 50)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")

        try:
            # Send the question
            response = requests.post(
                f"{base_url}/api/rag/chat",
                json={"message": question},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    resp_text = data["response"]

                    # Check if it's a generic response
                    if "I don't have specific information" in resp_text:
                        print("   ❌ Still getting generic response")
                        print(f"   📝 Response: {resp_text[:100]}...")
                    else:
                        print("   ✅ Got detailed response!")
                        print(f"   📏 Length: {len(resp_text)} characters")
                        print(f"   📝 Preview: {resp_text[:120]}...")

                        if "citations" in data and data["citations"]:
                            print(f"   📚 Citations: {len(data['citations'])}")

                        # Check for specific keywords we added
                        keywords = [
                            "data quality",
                            "pyspark",
                            "null",
                            "validation",
                            "testing",
                        ]
                        found_keywords = [
                            k for k in keywords if k.lower() in resp_text.lower()
                        ]
                        if found_keywords:
                            print(f"   🎯 Found keywords: {', '.join(found_keywords)}")
                else:
                    print("   ❌ No 'response' field in response")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   📝 Response: {response.text[:100]}...")

        except Exception as e:
            print(f"   ❌ Request failed: {e}")

        # Small delay between requests
        time.sleep(1)

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)
    print("If you see detailed responses above (not generic ones),")
    print("then the RAG system improvement was successful!")
    print("You can now test the frontend interface - it should")
    print("provide much better, more detailed answers.")
    print("=" * 70)


if __name__ == "__main__":
    test_improved_chat()
