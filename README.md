# InvoiceScan

An invoice processing system that uses AI to identify invoices and extract key information from document images.

## Overview

InvoiceScan leverages large language models (LLMs) to:
- Detect whether an image is an invoice
- Extract structured data from invoices including:
  - Invoice date (in ISO format YYYY-MM-DD)
  - Total amount
  - Currency (ISO codes)

## Components

### Core Files

- `main.py` - Main workflow orchestrator that processes images through the invoice detection and extraction pipeline
- `openrouter.py` - AI inference handler supporting OpenRouter API and local Ollama instances
- `local.py` - Local Llama model implementation using llama-cpp-python for offline processing
- `utils.py` - Utility functions for image encoding (base64)

## Features

### Invoice Detection
Uses vision models to classify images as invoices or non-invoices with JSON schema validation.

### Data Extraction
Extracts structured invoice data with support for:
- German date formats (e.g., "30. Juni 1975", "30.06.1975")
- Various currency formats and symbols
- Thousand separators and decimal variations
- ISO currency code mapping (€/EUR → EUR, DM → DEM)

### Model Support
- **OpenRouter API**: Cloud-based inference with various models
- **Ollama**: Local inference server (http://localhost:11434/v1)
- **Llama.cpp**: Direct local model execution with GPU acceleration (Vulkan)

## Requirements

```
openai
python-dotenv
llama-cpp-python
requests
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
LLAMACPP_PATH=path/to/llama.dll
```

## Usage

### Basic Workflow

```python
from openrouter import Inferencer
from main import workflow

# Initialize with local Ollama
ollama = Inferencer(local=True)

# Process an image
result = workflow(ollama, "./invoice_image.png")
print(result)
```

### Using OpenRouter API

```python
# Initialize with OpenRouter (cloud)
openrouter = Inferencer(local=False)
```

### Direct Inference

```python
from openrouter import Inferencer

inferencer = Inferencer(local=True)

# Check if image is an invoice
is_invoice = inferencer.invoice_or_not(image_path, "minicpm-v:8b-2.6-q4_K_M")

# Extract invoice properties
properties = inferencer.invoice_properties(image_path, "minicpm-v:8b-2.6-q4_K_M")
```

## Architecture

### Inferencer Class (`openrouter.py`)
Handles AI model interactions with support for:
- Multiple inference backends (OpenRouter, Ollama)
- JSON schema validation for structured outputs
- Temperature control for deterministic results

### LocalLlama Class (`local.py`)
Provides offline inference capabilities with:
- GPU acceleration support
- Configurable context size and threads
- Direct llama.cpp integration

### Workflow (`main.py`)
Main processing pipeline:
1. Classifies image as invoice/non-invoice
2. If invoice, extracts structured data
3. Returns None for non-invoice images

## Model Configuration

Default model: `minicpm-v:8b-2.6-q4_K_M`

For local Llama setup:
- Adjust `n_gpu_layers` based on your GPU
- Configure `n_ctx` for context length
- Set `n_threads` for CPU threads
