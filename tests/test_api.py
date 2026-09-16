"""
FastAPI route unit tests
"""
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.routes import app


class TestAPI(unittest.TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("version", data)
        self.assertEqual(data["name"], "RAG Stock Analyst API")
    
    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)


if __name__ == "__main__":
    unittest.main()
