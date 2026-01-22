# InvoiceScan

An invoice processing system that uses AI to identify invoices and extract key information from document images.

## Overview

InvoiceScan leverages large language models (LLMs) to:
- Detect whether an image is an invoice
- Extract structured data from invoices including:
  - Invoice date (in ISO format YYYY-MM-DD)
  - Total amount
  - Currency (ISO codes)

## Architecture

```
invoicescan/
├── main.py              # CLI entrypoint with backend selection
├── backend.py           # Unified Backend class with all inference logic
├── base.py              # BaseInferencer with shared methods
├── utils.py             # Schemas, prompts, image encoding
├── api.py               # FastAPI web server
├── frontend/            # Web UI
│   ├── index.html
│   ├── script.js
│   └── style.css
└── tests/               # Unit tests (19 passing)
    ├── conftest.py
    ├── test_backends.py
    └── test_cli.py
```

## Features

### Invoice Detection
Uses vision models to classify images as invoices or non-invoices with JSON schema validation.

### Data Extraction
Extracts structured invoice data with support for:
- German date formats (e.g., "30. Juni 1975", "30.06.1975")
- Various currency formats and symbols
- Thousand separators and decimal variations
- ISO currency code mapping (€/EUR → EUR, DM → DEM)

### Multiple Backends
- **OpenRouter API**: Cloud-based inference with various models
- **Ollama**: Local inference server (http://localhost:11434/v1)
- **Llama.cpp Server**: Local inference via HTTP (http://localhost:8080/v1)

## Requirements

```
openai
python-dotenv
requests
fastapi
uvicorn
python-multipart
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENROUTER_API_KEY=your_openrouter_key
OLLAMA_API_KEY=your_ollama_key
```

## Usage

### Web Interface (Recommended)

Start the FastAPI server:
```bash
python -m api
```

Then open http://localhost:8000 in your browser.

### Command Line

**Using main.py with backend selection:**
```bash
# OpenRouter (cloud)
python main.py openrouter ./invoice.jpg --model google/gemma-3-27b-it:free

# Ollama (local)
python main.py ollama ./invoice.jpg --model llava

# Llama.cpp server (simple output)
python main.py llama ./invoice.jpg

# Llama.cpp server (detailed debug output)
python main.py llama ./invoice.jpg --debug

# Llama.cpp server (custom URL)
python main.py llama ./invoice.jpg --url http://localhost:8080/v1
```

### Programmatic Usage

```python
from backend import Backend, BackendType

# Initialize with llama.cpp server
backend = Backend(type=BackendType.LLAMA, base_url="http://localhost:8080/v1")

# Process an invoice image
result = backend.process_invoice("./invoice_image.png")
print(result)
# Output: {"invoice_date": "2024-01-15", "total_amount": 123.45, "currency": "EUR"}
```

### Direct API Calls

```python
import requests

# Using the FastAPI server
files = {"file": open("./invoice.jpg", "rb")}
response = requests.post("http://localhost:8000/process", files=files)
print(response.json())
```

## API Endpoints

### POST /process
Process an invoice image and extract properties.

**Request:** `multipart/form-data` with `file` field containing the image.

**Response (success):**
```json
{
  "invoice_date": "2024-01-15",
  "total_amount": 123.45,
  "currency": "EUR"
}
```

**Response (no invoice detected):**
```json
{
  "error": "No invoice detected in image"
}
```

**Response (error):**
```json
{
  "detail": "Error message"
}
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_backends.py -v
pytest tests/test_cli.py -v

# Run with coverage
pytest --cov=invoicescan --cov-report=term-missing
```

## Model Configuration

### OpenRouter/Ollama
Specify model when calling inference methods:
```python
backend.invoice_or_not(image_path, "minicpm-v:8b-2.6-q4_K_M")
backend.invoice_properties(image_path, "minicpm-v:8b-2.6-q4_K_M")
backend.process_invoice(image_path, "minicpm-v:8b-2.6-q4_K_M")
```

### Llama.cpp Server
The server handles model loading. Configure model in your llama.cpp server startup command.

## Project Structure

### Backend Classes

**Backend** (`backend.py`):
- Unified class supporting all backends via `BackendType` enum
- `process_invoice()`: End-to-end invoice processing
- `invoice_or_not()`: Detect if image is an invoice
- `invoice_properties()`: Extract structured data

**BaseInferencer** (`base.py`):
- Base class with shared inference logic
- `generate()`: Core method for LLM calls

### Shared Components

**utils.py**:
- `INVOICE_DETECTION_SCHEMA`: JSON schema for invoice detection
- `INVOICE_PROPERTIES_SCHEMA`: JSON schema for data extraction
- `INVOICE_DETECTION_PROMPT`: Prompt for invoice detection
- `INVOICE_PROPERTIES_PROMPT`: Prompt for data extraction
- `encode_image()`: Convert image to base64
