"""
Unit tests for P7 Ollama Client module.
Tests connection checks, model availability, single/batch embedding requests,
fallback mechanism, and error handling using mock HTTP responses.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Ensure ai/embeddings is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    OllamaResponseError
)


class TestOllamaClient(unittest.TestCase):

    def setUp(self):
        self.client = OllamaClient(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            timeout=5.0
        )

    def test_client_init_defaults(self):
        c = OllamaClient()
        self.assertEqual(c.base_url, "http://localhost:11434")
        self.assertEqual(c.model, "nomic-embed-text")
        self.assertEqual(c.timeout, 60.0)

    @patch("requests.Session.get")
    def test_is_server_running_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"version": "0.3.14"}
        mock_get.return_value = mock_resp

        self.assertTrue(self.client.is_server_running())
        mock_get.assert_called_with("http://localhost:11434/api/version", timeout=5.0)

    @patch("requests.Session.get")
    def test_is_server_running_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        self.assertFalse(self.client.is_server_running())

    @patch("requests.Session.get")
    def test_list_models_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [
                {"name": "nomic-embed-text:latest"},
                {"name": "all-minilm:latest"}
            ]
        }
        mock_get.return_value = mock_resp

        models = self.client.list_models()
        self.assertEqual(models, ["nomic-embed-text:latest", "all-minilm:latest"])

    @patch("requests.Session.get")
    def test_is_model_available_exact_and_tagged(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [
                {"name": "nomic-embed-text:latest"}
            ]
        }
        mock_get.return_value = mock_resp

        self.assertTrue(self.client.is_model_available("nomic-embed-text"))
        self.assertTrue(self.client.is_model_available("nomic-embed-text:latest"))
        self.assertFalse(self.client.is_model_available("llama3"))

    def test_embed_text_empty_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.client.embed_text("")
        with self.assertRaises(ValueError):
            self.client.embed_text("   \n\t  ")

    @patch("requests.Session.post")
    def test_embed_text_modern_api_embed_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "model": "nomic-embed-text",
            "embeddings": [[0.123, -0.456, 0.789]]
        }
        mock_post.return_value = mock_resp

        vec = self.client.embed_text("Industrial motor temperature")
        self.assertEqual(vec, [0.123, -0.456, 0.789])

    @patch("requests.Session.post")
    def test_embed_text_fallback_to_legacy_embeddings_on_404(self, mock_post):
        # First call to /api/embed returns 404
        resp_404 = MagicMock()
        resp_404.status_code = 404
        resp_404.text = "Not found"

        # Second call to /api/embeddings returns 200
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {
            "embedding": [0.321, -0.654, 0.987]
        }

        mock_post.side_effect = [resp_404, resp_200]

        vec = self.client.embed_text("Centrifugal pump cavitation")
        self.assertEqual(vec, [0.321, -0.654, 0.987])

    @patch("requests.Session.post")
    def test_embed_batch_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "embeddings": [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6]
            ]
        }
        mock_post.return_value = mock_resp

        vectors = self.client.embed_batch(["text one", "text two"])
        self.assertEqual(len(vectors), 2)
        self.assertEqual(vectors[0], [0.1, 0.2, 0.3])
        self.assertEqual(vectors[1], [0.4, 0.5, 0.6])

    @patch("requests.Session.post")
    def test_malformed_response_raises_response_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"invalid_key": []}
        mock_post.return_value = mock_resp

        with self.assertRaises(OllamaResponseError):
            self.client.embed_text("Valid text with invalid response")


if __name__ == "__main__":
    unittest.main()
