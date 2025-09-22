# Project Context: ChatGPT-PDF

## Project Overview
This is a Streamlit-based web application designed for document processing and information extraction using OCR (Optical Character Recognition) and LLM (Large Language Models). The application provides various tools for handling PDF documents, images, and extracting structured information from them.

### Core Features
1. **Document Processing**:
   - PDF compression
   - Card detection and recognition
   - Seal detection in images

2. **OCR + LLM Integration**:
   - ID card information extraction (OCR + LLM)
   - Business license information extraction (OCR + LLM)
   - Invoice information extraction (OCR + LLM)
   - Contract information validation (OCR + LLM)
   - Contract key information extraction (OCR + LLM)

3. **File Management**:
   - Upload files to DFS (Distributed File System) server

### Technology Stack
- **Framework**: Streamlit for web interface
- **Backend**: Python with various libraries for image processing and PDF manipulation
- **ML/OCR Services**: Integration with external APIs for OCR and seal recognition
- **LLM Integration**: Connection to LLM services for information extraction
- **Key Libraries**: fitz (PyMuPDF), OpenCV, PIL, requests, numpy

## Project Structure
```
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── uv.lock                # Precise dependency lock file
├── setup.cmd              # Launch script
├── pages/                 # Individual Streamlit pages for each feature
├── service/               # Backend service modules
├── models/                # ML models (ONNX format)
├── db/                    # Database files (if any)
└── huggingface/          # HuggingFace models and resources
```

## Setup and Running

### Prerequisites
- Python 3.11+
- `uv` package manager

### Installation
Using `uv` for package management (recommended):

1. Create and activate a virtual environment with `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```
   
Alternatively, you can use the `uv.lock` file for more precise dependency resolution:
```bash
uv sync
```

### Configuration
The application uses environment variables stored in the `.env` file:
- `OPENAI_API_KEY`: API key for LLM services
- `OPENAI_BASE_URL`: Base URL for LLM API
- `PADDLE_OCR_URL`: URL for Paddle OCR service
- `PADDLE_SEAL_URL`: URL for Paddle seal recognition service
- `LLM_VERSION`: Version of LLM to use (e.g., qwen3:8b)
- `VLM_VERSION`: Version of Vision Language Model
- Various service URLs for specific features (DFS, contract processing, etc.)

### Running the Application
Execute the setup script:
```bash
setup.cmd
```
Or directly run:
```bash
streamlit run app.py
```

This will start the Streamlit server, typically accessible at `http://localhost:8501`.

## Development Information

### Main Components

#### 1. Entry Point (`app.py`)
- Configures Streamlit pages using `st_pages`
- Defines navigation to different feature pages with icons

#### 2. Feature Pages (`pages/`)
Each feature has its own page:
- `CompressPdf.py`: PDF compression functionality
- `OcrInvoiceLLM.py`: Invoice information extraction
- `ContractInfoExtractLLM.py`: Contract information extraction
- `CardDetection.py`: Card detection and recognition
- `ExtractSeal.py`: Seal detection in images
- `OcrSeal.py`: Seal extraction using PaddleOCR
- `OcrIdcardLLM.py`: ID card information extraction
- `OcrBusinessLLM.py`: Business license information extraction
- `UploadFileToDfs.py`: Upload files to DFS server

#### 3. Service Layer (`service/`)
Backend services for different functionalities:
- `PdfService.py`: PDF to image and image to PDF conversion
- `OcrService.py`: OCR-related functions
- `OneApiService.py`: LLM API integration
- `PaddleOcrService.py`: Paddle OCR service integration
- `ExtractSealService.py`: Seal detection service
- `IPService.py`: Integration with IPS (Information Processing Service)

#### 4. Configuration (`config.py`)
Contains settings for:
- Data directories
- Model configurations
- Training parameters
- Test parameters

### Key Workflows

#### PDF Compression
1. User uploads a PDF file
2. System converts PDF to images
3. Images are compressed based on quality settings
4. Compressed images are converted back to PDF
5. Result is provided for download

#### Document Information Extraction
1. User uploads document image/PDF
2. OCR service extracts text from document
3. LLM processes extracted text to identify specific information
4. Results are displayed in structured format

#### Seal Detection
1. User uploads image with potential seals
2. External seal recognition service processes image
3. Detected seals are highlighted/returned

## Development Conventions
- Each feature is implemented as a separate Streamlit page
- Services are modularized in the `service/` directory
- Environment variables are used for configuration
- Error handling is implemented for user-facing operations
- Progress indicators/spinners are used for long-running operations

## Common Tasks

### Adding a New Feature
1. Create a new page in the `pages/` directory
2. Implement the Streamlit UI and functionality
3. Add any required backend services in `service/`
4. Update `app.py` to include the new page in navigation

### Modifying LLM Integration
1. Update the `.env` file with new LLM settings
2. Modify `OneApiService.py` if API interaction changes
3. Update UI components in relevant pages to reflect new capabilities

### Updating Dependencies
With `uv` package management:
1. Add new dependencies: `uv pip install package-name`
2. Update `requirements.txt`: `uv pip compile pyproject.toml -o requirements.txt`
3. Update lock file: `uv lock`

Alternative method:
1. Modify `requirements.txt` as needed
2. Run `uv pip install -r requirements.txt` to update environment