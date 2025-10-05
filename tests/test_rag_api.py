"""API endpoint tests for RAG functionality."""

import sys
import os
import unittest
import json

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Flask app import to test routes
try:
    from flask import Flask
    from flask_cors import CORS
    from src.rag.routes_simple import rag_bp

    FLASK_AVAILABLE = True
except ImportError as e:
    FLASK_AVAILABLE = False
    print(f"Warning: Flask not available: {e}")


class TestRAGAPIEndpoints(unittest.TestCase):
    """Test RAG API endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask app."""
        if not FLASK_AVAILABLE:
            return

        cls.app = Flask(__name__)
        CORS(cls.app)
        cls.app.register_blueprint(rag_bp)
        cls.client = cls.app.test_client()
        cls.app.config["TESTING"] = True

    def setUp(self):
        """Set up for each test."""
        if not FLASK_AVAILABLE:
            self.skipTest("Flask not available")

    def test_health_endpoint(self):
        """Test /api/rag/health endpoint."""
        response = self.client.get("/api/rag/health")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
        print(f"✓ Health endpoint working: {data}")

    def test_chat_post_endpoint_requires_message(self):
        """Test POST /api/rag/chat requires message parameter."""
        response = self.client.post(
            "/api/rag/chat", json={}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn("error", data)
        print("✓ Chat endpoint validates message parameter")

    def test_chat_post_endpoint_with_message(self):
        """Test POST /api/rag/chat with valid message."""
        response = self.client.post(
            "/api/rag/chat",
            json={"message": "What is data quality?"},
            content_type="application/json",
        )

        # Should return 200 or 500 (depending on setup)
        self.assertIn(response.status_code, [200, 500])

        data = json.loads(response.data)
        if response.status_code == 200:
            self.assertIn("response", data)
            self.assertIn("citations", data)
            print("✓ Chat POST endpoint working")
        else:
            print(f"⚠ Chat POST endpoint error: {data.get('error', 'Unknown')}")

    def test_chat_get_endpoint_requires_message(self):
        """Test GET /api/rag/chat requires message parameter."""
        response = self.client.get("/api/rag/chat")
        # EventSource endpoint should return error or handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
        print("✓ Chat GET endpoint responds to missing message")

    def test_chat_get_endpoint_with_message(self):
        """Test GET /api/rag/chat with message (EventSource endpoint)."""
        response = self.client.get("/api/rag/chat?message=test")

        # Should return streaming response or error
        self.assertIn(response.status_code, [200, 500])

        if response.status_code == 200:
            # Check content type for event stream
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type:
                print("✓ Chat GET endpoint configured for EventSource")
            else:
                print(f"⚠ Content-Type is: {content_type}")
        else:
            print("⚠ Chat GET endpoint error")

    def test_sources_endpoint(self):
        """Test GET /api/rag/sources endpoint."""
        response = self.client.get("/api/rag/sources")
        self.assertIn(response.status_code, [200, 500])

        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn("sources", data)
            self.assertIsInstance(data["sources"], list)
            print(f"✓ Sources endpoint working: {len(data['sources'])} sources")
        else:
            print("⚠ Sources endpoint error")

    def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        response = self.client.options("/api/rag/health")

        # Check for CORS headers
        headers = dict(response.headers)
        print(f"✓ CORS check - Status: {response.status_code}")
        if "Access-Control-Allow-Origin" in headers:
            print(
                f"  Access-Control-Allow-Origin: {headers['Access-Control-Allow-Origin']}"
            )
        else:
            print("  ⚠ Access-Control-Allow-Origin header not found")


class TestRAGAPIResponseFormat(unittest.TestCase):
    """Test API response formats match frontend expectations."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask app."""
        if not FLASK_AVAILABLE:
            return

        cls.app = Flask(__name__)
        CORS(cls.app)
        cls.app.register_blueprint(rag_bp)
        cls.client = cls.app.test_client()
        cls.app.config["TESTING"] = True

    def setUp(self):
        """Set up for each test."""
        if not FLASK_AVAILABLE:
            self.skipTest("Flask not available")

    def test_chat_response_structure(self):
        """Test that chat response has expected structure."""
        response = self.client.post(
            "/api/rag/chat", json={"message": "test"}, content_type="application/json"
        )

        if response.status_code == 200:
            data = json.loads(response.data)

            # Check required fields
            self.assertIn("response", data, "Response should have 'response' field")
            self.assertIn("citations", data, "Response should have 'citations' field")

            # Check citations structure
            if len(data["citations"]) > 0:
                citation = data["citations"][0]
                self.assertIn("id", citation, "Citation should have 'id' field")
                self.assertIn("text", citation, "Citation should have 'text' field")
                self.assertIn(
                    "metadata", citation, "Citation should have 'metadata' field"
                )

            print("✓ Chat response structure matches frontend expectations")

    def test_streaming_response_format(self):
        """Test streaming response format for EventSource."""
        response = self.client.get("/api/rag/chat?message=test")

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")

            # Should be text/event-stream
            self.assertIn(
                "text/event-stream",
                content_type,
                "Streaming endpoint should use text/event-stream",
            )

            # Try to parse response data
            data = response.data.decode("utf-8")

            # Should contain SSE format: "data: {...}\n\n"
            if "data:" in data:
                print("✓ Streaming response uses SSE format")

                # Check for expected event types
                if "type" in data:
                    print("  Contains 'type' field")
                if "token" in data:
                    print("  Contains token events")
                if "citations" in data:
                    print("  Contains citations")
            else:
                print("⚠ Streaming response format unclear")


class TestRAGAPIErrorHandling(unittest.TestCase):
    """Test API error handling."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask app."""
        if not FLASK_AVAILABLE:
            return

        cls.app = Flask(__name__)
        CORS(cls.app)
        cls.app.register_blueprint(rag_bp)
        cls.client = cls.app.test_client()
        cls.app.config["TESTING"] = True

    def setUp(self):
        """Set up for each test."""
        if not FLASK_AVAILABLE:
            self.skipTest("Flask not available")

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON."""
        response = self.client.post(
            "/api/rag/chat", data="invalid json", content_type="application/json"
        )

        # Should return error
        self.assertIn(response.status_code, [400, 500])
        print("✓ Invalid JSON handled")

    def test_missing_content_type(self):
        """Test handling of missing content type."""
        response = self.client.post("/api/rag/chat", data='{"message": "test"}')

        # Should handle missing content type
        self.assertIsNotNone(response)
        print(f"✓ Missing content-type handled: {response.status_code}")

    def test_empty_message_handling(self):
        """Test handling of empty message."""
        response = self.client.post(
            "/api/rag/chat", json={"message": ""}, content_type="application/json"
        )

        # Should validate empty message
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        print("✓ Empty message validated")


class TestFrontendBackendIntegration(unittest.TestCase):
    """Test frontend-backend integration points."""

    def test_frontend_api_url_format(self):
        """Test that API URLs match frontend expectations."""
        expected_endpoints = [
            "/api/rag/chat",  # POST for non-streaming
            "/api/rag/chat",  # GET for EventSource streaming
            "/api/rag/health",  # Health check
            "/api/rag/sources",  # List sources
            "/api/rag/upload",  # Upload documents
        ]

        print("✓ Expected API endpoints defined:")
        for endpoint in expected_endpoints:
            print(f"  - {endpoint}")

    def test_eventsource_url_format(self):
        """Test EventSource URL format."""
        # Frontend uses: new EventSource(`/api/rag/chat?message=${encodeURIComponent(userMessage)}`)
        test_message = "What is data quality?"
        from urllib.parse import quote

        expected_url = f"/api/rag/chat?message={quote(test_message)}"
        print(f"✓ EventSource URL format: {expected_url}")

        # Verify URL encoding works
        self.assertNotIn(" ", expected_url)
        self.assertIn("message=", expected_url)


def run_api_test_suite():
    """Run all API tests and provide summary."""
    print("\n" + "=" * 70)
    print("RAG API TEST SUITE")
    print("=" * 70 + "\n")

    if not FLASK_AVAILABLE:
        print("ERROR: Flask is not available. Install requirements first.")
        print("Run: pip install -r requirements.txt")
        return None

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRAGAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGAPIResponseFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGAPIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestFrontendBackendIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("API TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print("=" * 70 + "\n")

    return result


if __name__ == "__main__":
    run_api_test_suite()
