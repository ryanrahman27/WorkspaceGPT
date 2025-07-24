import os
import sys
from typing import Dict, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from context.context_manager import ContextManager
from vector_store.chroma_store import ChromaVectorStore  # Using ChromaDB instead of FAISS
from agents.planner import PlannerAgent
from agents.retriever import RetrieverAgent
from agents.executor import ExecutorAgent


class WorkspaceGPT:
    """Main orchestrator for the multi-agent AI assistant system (ChromaDB version)."""
    
    def __init__(self):
        # Load environment variables from parent directory
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize components
        print("🚀 Initializing WorkspaceGPT (ChromaDB version)...")
        
        # Context Manager
        self.context_manager = ContextManager()
        
        # Vector Store (using ChromaDB)
        self.vector_store = ChromaVectorStore(
            docs_folder="docs",  # relative to backend directory
            persist_directory="vector_store/chroma_db"  # relative to backend directory
        )
        
        # Agents
        self.planner = PlannerAgent(self.openai_client)
        self.retriever = RetrieverAgent(self.vector_store)
        self.executor = ExecutorAgent(self.openai_client)
        
        # Initialize vector store
        print("🔄 Setting up ChromaDB vector store...")
        self.vector_store.create_vector_store()
        
        print("✅ WorkspaceGPT (ChromaDB) initialized successfully!")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query through the multi-agent pipeline."""
        
        # Create a new conversation context
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        context = self.context_manager.create_context(session_id, user_query)
        
        try:
            # Step 1: Planning Phase
            print("\n" + "="*60)
            print("🧠 PLANNING PHASE")
            print("="*60)
            
            plan_result = self.planner.plan(user_query)
            
            self.context_manager.log_agent_action(
                agent="Planner",
                action="create_plan",
                input_data={"user_query": user_query},
                output_data=plan_result
            )
            
            if not plan_result.get("success"):
                context.status = "error"
                return {
                    "session_id": session_id,
                    "success": False,
                    "error": "Planning failed",
                    "details": plan_result
                }
            
            plan = plan_result["plan"]
            print(f"📋 Generated plan with {len(plan['steps'])} steps")
            
            # Step 2: Execute plan steps
            print("\n" + "="*60)
            print("⚡ EXECUTION PHASE")
            print("="*60)
            
            step_results = []
            retrieved_content = []  # Store content for later use
            
            for step in plan["steps"]:
                step_number = step["step_number"]
                agent_name = step["agent"]
                action = step["action"]
                description = step["description"]
                parameters = step.get("parameters", {})
                
                print(f"\n🔄 Executing Step {step_number}: {description}")
                
                if agent_name == "Retriever":
                    # Handle retriever steps
                    result = self._execute_retriever_step(action, parameters)
                    
                    # Store retrieved content for use by executor
                    if result.get("success") and result.get("results"):
                        retrieved_content.extend([
                            {"source": r["source_file"], "content": r["content"]}
                            for r in result["results"]
                        ])
                
                elif agent_name == "Executor":
                    # Handle executor steps
                    # Add retrieved content to parameters if available
                    if retrieved_content:
                        parameters["retrieved_content"] = retrieved_content
                    
                    result = self._execute_executor_step(action, parameters)
                
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown agent: {agent_name}"
                    }
                
                # Log the step execution
                self.context_manager.log_agent_action(
                    agent=agent_name,
                    action=action,
                    input_data={"step": step, "parameters": parameters},
                    output_data=result
                )
                
                step_results.append({
                    "step_number": step_number,
                    "agent": agent_name,
                    "action": action,
                    "description": description,
                    "result": result,
                    "success": result.get("success", False)
                })
            
            # Step 3: Final Summary
            print("\n" + "="*60)
            print("📊 SUMMARY")
            print("="*60)
            
            successful_steps = [s for s in step_results if s["success"]]
            failed_steps = [s for s in step_results if not s["success"]]
            
            print(f"✅ Successful steps: {len(successful_steps)}")
            print(f"❌ Failed steps: {len(failed_steps)}")
            
            # Generate final summary
            final_summary = self._generate_final_summary(
                user_query, plan, step_results, retrieved_content
            )
            
            context.status = "completed" if not failed_steps else "completed_with_errors"
            
            return {
                "session_id": session_id,
                "success": True,
                "user_query": user_query,
                "plan": plan,
                "step_results": step_results,
                "retrieved_content": retrieved_content,
                "final_summary": final_summary,
                "context_summary": self.context_manager.get_context_summary()
            }
            
        except Exception as e:
            context.status = "error"
            print(f"❌ Error during processing: {str(e)}")
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "user_query": user_query
            }
    
    def _execute_retriever_step(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a retriever step."""
        
        query = parameters.get("query", "")
        k = parameters.get("k", 4)
        
        if action == "search":
            return self.retriever.search(query, k=k)
        
        elif action == "search_by_document":
            source_file = parameters.get("source_file", "")
            return self.retriever.search_by_document(query, source_file, k=k)
        
        elif action == "get_documents":
            return self.retriever.get_document_list()
        
        else:
            return {
                "success": False,
                "error": f"Unknown retriever action: {action}"
            }
    
    def _execute_executor_step(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an executor step."""
        
        # Prepare content for summarization/analysis
        if "retrieved_content" in parameters and action in ["summarize", "analyze_content", "create_checklist"]:
            # Combine retrieved content
            combined_content = "\n\n".join([
                f"From {item['source']}: {item['content']}"
                for item in parameters["retrieved_content"]
            ])
            parameters["content"] = combined_content
            # Remove retrieved_content from parameters to avoid confusion
            del parameters["retrieved_content"]
        
        # Fix parameter mapping for create_task
        if action == "create_task":
            # Map task_type to title if needed
            if "task_type" in parameters and "title" not in parameters:
                parameters["title"] = parameters["task_type"]
                del parameters["task_type"]
            
            # Ensure we have a title
            if "title" not in parameters:
                parameters["title"] = "Generated Task"
        
        # Fix parameter mapping for create_checklist
        if action == "create_checklist":
            # Ensure we have a title
            if "title" not in parameters:
                parameters["title"] = "Generated Checklist"
        
        return self.executor.execute(action, parameters)
    
    def _generate_final_summary(self, user_query: str, plan: Dict[str, Any], 
                               step_results: list, retrieved_content: list) -> Dict[str, Any]:
        """Generate a final summary of the entire process."""
        
        summary = {
            "user_query": user_query,
            "plan_analysis": plan.get("analysis", ""),
            "expected_outcome": plan.get("expected_outcome", ""),
            "total_steps": len(step_results),
            "successful_steps": len([s for s in step_results if s["success"]]),
            "failed_steps": len([s for s in step_results if not s["success"]]),
            "retrieved_documents": len(set(item["source"] for item in retrieved_content)),
            "key_achievements": []
        }
        
        # Extract key achievements from successful steps
        for step in step_results:
            if step["success"] and step["result"]:
                result = step["result"]
                
                if step["agent"] == "Retriever":
                    summary["key_achievements"].append(
                        f"Retrieved {result.get('total_results', 0)} relevant documents for '{step['description']}'"
                    )
                
                elif step["agent"] == "Executor":
                    if step["action"] == "create_task":
                        task_title = result.get("result", {}).get("task", {}).get("title", "Unknown")
                        summary["key_achievements"].append(f"Created task: {task_title}")
                    
                    elif step["action"] == "summarize":
                        summary["key_achievements"].append("Generated content summary")
                    
                    elif step["action"] == "generate_report":
                        report_title = result.get("result", {}).get("report", {}).get("title", "Unknown")
                        summary["key_achievements"].append(f"Generated report: {report_title}")
                    
                    elif step["action"] == "create_checklist":
                        item_count = result.get("result", {}).get("checklist", {}).get("total_items", 0)
                        summary["key_achievements"].append(f"Created checklist with {item_count} items")
        
        return summary
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return self.vector_store.get_stats()
    
    def add_document(self, file_path: str) -> bool:
        """Add a document to the vector store."""
        return self.vector_store.add_document(file_path)


def main():
    """Main function to demonstrate the WorkspaceGPT system."""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in a .env file or as an environment variable")
        return
    
    # Initialize WorkspaceGPT
    try:
        workspace_gpt = WorkspaceGPT()
    except Exception as e:
        print(f"❌ Failed to initialize WorkspaceGPT: {str(e)}")
        return
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎯 WORKSPACEGPT - Multi-Agent AI Assistant (ChromaDB)")
    print("="*60)
    print("Enter your queries below (or 'quit' to exit)")
    print("Example: 'Summarize my onboarding and create a checklist'")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n💬 Your query: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process the query
            result = workspace_gpt.process_query(user_input)
            
            if result.get("success"):
                print("\n🎉 Processing completed successfully!")
                print(f"📄 View full results in session: {result['session_id']}")
                
                # Show final summary
                final_summary = result.get("final_summary", {})
                if final_summary.get("key_achievements"):
                    print("\n🏆 Key Achievements:")
                    for achievement in final_summary["key_achievements"]:
                        print(f"  • {achievement}")
            else:
                print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main() 