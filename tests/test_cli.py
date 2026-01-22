import pytest
from unittest.mock import MagicMock, patch
from main import main
from backend import Backend, BackendType
import argparse
import sys
from io import StringIO


@pytest.fixture
def mock_client():
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = '{"invoice": true, "invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
    client.chat.completions.create.return_value = completion
    return client


class TestMain:
    def test_with_valid_invoice(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test_invoice.jpg"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["type"] == BackendType.LLAMA

    def test_with_non_invoice(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": false}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "non_invoice.jpg"]):
                main()

            mock_backend.invoice_properties.assert_not_called()

    def test_with_custom_url(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg", "--url", "http://custom:9000/v1"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["base_url"] == "http://custom:9000/v1"

    def test_file_not_found(self, capsys):
        with patch.object(sys, "argv", ["main.py", "llama", "nonexistent.jpg"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_invalid_json(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = "not valid json"
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1


class TestDebugFlag:
    def test_debug_output(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg", "--debug"]):
                main()

            captured = capsys.readouterr()
            assert "Connecting to" in captured.out
            assert "Testing invoice detection" in captured.out
            assert "Invoice detected" in captured.out
            assert "Extracted Data" in captured.out

    def test_no_debug_by_default(self, mock_client, capsys):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg"]):
                main()

            captured = capsys.readouterr()
            assert "Connecting to" not in captured.out
            assert "Testing invoice detection" not in captured.out


class TestBackendIntegration:
    def test_uses_llama_backend_by_default(self):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["type"] == BackendType.LLAMA

    def test_passes_model_argument(self):
        with patch("main.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["main.py", "llama", "test.jpg", "--model", "some-model"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["model"] == "some-model"
