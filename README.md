# WorkspaceGPT 🤖

A comprehensive multi-agent AI assistant system that demonstrates PDF-based retrieval, intelligent planning, and task execution using OpenAI, LangChain, and FAISS vector search.

## Features ✨

### 🧠 Multi-Agent Architecture
- **Planner Agent**: Breaks down user queries into actionable steps using OpenAI GPT-4
- **Retriever Agent**: Searches through PDF documents using FAISS vector embeddings
- **Executor Agent**: Performs actions like creating tasks, summaries, and reports

### 📄 PDF Processing & RAG
- Automatic PDF loading and text extraction using PyPDF
- Document chunking with RecursiveCharacterTextSplitter
- OpenAI embeddings with FAISS vector store
- Semantic search across document collections

### 🔄 MCP-Style Context Management
- In-memory conversation context tracking
- Step-by-step execution logging
- Decision and result history maintenance

### 🎨 Modern React UI
- Beautiful, responsive interface
- Real-time processing visualization
- Document management and upload
- Step-by-step execution tracking

## Project Structure 📁

```
WorkspaceGPT/
├── backend/
│   ├── agents/
│   │   ├── planner.py          # Planning agent using OpenAI
│   │   ├── retriever.py        # Vector search agent
│   │   └── executor.py         # Action execution agent
│   ├── context/
│   │   └── context_manager.py  # MCP-style context management
│   ├── vector_store/
│   │   └── faiss_store.py      # FAISS vector store implementation
│   ├── docs/                   # PDF documents folder
│   ├── main.py                 # Main orchestrator
│   └── api.py                  # FastAPI backend server
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── App.css             # Styling
│   │   └── index.js            # React entry point
│   ├── public/
│   └── package.json
├── requirements.txt            # Python dependencies
└── README.md
```

## Installation & Setup 🚀

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd WorkspaceGPT
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Add Sample Documents
Place your PDF files in the `backend/docs/` folder. A sample onboarding document is already included.

## Running the Application 🏃‍♂️

### Start the Backend Server
```bash
# From the project root
cd backend
python api.py
```
The FastAPI server will start on `http://localhost:8000`

### Start the Frontend
```bash
# In a new terminal, from the project root
cd frontend
npm start
```
The React app will start on `http://localhost:3000`

## Usage Guide 📖

### 1. Query Interface
- Navigate to the Query tab
- Enter your question (e.g., "Summarize my onboarding and create a checklist")
- Click "Process Query" to start the multi-agent workflow

### 2. Results Visualization
- View the generated execution plan
- Track step-by-step processing
- See final results and achievements

### 3. Document Management
- Upload new PDF documents
- View available documents and statistics
- Documents are automatically indexed for search

## Example Queries 💡

- **"Summarize my onboarding and create a checklist"**
  - Retrieves onboarding information
  - Creates a summary and actionable checklist

- **"What are the company values and policies?"**
  - Searches for company information
  - Provides structured summary

- **"Create a task list for my first week"**
  - Extracts first-week activities
  - Generates organized task list

## API Endpoints 🔌

### Backend API (FastAPI)
- `POST /query` - Process user queries
- `GET /stats` - Get vector store statistics
- `GET /documents` - List available documents
- `POST /upload` - Upload new PDF documents
- `GET /tasks` - Get created tasks
- `GET /reports` - Get generated reports

## Architecture Details 🏗️

### Agent Flow
1. **User Query** → **Planner Agent**
2. **Plan** → **Retriever Agent** (searches PDFs)
3. **Retrieved Content** → **Executor Agent** (performs actions)
4. **Results** → **Context Manager** (logs everything)

### Vector Store
- Uses FAISS for efficient similarity search
- OpenAI text-embedding-ada-002 for embeddings
- Configurable chunk size and overlap
- Persistent index storage

### Context Management
- Tracks all agent interactions
- Maintains conversation history
- Provides execution analytics
- Supports session management

## Dependencies 📦

### Backend
- `langchain` - LLM framework and document processing
- `openai` - OpenAI API integration
- `faiss-cpu` - Vector similarity search
- `pypdf` - PDF text extraction
- `fastapi` - Web API framework
- `python-dotenv` - Environment configuration

### Frontend
- `react` - UI framework
- `axios` - HTTP client
- `lucide-react` - Icon components

## Configuration ⚙️

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Vector Store Configuration
Modify settings in `backend/vector_store/faiss_store.py`:
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `score_threshold`: Similarity threshold (default: 0.7)

## Development 🛠️

### Running Backend Only
```bash
cd backend
python main.py
```

### Running Tests
```bash
# Backend tests (if implemented)
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### API Documentation
FastAPI automatically generates interactive API docs at:
`http://localhost:8000/docs`

## Troubleshooting 🔧

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in the `.env` file
   - Check that you have sufficient OpenAI credits

2. **PDF Processing Errors**
   - Ensure PDFs are readable and not password-protected
   - Check file permissions in the `backend/docs/` folder

3. **Vector Store Not Loading**
   - Delete the `backend/vector_store/faiss_index*` files to rebuild
   - Check that you have PDF documents in the docs folder

4. **Frontend Connection Issues**
   - Ensure the backend server is running on port 8000
   - Check CORS settings in `backend/api.py`

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project is for educational and demonstration purposes.

## Acknowledgments 🙏

- OpenAI for GPT-4 and embedding models
- LangChain for the excellent framework
- FAISS for efficient vector search
- React team for the UI framework

---

**Built with ❤️ to demonstrate modern AI agent architectures and RAG systems.** 