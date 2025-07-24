# WorkspaceGPT 🤖

A comprehensive multi-agent AI assistant system that demonstrates PDF-based retrieval, intelligent planning, and task execution using OpenAI GPT-4. Features dual vector store implementations (FAISS and ChromaDB) with a beautiful React frontend.

## Features ✨

### 🧠 Multi-Agent Architecture
- **Planner Agent**: Breaks down user queries into actionable steps using OpenAI GPT-4
- **Retriever Agent**: Searches through PDF documents using vector embeddings
- **Executor Agent**: Performs actions like creating tasks, summaries, checklists, and reports

### 📄 PDF Processing & RAG (Retrieval-Augmented Generation)
- Automatic PDF loading and text extraction using PyPDF
- Document chunking with RecursiveCharacterTextSplitter
- OpenAI embeddings (text-embedding-ada-002)
- **Dual Vector Store Support**:
  - **FAISS**: High-performance similarity search with CPU optimization
  - **ChromaDB**: Modern vector database with built-in persistence

### 🔄 Context Management
- In-memory conversation context tracking
- Step-by-step execution logging
- Decision and result history maintenance
- Session-based interaction tracking

### 🎨 Modern React UI
- Beautiful, responsive interface with Lucide React icons
- Real-time processing visualization
- Document management and query interface
- Step-by-step execution tracking
- Multi-tab navigation (Query, Results, Documents)

## Project Structure 📁

```
WorkspaceGPT/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py          # GPT-4 planning agent
│   │   ├── retriever.py        # Vector search agent
│   │   └── executor.py         # Action execution agent
│   ├── context/
│   │   ├── __init__.py
│   │   └── context_manager.py  # Session and context management
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── faiss_store.py      # FAISS vector store implementation
│   │   ├── chroma_store.py     # ChromaDB vector store implementation
│   │   └── chroma_db/          # ChromaDB persistent storage
│   ├── docs/                   # PDF documents folder
│   │   └── sample_onboarding.pdf
│   ├── backend/                # Additional docs and storage
│   │   ├── docs/               # Additional PDF storage
│   │   └── vector_store/       # Additional vector storage
│   ├── main.py                 # Main orchestrator (FAISS version)
│   ├── main_chroma.py          # Main orchestrator (ChromaDB version)
│   ├── api.py                  # FastAPI server (FAISS version)
│   ├── api_chroma.py           # FastAPI server (ChromaDB version)
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── App.css             # Beautiful styling
│   │   └── index.js            # React entry point
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── package-lock.json
├── requirements.txt            # Python dependencies (FAISS)
├── requirements_alternative.txt # Python dependencies (ChromaDB)
├── .gitignore                  # Git ignore rules
└── README.md
```

## Installation & Setup 🚀

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/ryanrahman27/WorkspaceGPT.git
cd WorkspaceGPT
```

### 2. Choose Vector Store Implementation

#### Option A: FAISS (Recommended for CPU performance)
```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### Option B: ChromaDB (Recommended for persistence and ease of use)
```bash
# Install Python dependencies
pip install -r requirements_alternative.txt
```

### 3. Set up Environment Variables
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Add Sample Documents
Place your PDF files in the `backend/docs/` folder. A sample onboarding document is already included.

## Running the Application 🏃‍♂️

### Backend Server

#### FAISS Version
```bash
# From the project root
cd backend
python api.py
```

#### ChromaDB Version
```bash
# From the project root
cd backend
python api_chroma.py
```

The FastAPI server will start on `http://localhost:8000`

### Frontend
```bash
# In a new terminal, from the project root
cd frontend
npm start
```
The React app will start on `http://localhost:3000`

### Command Line Interface

You can also run the system directly from the command line:

#### FAISS Version
```bash
cd backend
python main.py
```

#### ChromaDB Version
```bash
cd backend
python main_chroma.py
```

## Usage Guide 📖

### 1. Web Interface
- **Navigate to** `http://localhost:3000`
- **Query Tab**: Enter your questions and process them through the multi-agent system
- **Results Tab**: View execution plans, step-by-step processing, and final results
- **Documents Tab**: View available documents and statistics

### 2. Example Queries
- **"Summarize my onboarding and create a checklist"**
  - Retrieves onboarding information from PDFs
  - Creates a summary and actionable checklist

- **"What are the company values and policies?"**
  - Searches for company information across documents
  - Provides structured summary

- **"Create a task list for my first week"**
  - Extracts first-week activities from onboarding docs
  - Generates organized task list with priorities

### 3. API Usage
Send POST requests to `http://localhost:8000/query` with:
```json
{
  "query": "Your question here"
}
```

## API Endpoints 🔌

### Core Endpoints
- `POST /query` - Process user queries through multi-agent system
- `GET /stats` - Get vector store statistics and document counts
- `GET /documents` - List available documents
- `POST /upload` - Upload new PDF documents
- `GET /tasks` - Get created tasks from executor agent
- `GET /reports` - Get generated reports from executor agent

### Interactive API Documentation
FastAPI automatically generates interactive API docs at:
`http://localhost:8000/docs`

## Architecture Details 🏗️

### Agent Workflow
1. **User Query** → **Planner Agent** (GPT-4 analysis and step creation)
2. **Execution Plan** → **Retriever Agent** (PDF search and content extraction)
3. **Retrieved Content** → **Executor Agent** (task creation, summarization, analysis)
4. **Results** → **Context Manager** (session tracking and logging)

### Vector Store Comparison

| Feature | FAISS | ChromaDB |
|---------|-------|----------|
| **Performance** | Faster queries | Good performance |
| **Persistence** | Manual save/load | Automatic persistence |
| **Memory Usage** | Higher | Lower |
| **Setup Complexity** | Simple | Very simple |
| **Scalability** | Excellent | Good |

### Executor Agent Actions
- `create_task`: Creates individual tasks with priorities
- `summarize`: Generates summaries from retrieved content
- `create_checklist`: Extracts actionable checklist items
- `analyze_content`: Provides structured content analysis
- `generate_report`: Creates formatted reports with sections

## Dependencies 📦

### Backend (FAISS Version)
- `langchain==0.1.4` - LLM framework and document processing
- `openai==1.10.0` - OpenAI API integration
- `faiss-cpu==1.7.4` - Vector similarity search
- `pypdf==4.0.1` - PDF text extraction
- `fastapi==0.109.0` - Web API framework
- `uvicorn==0.27.0` - ASGI server
- `python-dotenv==1.0.0` - Environment configuration

### Backend (ChromaDB Version)
- `chromadb==0.4.24` - ChromaDB vector database
- _(All other dependencies same as FAISS version)_

### Frontend
- `react==18.2.0` - UI framework
- `axios==1.3.0` - HTTP client for API calls
- `lucide-react==0.263.1` - Beautiful icon components

## Configuration ⚙️

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Vector Store Configuration
Modify settings in vector store files:

**FAISS (`backend/vector_store/faiss_store.py`)**:
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `score_threshold`: Similarity threshold (default: 0.7)

**ChromaDB (`backend/vector_store/chroma_store.py`)**:
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `score_threshold`: Similarity threshold (default: 0.3)

## Development 🛠️

### Running Backend Only (CLI)
```bash
# FAISS version
cd backend && python main.py

# ChromaDB version  
cd backend && python main_chroma.py
```

### API Development
```bash
# FAISS API server
cd backend && python api.py

# ChromaDB API server
cd backend && python api_chroma.py
```

### Testing Frontend
```bash
cd frontend && npm test
```

## Troubleshooting 🔧

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `.env` file is in project root with valid API key
   - Check that you have sufficient OpenAI credits

2. **PDF Processing Errors**
   - Ensure PDFs are readable and not password-protected
   - Check file permissions in `backend/docs/` folder
   - Try placing PDFs in both `backend/docs/` and `backend/backend/docs/`

3. **Vector Store Issues**
   - **FAISS**: Delete `backend/vector_store/faiss_index*` files to rebuild
   - **ChromaDB**: Delete `backend/vector_store/chroma_db/` folder to rebuild
   - Ensure you have PDF documents in the docs folder

4. **Frontend Connection Issues**
   - Ensure backend server is running on port 8000
   - Check CORS settings in the API files
   - Verify API endpoints are accessible at `http://localhost:8000/docs`

5. **Module Import Errors**
   - Ensure you're in the correct directory when running commands
   - Check that all requirements are installed: `pip list`

### Performance Tips
- **FAISS**: Better for high-frequency queries and large document sets
- **ChromaDB**: Better for development and when you need automatic persistence
- Adjust `chunk_size` and `chunk_overlap` based on your document types
- Monitor OpenAI API usage to manage costs

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with both vector store implementations
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License 📄

This project is for educational and demonstration purposes.

## Acknowledgments 🙏

- **OpenAI** for GPT-4 and embedding models
- **LangChain** for the excellent framework
- **FAISS** (Facebook AI Similarity Search) for efficient vector search
- **ChromaDB** for modern vector database capabilities
- **React** team for the UI framework
- **FastAPI** for the modern, fast web framework

---

**Built with ❤️ to demonstrate modern AI agent architectures, RAG systems, and vector search technologies.** 