# RAG Steps - Intelligent Document Analysis System

## Overview
RAG Steps is a sophisticated document analysis system that combines the power of Retrieval-Augmented Generation (RAG) with modern AI techniques to provide intelligent answers from your PDF documents. The system uses state-of-the-art language models and semantic search to understand and answer questions about your documents with high accuracy.

## Key Features

### Document Processing
- 📄 Support for multiple PDF documents
- 🔄 Automatic text extraction and processing
- 📊 Smart text chunking for optimal context

### AI-Powered Search
- 🧠 Dense Passage Retrieval (DPR) for semantic understanding
- 🔍 Context-aware search capabilities
- 🎯 Intelligent query expansion

### Interactive Interface
- 💻 User-friendly Streamlit web interface
- 📁 Easy document management (upload/delete)
- 📊 Real-time processing status

### Advanced Features
- 💾 Persistent vector storage with ChromaDB
- 🤖 GPT-powered answer generation
- 🔄 Automatic query enhancement

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd ragsteps
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv rags
rags\Scripts\activate

# Linux/Mac
python -m venv rags
source rags/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.env` file in the project root
- Add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Streamlit interface:
```bash
streamlit run main_with_docs.py
```

2. Open your browser:
- The interface will automatically open at `http://localhost:8501`

## Usage Guide

### Adding Documents
1. Click the file upload button in the sidebar
2. Select one or more PDF files
3. Wait for processing completion
4. Your documents are now searchable!

### Asking Questions
1. Type your question in the main text input
2. The system will:
   - Expand your query for better coverage
   - Search for relevant context
   - Generate a comprehensive answer

### Managing Documents
- View all uploaded documents in the sidebar
- Delete individual documents with the 🗑️ button
- Use "Clear All" to reset the system

## Technical Details

### Components
- **Frontend**: Streamlit
- **Embeddings**: DPR (facebook/dpr-ctx_encoder-single-nq-base)
- **Vector Store**: ChromaDB
- **LLM**: GPT-3.5-turbo
- **PDF Processing**: PyPDF, LangChain

### File Structure
```
ragsteps/
├── main_with_docs.py    # Main Streamlit interface
├── pdf_loader.py        # PDF processing & vectorization
├── rag_query.py         # Query processing
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables
└── data/               # Document storage
```

## Performance Notes
- Initial setup downloads the DPR model (~500MB)
- PDF processing time varies with document size
- Vector search is optimized for quick retrieval

## Security Considerations
- Keep your `.env` file secure
- Never commit API keys
- Regularly update dependencies

## Troubleshooting

### Common Issues
1. **Slow Model Download**
   - First run downloads large models
   - Ensure stable internet connection

2. **Memory Usage**
   - Large documents may require more RAM
   - Process fewer documents simultaneously

3. **API Key Issues**
   - Verify OpenAI API key in `.env`
   - Check API usage limits

## Contributing
Contributions are welcome! Please feel free to submit pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


## Environment Setup

1. Copy `.env.example` to [.env](cci:7://file:///c:/Users/Roy%20Agoya/Desktop/Michael%27s%20projects/ragsteps/.env:0:0-0:0):
   ```bash
   cp .env.example .env