import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('app.main.workflow_engine')
    def test_get_workflow_status_found(self, mock_workflow_engine):
        # Mock the get_workflow_status method
        mock_workflow_engine.get_workflow_status.return_value = {
            "workflow_id": "test_id",
            "status": "completed",
        }

        response = self.client.get("/api/workflow/status/test_id")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        mock_workflow_engine.get_workflow_status.assert_called_once_with("test_id")

    @patch('app.main.workflow_engine')
    def test_get_workflow_status_not_found(self, mock_workflow_engine):
        # Mock the get_workflow_status method to return None
        mock_workflow_engine.get_workflow_status.return_value = None

        response = self.client.get("/api/workflow/status/not_found_id")
        self.assertEqual(response.status_code, 404)
        mock_workflow_engine.get_workflow_status.assert_called_once_with("not_found_id")

if __name__ == '__main__':
    unittest.main()
