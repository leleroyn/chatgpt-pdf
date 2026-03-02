# AGENTS.md - Development Guide for AI Agents

## Project Overview

ChatGPT-PDF is a Streamlit-based web application for document processing and information extraction using OCR and LLM technologies. The project is written in Python 3.11 and uses `uv` as the package manager.

---

## Build / Run Commands

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation
```bash
# Create virtual environment
uv venv

# Activate on Windows
.venv\Scripts\activate

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

### Testing
**No formal test framework is currently configured.** If tests are added:
```bash
# Run all tests (if pytest is configured)
pytest

# Run a single test file
pytest tests/test_specific.py

# Run a single test function
pytest tests/test_specific.py::test_function_name
```

### Linting / Type Checking
**No linting or type checking is currently configured.** If tools are added:
```bash
# Run ruff linter (if configured)
ruff check .

# Run mypy type checker (if configured)
mypy .
```

---

## Code Style Guidelines

### General Rules
- This is a Streamlit application with modular service layer
- Pages go in `pages/` directory, backend services in `service/`
- Follow existing patterns in the codebase

### Imports
```python
# Standard library first
import os
import json
from time import time
import io

# Third-party libraries
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Local application imports
from service.IPService import IPService
from service.OneApiService import OneApiService
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `OneApiService`, `PdfService`)
- **Functions/variables**: snake_case (e.g., `pdf_to_pic`, `byte_stream`)
- **Constants**: UPPER_SNAKE_CASE
- **Files**: snake_case (e.g., `ocr_idcard_llm.py`)

### Type Hints
- **Currently not used** in this codebase, but if added:
```python
def process_image(image_bytes: bytes) -> dict[str, Any]:
    ...
```

### File Organization

#### Streamlit Pages (`pages/`)
- One file per feature
- Main function named `main()`
- Standard imports at top
- Use `load_dotenv()` at entry point
- Wrap main logic in try/except for error handling

#### Service Layer (`service/`)
- One service class per file
- Import `load_dotenv` in `__init__` or constructor
- Use environment variables via `os.getenv()`
- Return structured data (dicts, JSON strings)

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

### Code Comments
- Currently minimal comments in codebase
- Add brief comments for complex logic if needed

---

## Project Structure

```
chatgpt-pdf/
├── app.py                 # Main entry point, defines navigation
├── pages/                 # Streamlit page modules
│   ├── OcrIdcardLLM.py
│   ├── OcrBusinessLLM.py
│   ├── OcrInvoiceLLM.py
│   ├── ContractInfoLLM.py
│   ├── CompressPdf.py
│   └── ...
├── service/               # Backend services
│   ├── OneApiService.py   # LLM integration
│   ├── PdfService.py      # PDF operations
│   ├── IPService.py       # OCR/preprocessing
│   └── ...
├── .env                   # Environment variables (API keys, URLs)
├── requirements.txt       # Dependencies
└── pyproject.toml         # Project metadata
```

---

## Adding New Features

1. **Create a new page** in `pages/`
2. **Implement Streamlit UI** with appropriate components
3. **Add backend service** in `service/` if needed
4. **Register page** in `app.py` using `st_pages`
5. **Test locally** with `streamlit run app.py`

---

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY` - LLM API key
- `OPENAI_BASE_URL` - LLM API endpoint
- `LLM_VERSION` - Model name (e.g., `qwen3:8b`)
- `PADDLE_OCR_URL` - OCR service URL
- `PADDLE_SEAL_URL` - Seal detection URL
- `DFS_URL`, `CONTRACT_VALID_URL`, etc. - Feature-specific services
