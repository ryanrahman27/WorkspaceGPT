from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import shutil
from main import WorkspaceGPT

# Initialize FastAPI app
app = FastAPI(title="WorkspaceGPT API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WorkspaceGPT
workspace_gpt = None

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    user_query: Optional[str] = None
    error: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    step_results: Optional[List[Dict[str, Any]]] = None
    final_summary: Optional[Dict[str, Any]] = None

class StatsResponse(BaseModel):
    success: bool
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize WorkspaceGPT on startup."""
    global workspace_gpt
    try:
        workspace_gpt = WorkspaceGPT()
        print("✅ WorkspaceGPT API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize WorkspaceGPT API: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "WorkspaceGPT API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    return {"status": "healthy", "service": "WorkspaceGPT API"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the multi-agent system."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    try:
        result = workspace_gpt.process_query(request.query)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get vector store statistics."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    try:
        stats = workspace_gpt.get_vector_store_stats()
        return StatsResponse(success=True, stats=stats)
    except Exception as e:
        return StatsResponse(success=False, error=str(e))

@app.get("/documents")
async def list_documents():
    """List all available documents."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    try:
        result = workspace_gpt.retriever.get_document_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document to the vector store."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    # Check file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file
        file_path = f"backend/docs/{file.filename}"
        os.makedirs("backend/docs", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to vector store
        success = workspace_gpt.add_document(file_path)
        
        if success:
            return {"message": f"Document '{file.filename}' uploaded and indexed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to index document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/tasks")
async def get_tasks():
    """Get all created tasks."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    try:
        tasks = workspace_gpt.executor.get_tasks()
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@app.get("/reports")
async def get_reports():
    """Get all generated reports."""
    if workspace_gpt is None:
        raise HTTPException(status_code=503, detail="WorkspaceGPT not initialized")
    
    try:
        reports = workspace_gpt.executor.get_reports()
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 