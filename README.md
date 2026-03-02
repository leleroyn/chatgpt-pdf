# ChatGPT-PDF

A Streamlit-based web application for document processing and information extraction using OCR and LLM technologies.

## Features

- **Document Processing**: PDF compression, card detection, seal detection
- **OCR + LLM Integration**:
  - ID card information extraction
  - Business license information extraction
  - Invoice information extraction
  - Contract information validation
  - Contract key information extraction

## Tech Stack

- **Framework**: Streamlit
- **Language**: Python 3.11
- **Package Manager**: uv
- **Key Libraries**: PyMuPDF, OpenCV, PIL, OpenAI

## Quick Start

```bash
# Create virtual environment
uv venv

# Activate
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=http://your-llm-endpoint
LLM_VERSION=qwen3:8b
PADDLE_OCR_URL=http://your-ocr-service
PADDLE_SEAL_URL=http://your-seal-service
```

## Project Structure

```
├── app.py              # Main entry point
├── pages/              # Streamlit page modules
├── service/           # Backend services
├── requirements.txt   # Dependencies
└── pyproject.toml     # Project metadata
```

## License

MIT
