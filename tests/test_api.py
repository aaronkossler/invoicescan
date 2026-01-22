import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from api import app
    return TestClient(app)


@pytest.fixture
def mock_backend():
    """Create a mock Backend for testing."""
    backend = MagicMock()
    backend.process_invoice.return_value = '{"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}'
    return backend


class TestProcessEndpoint:
    """Tests for the /process endpoint."""

    def test_valid_image_returns_200(self, test_client, mock_backend):
        """Test that a valid image returns 200 with extracted data."""
        with patch("api.Backend", return_value=mock_backend):
            with open("test_invoice.png", "rb") as f:
                response = test_client.post("/process", files={"file": ("test.png", f, "image/png")})

        assert response.status_code == 200
        data = response.json()
        assert "invoice_date" in data
        assert "total_amount" in data
        assert "currency" in data

    def test_non_image_returns_400(self, test_client):
        """Test that non-image files return 400."""
        with open("test.txt", "w") as f:
            f.write("not an image")
        with open("test.txt", "rb") as f:
            response = test_client.post("/process", files={"file": ("test.txt", f, "text/plain")})

        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]

    def test_missing_file_returns_422(self, test_client):
        """Test that missing file returns 422."""
        response = test_client.post("/process", data={})
        assert response.status_code == 422

    def test_process_invoice_returns_none_for_non_invoice(self, test_client):
        """Test that non-invoice images return error message."""
        mock_backend = MagicMock()
        mock_backend.process_invoice.return_value = None

        with patch("api.Backend", return_value=mock_backend):
            with open("test_invoice.png", "rb") as f:
                response = test_client.post("/process", files={"file": ("test.png", f, "image/png")})

        assert response.status_code == 200
        assert response.json()["error"] == "No invoice detected in image"


class TestStaticFiles:
    """Tests for static file serving."""

    def test_index_html_served(self, test_client):
        """Test that index.html is served at root."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_css_file_served(self, test_client):
        """Test that CSS file is served."""
        response = test_client.get("/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

    def test_js_file_served(self, test_client):
        """Test that JS file is served."""
        response = test_client.get("/script.js")
        assert response.status_code == 200
        # FastAPI may serve JS as text/plain, which is acceptable
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type or "text" in content_type

    def test_404_for_missing_static_file(self, test_client):
        """Test that 404 is returned for missing static files."""
        response = test_client.get("/nonexistent.css")
        assert response.status_code == 404


class TestHealthCheck:
    """Basic health check tests."""

    def test_api_returns_200(self, test_client):
        """Test that API root returns 200."""
        response = test_client.get("/")
        assert response.status_code == 200
