from typing import List, Dict, Any, Optional
from vector_store.chroma_store import ChromaVectorStore  # Changed to ChromaDB


class RetrieverAgent:
    """Agent responsible for retrieving relevant information from PDF documents."""
    
    def __init__(self, vector_store: ChromaVectorStore):  # Changed type hint
        self.vector_store = vector_store
        self.agent_name = "Retriever"
    
    def search(self, query: str, k: int = 4, score_threshold: float = 0.3) -> Dict[str, Any]:
        """Perform a search query against the vector store."""
        
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search(
                query=query, 
                k=k, 
                score_threshold=score_threshold
            )
            
            # Process and format results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_result = {
                    "rank": i + 1,
                    "content": result["content"],
                    "source_file": result["metadata"].get("source_file", "unknown"),
                    "page": result["metadata"].get("page", "unknown"),
                    "chunk_id": result["metadata"].get("chunk_id", "unknown"),
                    "similarity_score": round(result["similarity_score"], 4),
                    "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                }
                formatted_results.append(formatted_result)
            
            # Generate summary of search results
            summary = self._generate_search_summary(query, formatted_results)
            
            return {
                "success": True,
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results,
                "summary": summary,
                "search_parameters": {
                    "k": k,
                    "score_threshold": score_threshold
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": f"Search failed: {str(e)}",
                "results": [],
                "total_results": 0
            }
    
    def search_by_document(self, query: str, source_file: str, k: int = 3) -> Dict[str, Any]:
        """Search within a specific document."""
        
        try:
            # First, get all results
            all_results = self.vector_store.similarity_search(query=query, k=k*3)
            
            # Filter by source file
            filtered_results = [
                result for result in all_results 
                if result["metadata"].get("source_file", "").lower() == source_file.lower()
            ]
            
            # Take top k results
            filtered_results = filtered_results[:k]
            
            # Format results
            formatted_results = []
            for i, result in enumerate(filtered_results):
                formatted_result = {
                    "rank": i + 1,
                    "content": result["content"],
                    "source_file": result["metadata"].get("source_file", "unknown"),
                    "page": result["metadata"].get("page", "unknown"),
                    "chunk_id": result["metadata"].get("chunk_id", "unknown"),
                    "similarity_score": round(result["similarity_score"], 4),
                    "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                }
                formatted_results.append(formatted_result)
            
            summary = self._generate_search_summary(query, formatted_results, source_file)
            
            return {
                "success": True,
                "query": query,
                "source_file": source_file,
                "total_results": len(formatted_results),
                "results": formatted_results,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "source_file": source_file,
                "error": f"Document search failed: {str(e)}",
                "results": [],
                "total_results": 0
            }
    
    def get_document_list(self) -> Dict[str, Any]:
        """Get a list of all available documents in the vector store."""
        
        try:
            stats = self.vector_store.get_stats()
            
            if stats.get("status") != "initialized":
                return {
                    "success": False,
                    "error": "Vector store not initialized",
                    "documents": []
                }
            
            documents = stats.get("source_files", [])
            
            # Get additional info for each document
            document_info = []
            for doc in documents:
                # Count chunks for this document
                chunk_count = sum(
                    1 for chunk in self.vector_store.documents 
                    if chunk.metadata.get("source_file") == doc
                )
                
                document_info.append({
                    "filename": doc,
                    "chunk_count": chunk_count,
                    "available": True
                })
            
            return {
                "success": True,
                "total_documents": len(documents),
                "documents": document_info,
                "vector_store_stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get document list: {str(e)}",
                "documents": []
            }
    
    def search_multiple_queries(self, queries: List[str], k: int = 3) -> Dict[str, Any]:
        """Perform multiple searches and combine results."""
        
        all_results = []
        search_summaries = []
        
        for query in queries:
            result = self.search(query, k=k)
            if result["success"]:
                all_results.extend(result["results"])
                search_summaries.append({
                    "query": query,
                    "result_count": result["total_results"],
                    "summary": result["summary"]
                })
        
        # Remove duplicates based on chunk_id
        seen_chunks = set()
        unique_results = []
        
        for result in all_results:
            chunk_id = result.get("chunk_id")
            if chunk_id not in seen_chunks:
                seen_chunks.add(chunk_id)
                unique_results.append(result)
        
        # Sort by similarity score
        unique_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Re-rank
        for i, result in enumerate(unique_results):
            result["rank"] = i + 1
        
        return {
            "success": True,
            "queries": queries,
            "total_unique_results": len(unique_results),
            "results": unique_results,
            "search_summaries": search_summaries
        }
    
    def get_content_by_source(self, source_file: str, max_chunks: int = 10) -> Dict[str, Any]:
        """Get content from a specific source document."""
        
        try:
            # Get all chunks from the specified source
            source_chunks = [
                chunk for chunk in self.vector_store.documents
                if chunk.metadata.get("source_file", "").lower() == source_file.lower()
            ]
            
            if not source_chunks:
                return {
                    "success": False,
                    "error": f"No content found for source: {source_file}",
                    "content": []
                }
            
            # Sort by chunk_id or page number
            source_chunks.sort(key=lambda x: (
                x.metadata.get("page", 0),
                x.metadata.get("chunk_id", 0)
            ))
            
            # Limit results
            source_chunks = source_chunks[:max_chunks]
            
            # Format content
            formatted_content = []
            for chunk in source_chunks:
                formatted_content.append({
                    "content": chunk.page_content,
                    "page": chunk.metadata.get("page", "unknown"),
                    "chunk_id": chunk.metadata.get("chunk_id", "unknown"),
                    "chunk_size": len(chunk.page_content)
                })
            
            return {
                "success": True,
                "source_file": source_file,
                "total_chunks": len(formatted_content),
                "content": formatted_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get content for {source_file}: {str(e)}",
                "content": []
            }
    
    def _generate_search_summary(self, query: str, results: List[Dict[str, Any]], 
                                source_file: Optional[str] = None) -> str:
        """Generate a summary of search results."""
        
        if not results:
            return f"No relevant results found for query: '{query}'"
        
        # Count sources
        sources = set(result["source_file"] for result in results)
        
        summary_parts = [
            f"Found {len(results)} relevant results for query: '{query}'"
        ]
        
        if source_file:
            summary_parts.append(f"from document: {source_file}")
        else:
            summary_parts.append(f"across {len(sources)} document(s): {', '.join(sorted(sources))}")
        
        # Add score range
        if results:
            max_score = max(result["similarity_score"] for result in results)
            min_score = min(result["similarity_score"] for result in results)
            summary_parts.append(f"Similarity scores range from {min_score:.3f} to {max_score:.3f}")
        
        return ". ".join(summary_parts) + "." 