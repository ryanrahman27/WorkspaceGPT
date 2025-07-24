import os
import glob
from typing import List, Dict, Any, Optional
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import chromadb


class ChromaVectorStore:
    """ChromaDB-based vector store for PDF document retrieval."""
    
    def __init__(self, docs_folder: str = "docs", 
                 persist_directory: str = "vector_store/chroma_db",
                 chunk_size: int = 1000, chunk_overlap: int = 200):
        # Ensure we're working with absolute paths
        if not os.path.isabs(docs_folder):
            docs_folder = os.path.abspath(docs_folder)
        if not os.path.isabs(persist_directory):
            persist_directory = os.path.abspath(persist_directory)
            
        self.docs_folder = docs_folder
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings()
        self.vector_store: Optional[Chroma] = None
        self.documents: List[Document] = []
        
        # Create docs folder if it doesn't exist
        os.makedirs(docs_folder, exist_ok=True)
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdfs(self) -> List[Document]:
        """Load all PDF files from the docs folder."""
        print(f"📂 Loading PDFs from {self.docs_folder}...")
        
        # Find all PDF files
        pdf_files = glob.glob(os.path.join(self.docs_folder, "*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {self.docs_folder}")
            return []
        
        documents = []
        for pdf_file in pdf_files:
            print(f"📄 Loading: {os.path.basename(pdf_file)}")
            try:
                loader = PyPDFLoader(pdf_file)
                pdf_docs = loader.load()
                
                # Add metadata
                for doc in pdf_docs:
                    doc.metadata.update({
                        "source_file": os.path.basename(pdf_file),
                        "file_path": pdf_file
                    })
                
                documents.extend(pdf_docs)
                print(f"✅ Loaded {len(pdf_docs)} pages from {os.path.basename(pdf_file)}")
                
            except Exception as e:
                print(f"❌ Error loading {pdf_file}: {str(e)}")
        
        print(f"📚 Total documents loaded: {len(documents)}")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        print(f"✂️  Splitting documents into chunks (size: {self.chunk_size}, overlap: {self.chunk_overlap})...")
        
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk.page_content)
            })
        
        print(f"📝 Created {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, force_rebuild: bool = False) -> Chroma:
        """Create or load the ChromaDB vector store."""
        
        # Check if index already exists
        if os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3")) and not force_rebuild:
            print("📍 Loading existing ChromaDB index...")
            try:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print("✅ ChromaDB index loaded successfully")
                return self.vector_store
            except Exception as e:
                print(f"⚠️  Error loading existing index: {str(e)}")
                print("🔄 Creating new index...")
        
        # Load and process documents
        documents = self.load_pdfs()
        if not documents:
            # Create empty vector store if no documents
            print("🏗️  Creating empty vector store...")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # Split documents into chunks
            chunks = self.split_documents(documents)
            self.documents = chunks
            
            # Create embeddings and vector store
            print("🧠 Creating embeddings and building ChromaDB index...")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        
        # Persist the database
        print(f"💾 Persisting ChromaDB to {self.persist_directory}...")
        self.vector_store.persist()
        print("✅ Vector store created and persisted successfully")
        
        return self.vector_store
    
    def similarity_search(self, query: str, k: int = 4, 
                         score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Perform similarity search on the vector store."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")
        
        print(f"🔍 Searching for: '{query}' (top {k} results)")
        
        # Perform similarity search with scores
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        results = []
        for doc, score in docs_with_scores:
            # ChromaDB returns similarity scores (higher is better)
            similarity_score = 1 - score  # Convert distance to similarity
            
            if similarity_score >= score_threshold:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": similarity_score,
                    "distance": score
                }
                results.append(result)
        
        print(f"📋 Found {len(results)} relevant documents")
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        # Try to get collection info
        try:
            collection = self.vector_store._collection
            doc_count = collection.count()
        except:
            doc_count = len(self.documents)
        
        stats = {
            "status": "initialized",
            "total_documents": len(self.documents),
            "index_size": doc_count,
            "docs_folder": self.docs_folder,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
        
        # Count source files
        if self.documents:
            source_files = set(doc.metadata.get("source_file", "unknown") for doc in self.documents)
            stats["source_files"] = list(source_files)
            stats["num_source_files"] = len(source_files)
        
        return stats
    
    def add_document(self, file_path: str) -> bool:
        """Add a single document to the vector store."""
        try:
            print(f"📄 Adding document: {file_path}")
            
            # Load the document
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata.update({
                    "source_file": os.path.basename(file_path),
                    "file_path": file_path
                })
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(docs)
            
            # Add to existing vector store or create new one
            if self.vector_store:
                # Add to existing store
                self.vector_store.add_documents(chunks)
                self.vector_store.persist()
            else:
                # Create new store
                self.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                self.vector_store.persist()
            
            # Update documents list
            self.documents.extend(chunks)
            
            print(f"✅ Successfully added {len(chunks)} chunks from {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding document {file_path}: {str(e)}")
            return False 