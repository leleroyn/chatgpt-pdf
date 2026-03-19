# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ChatGPT-PDF** is a Streamlit-based web application for document processing and information extraction using OCR and LLM technologies.

### Key Technologies
- **Framework**: Streamlit with `st_pages` for navigation
- **Language**: Python 3.11
- **Package Manager**: `uv`
- **Key Libraries**: PyMuPDF (fitz), OpenCV, PIL, OpenAI SDK

### Core Features
- Document compression (PDF)
- Card detection and seal detection
- OCR + LLM integration for:
  - ID card information extraction
  - Business license information extraction
  - Invoice information extraction
  - Contract information validation and extraction
- Handprint detection

---

## Architecture

### Directory Structure

```
chatgpt-pdf/
├── app.py                          # Main entry point, defines navigation
├── pages/                           # Streamlit page modules (12 features)
│   ├── SmartQAKB.py                 # Smart Q&A (Simple_KB)
│   ├── CompanyMatch.py              # Company name matching
│   ├── ExtractSeal.py               # Seal detection
│   ├── OcrSeal.py                   # Seal extraction (Paddle)
│   ├── UploadFileToDfs.py           # Upload to DFS server
│   ├── CompressPdf.py               # PDF compression
│   ├── CardDetection.py             # Card detection
│   ├── OcrIdcardLLM.py              # ID card extraction (OCR+LLM)
│   ├── OcrBusinessLLM.py            # Business license extraction
│   ├── OcrInvoiceLLM.py             # Invoice extraction
│   ├── ContractInfoLLM.py           # Contract validation
│   ├── ContractInfoExtractLLM.py    # Contract extraction
│   └── HandprintDetection.py        # Handprint detection
├── service/                         # Backend services
│   ├── OneApiService.py             # LLM integration (OpenAI)
│   ├── IPService.py                 # OCR/preprocessing
│   ├── PdfService.py                # PDF operations
│   ├── OcrService.py                # OCR utilities
│   ├── PaddleOcrService.py          # Paddle OCR integration
│   ├── ExtractSealService.py        # Seal extraction
│   ├── VectorDBService.py           # Vector database operations
│   ├── CompanyMatchService.py       # Company name matching
│   └── __init__.py                  # Re-exports
├── .env                             # Environment variables
├── requirements.txt                 # Dependencies
└── pyproject.toml                   # Project metadata
```

### Design Patterns

**1. Service Layer Pattern**
- Each service is a self-contained class with single responsibility
- Services load environment variables via `load_dotenv()` at initialization
- Services use `os.getenv()` for configuration
- Return structured data (dicts, JSON strings, LLM responses)

**2. Streamlit Pages Pattern**
- Each page has a `main()` function as entry point
- Pages use `st.set_page_config()` with custom titles and icons
- Standard error handling with try/except blocks
- Use `load_dotenv()` at entry point

**3. OCR + LLM Pipeline Pattern**
Most pages follow this pattern:
```
1. Upload file → 2. OCR detection → 3. Image preprocessing → 4. LLM extraction → 5. Result display
```

---

## Development Workflow

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation
```bash
# Create virtual environment
uv venv

# Activate
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Using setup script (Windows)
setup.cmd

# Or directly with Streamlit
streamlit run app.py
```
The app runs at `http://localhost:8501`.

### Dependency Management
```bash
# Add new dependency
uv pip install package-name

# Update requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Update lock file
uv lock
```

---

## Code Conventions

### Imports
Standard order: standard library → third-party → local application
```python
import io
from time import time
import json
import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service.IPService import IPService
from service.OneApiService import OneApiService
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `OneApiService`, `IPService`)
- **Functions/variables**: snake_case (e.g., `pdf_to_pic`, `byte_stream`)
- **Constants**: UPPER_SNAKE_CASE
- **Files**: snake_case (e.g., `ocr_idcard_llm.py`)

### Error Handling
```python
try:
    # Main logic
    result = service.process(data)
except Exception as e:
    st.error(f"Error message: {str(e)}")
    st.info("User guidance message")
```

### UI Patterns
- Use `st.columns()` for layout
- Use `st.spinner()` for async operations
- Use `st.expander()` to collapse detailed information
- Display metrics with `st.metric()`
- Show status with `st.success()`, `st.warning()`, `st.error()`, `st.info()`

### Logging
- Currently uses `print()` statements for debugging
- Consider using `loguru` (already in dependencies) for production

---

## Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=http://your-llm-endpoint
LLM_VERSION=qwen3:8b
PADDLE_OCR_URL=http://your-ocr-service
PADDLE_SEAL_URL=http://your-seal-service
DFS_URL=your_dfs_url
CONTRACT_VALID_URL=your_contract_validation_url
```

---

## Key Service Classes

### OneApiService
Handles LLM interactions via OpenAI SDK:
- `ocr_idcard_llm()` - ID card information extraction
- `ocr_business_llm()` - Business license extraction
- `ocr_invoice_llm()` - Invoice extraction
- `contract_llm()` - Contract validation
- `ocr_idcard_vl()` - Visual ID card recognition
- `ocr_business_vl()` - Visual business license recognition
- `ocr_invoice_vl()` - Visual invoice recognition

### IPService
Handles OCR and preprocessing:
- `idcard_preprocess()` - ID card detection and preprocessing
- `base64_to_pil()` - Image conversion utilities

---

## Adding New Features

1. **Create a new page** in `pages/`
2. **Implement Streamlit UI** with appropriate components
3. **Add backend service** in `service/` if needed
4. **Register page** in `app.py` using `st_pages`
5. **Test locally** with `streamlit run app.py`

---

## Testing
**No formal test framework is currently configured.** If tests are added:
```bash
# Run all tests (if pytest is configured)
pytest

# Run a single test file
pytest tests/test_specific.py

# Run a single test function
pytest tests/test_specific.py::test_function_name
```

---

## Linting / Type Checking
**No linting or type checking is currently configured.** If tools are added:
```bash
# Run ruff linter (if configured)
ruff check .

# Run mypy type checker (if configured)
mypy .
```

---

## Common Development Tasks

### Understanding a Page's Flow
1. Look for the `main()` function - this is the entry point
2. Check for `st.file_uploader` or other input widgets
3. Identify the service calls (usually in `service/` imports)
4. Look for timing metrics (using `time.time()`) - indicates performance-sensitive code

### Adding New Services
1. Create a new file in `service/`
2. Implement a class with `__init__` that loads env vars
3. Add methods for specific operations
4. Re-export in `service/__init__.py` if needed

### Debugging LLM Calls
- Check `OneApiService.py` for prompt construction
- Verify `LLM_VERSION` environment variable
- Check OpenAI SDK error handling

---

## Notes
- The project uses `st_pages` library for custom navigation
- Most pages combine OCR detection with LLM-based extraction
- Performance metrics are tracked using `time.time()`
- The codebase is relatively new with minimal type hints
- Environment configuration is critical - ensure `.env` is properly set up
