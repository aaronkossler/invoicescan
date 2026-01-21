import pytest
from unittest.mock import MagicMock, patch
from cli import main
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


class TestCliMain:
    def test_cli_with_valid_invoice(self, mock_client, capsys):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "test_invoice.jpg"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["type"] == BackendType.LLAMA

    def test_cli_with_non_invoice(self, mock_client, capsys):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": false}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "non_invoice.jpg"]):
                main()

            mock_backend.invoice_properties.assert_not_called()

    def test_cli_with_custom_url(self, mock_client, capsys):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "test.jpg", "--url", "http://custom:9000/v1"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["base_url"] == "http://custom:9000/v1"

    def test_cli_file_not_found(self, capsys):
        with patch.object(sys, "argv", ["cli.py", "nonexistent.jpg"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_invalid_json(self, mock_client, capsys):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = "not valid json"
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "test.jpg"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1


class TestCliBackendIntegration:
    def test_cli_uses_llama_backend_by_default(self):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "test.jpg"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["type"] == BackendType.LLAMA

    def test_cli_passes_model_argument(self):
        with patch("cli.Backend") as mock_backend_class:
            mock_backend = MagicMock()
            mock_backend.invoice_or_not.return_value = '{"invoice": true}'
            mock_backend.invoice_properties.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
            mock_backend_class.return_value = mock_backend

            with patch.object(sys, "argv", ["cli.py", "test.jpg", "--model", "some-model"]):
                main()

            mock_backend_class.assert_called_once()
            call_kwargs = mock_backend_class.call_args[1]
            assert call_kwargs["model"] == "some-model"
