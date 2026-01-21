import pytest
from unittest.mock import MagicMock, patch
from backend import Backend, BackendType


@pytest.fixture
def mock_client():
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = '{"invoice": true}'
    client.chat.completions.create.return_value = completion
    return client


class TestBackendCreation:
    def test_openrouter_creation(self):
        backend = Backend(type=BackendType.OPENROUTER)
        assert backend.type == BackendType.OPENROUTER
        assert backend.client is not None
        assert "openrouter.ai/api/v1" in str(backend.client.base_url)

    def test_ollama_creation(self):
        backend = Backend(type=BackendType.OLLAMA)
        assert backend.type == BackendType.OLLAMA
        assert backend.client is not None
        assert "localhost:11434/v1" in str(backend.client.base_url)

    def test_llama_creation(self):
        backend = Backend(type=BackendType.LLAMA)
        assert backend.type == BackendType.LLAMA
        assert backend.client is not None
        assert "localhost:8080/v1" in str(backend.client.base_url)

    def test_llama_custom_url(self):
        backend = Backend(type=BackendType.LLAMA, base_url="http://custom:9000/v1")
        assert backend.client is not None
        assert "http://custom:9000/v1" in str(backend.client.base_url)


class TestInvoiceDetection:
    def test_invoice_or_not_openrouter(self, mock_client):
        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.OPENROUTER)
            backend.client = mock_client
            result = backend.invoice_or_not("test.jpg", "test-model")
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "test-model"

    def test_invoice_or_not_llama(self, mock_client):
        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.LLAMA)
            backend.client = mock_client
            result = backend.invoice_or_not("test.jpg")
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == ""


class TestProcessInvoice:
    def test_process_invoice_is_invoice(self, mock_client):
        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.OPENROUTER)
            backend.client = mock_client
            result = backend.process_invoice("test.jpg", "test-model")
            assert result is not None

    def test_process_invoice_not_invoice(self):
        not_invoice_client = MagicMock()
        not_invoice = MagicMock()
        not_invoice.choices = [MagicMock()]
        not_invoice.choices[0].message.content = '{"invoice": false}'
        not_invoice_client.chat.completions.create.return_value = not_invoice

        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.LLAMA)
            backend.client = not_invoice_client
            result = backend.process_invoice("test.jpg")
            assert result is None


class TestGenerateMethod:
    def test_generate_uses_model_for_openrouter(self, mock_client):
        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.OPENROUTER, model="my-model")
            backend.client = mock_client
            backend.generate("prompt", "test.jpg", {"type": "json_object"})
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "my-model"

    def test_generate_empty_model_for_llama(self, mock_client):
        with patch("base.encode_image", return_value="fake_base64"):
            backend = Backend(type=BackendType.LLAMA, model="some-model")
            backend.client = mock_client
            backend.generate("prompt", "test.jpg", {"type": "json_object"})
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == ""
