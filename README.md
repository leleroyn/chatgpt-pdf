# ChatGPT-PDF Document Processing System

## 📋 Overview
ChatGPT-PDF is a modern Streamlit-based web application designed for comprehensive document processing and information extraction. It combines OCR (Optical Character Recognition) with LLM (Large Language Models) to provide powerful tools for handling PDF documents, images, and extracting structured information from them.

## ✨ Key Features
1. **Document Processing**:
   - PDF compression with quality control
   - Card detection and recognition (ID cards, business licenses, etc.)
   - Seal detection in document images
   - File upload to distributed file systems

2. **OCR + LLM Integration**:
   - ID card information extraction using OCR + LLM
   - Business license information extraction using OCR + LLM
   - Invoice information extraction using OCR + LLM
   - Contract information validation using OCR + LLM
   - Contract key information extraction using OCR + LLM

3. **Modern UI/UX**:
   - Sleek, responsive design with gradient backgrounds
   - Card-based layout for better organization
   - Hover effects and smooth transitions
   - Consistent styling across all pages
   - Mobile-responsive components

## 🛠️ Technology Stack
- **Framework**: [Streamlit](https://streamlit.io/) for web interface
- **Backend**: Python with libraries for image processing and PDF manipulation
- **ML/OCR Services**: Integration with external APIs for OCR and seal recognition
- **LLM Integration**: Connection to LLM services for intelligent information extraction
- **Key Libraries**: PyMuPDF, OpenCV, PIL, requests, numpy

## 📁 Project Structure
```
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── uv.lock                # Precise dependency lock file
├── setup.cmd              # Launch script
├── styles.css             # Modern UI styling
├── pages/                 # Individual Streamlit pages for each feature
├── service/               # Backend service modules
├── models/                # ML models (ONNX format)
├── db/                    # Database files (if any)
└── huggingface/          # HuggingFace models and resources
```

## 🚀 Setup and Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation Using uv (Recommended)
```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Alternative Installation Using pip
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
The application uses environment variables stored in the `.env` file:
```env
# LLM Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=http://your-llm-api-endpoint
LLM_VERSION=qwen3:8b

# OCR Services
PADDLE_OCR_URL=http://your-ocr-service-endpoint
PADDLE_SEAL_URL=http://your-seal-recognition-service-endpoint

# Additional Services
DFS_URL=http://your-dfs-upload-endpoint
CONTRACT_VALID_URL=http://your-contract-validation-endpoint
CONTRACT_EXTRACT_URL=http://your-contract-extraction-endpoint
```

### Running the Application
```bash
# Using the setup script
setup.cmd

# Or directly run with Streamlit
streamlit run app.py
```

The application will typically be accessible at `http://localhost:8501`.

## 🎨 Modern UI Features

### Visual Design
- **Gradient Backgrounds**: Modern gradient color schemes for headers and buttons
- **Card-Based Layout**: Content organized in visually distinct cards with shadows
- **Hover Effects**: Interactive elements respond to user interactions
- **Responsive Design**: Adapts to different screen sizes
- **Consistent Styling**: Unified look and feel across all pages

### Component Styling
- **Buttons**: Gradient backgrounds with hover animations
- **File Uploaders**: Custom-styled drag-and-drop areas
- **Sliders**: Enhanced visual appearance
- **Metrics**: Modern card-based display
- **Expanders**: Clean, modern borders and shadows
- **Tabs**: Well-defined tab containers

### User Experience Improvements
- **Clear Visual Hierarchy**: Proper use of typography and spacing
- **Intuitive Navigation**: Sidebar with quick links and feature descriptions
- **Loading States**: Spinner animations during processing
- **Result Organization**: Structured presentation of results
- **Helpful Messages**: Clear instructions and feedback

## 📖 Usage Guide

### PDF Compression
1. Navigate to the "PDF压缩" page
2. Upload your PDF file
3. Adjust compression settings as needed
4. Download the compressed PDF

### Document Information Extraction
1. Select the appropriate document type page (ID card, business license, invoice, etc.)
2. Upload your document image or PDF
3. The system will automatically process the document using OCR + LLM
4. View extracted information in structured format

### Seal Detection
1. Navigate to the "检测图片中的印章" page
2. Upload an image containing potential seals
3. The system will detect and highlight seals in the document

### File Upload to DFS
1. Navigate to the "上传文件到DFS服务器" page
2. Select files to upload
3. Files will be uploaded to the configured DFS server

## 👨‍💻 Development

### Adding New Features
1. Create a new page in the `pages/` directory
2. Implement the Streamlit UI and functionality
3. Add any required backend services in `service/`
4. Register the new page in `app.py`

### Modifying LLM Integration
1. Update the `.env` file with new LLM settings
2. Modify `service/OneApiService.py` if API interaction changes
3. Update UI components in relevant pages to reflect new capabilities

### Dependency Management
With `uv` package management:
```bash
# Add new dependencies
uv pip install new-package-name

# Update requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Update lock file
uv lock
```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.