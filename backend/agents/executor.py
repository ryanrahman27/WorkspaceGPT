from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from openai import OpenAI


class ExecutorAgent:
    """Agent responsible for executing actions based on plan steps."""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.agent_name = "Executor"
        self.tasks = []  # In-memory task storage
        self.reports = []  # In-memory report storage
        
        # Available actions
        self.available_actions = {
            "create_task": self.create_task,
            "summarize": self.summarize,
            "generate_report": self.generate_report,
            "create_checklist": self.create_checklist,
            "analyze_content": self.analyze_content
        }
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action with given parameters."""
        
        if action not in self.available_actions:
            return {
                "success": False,
                "action": action,
                "error": f"Unknown action: {action}. Available: {list(self.available_actions.keys())}",
                "result": None
            }
        
        try:
            result = self.available_actions[action](**parameters)
            return {
                "success": True,
                "action": action,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "parameters": parameters,
                "error": f"Execution failed: {str(e)}",
                "result": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def create_task(self, title: str, description: str = "", 
                   priority: str = "medium", **kwargs) -> Dict[str, Any]:
        """Create a new task."""
        
        task_id = f"task_{len(self.tasks) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        
        return {
            "task_id": task_id,
            "task": task,
            "message": f"✅ Task '{title}' created successfully"
        }
    
    def summarize(self, content: str, max_length: int = 200, **kwargs) -> Dict[str, Any]:
        """Summarize the given content using OpenAI."""
        
        prompt = f"""Please summarize the following content in bullet points (max {max_length} words):

{content}

Return a concise summary in bullet point format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_length * 2
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary),
                "message": f"📝 Content summarized successfully"
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "error": str(e),
                "message": "❌ Failed to generate summary"
            }
    
    def generate_report(self, title: str, sections: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate a formatted report from sections of content."""
        
        report_id = f"report_{len(self.reports) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate markdown report
        report_content = f"# {title}\n\n"
        report_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for section in sections:
            section_title = section.get("title", "Section")
            section_content = section.get("content", "")
            
            report_content += f"## {section_title}\n\n"
            report_content += f"{section_content}\n\n"
        
        report = {
            "id": report_id,
            "title": title,
            "content": report_content,
            "sections": sections,
            "created_at": datetime.now().isoformat()
        }
        
        self.reports.append(report)
        
        return {
            "report_id": report_id,
            "report": report,
            "message": f"📊 Report '{title}' generated successfully"
        }
    
    def create_checklist(self, title: str, content: str = "", **kwargs) -> Dict[str, Any]:
        """Create a checklist from content."""
        
        prompt = f"""Extract actionable checklist items from the following content:

{content}

Return a numbered list of clear, actionable items."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting actionable tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            checklist_text = response.choices[0].message.content.strip()
            
            # Parse items (simple parsing)
            items = []
            for line in checklist_text.split('\n'):
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '•')):
                    item_text = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    items.append({"item": item_text, "completed": False})
            
            checklist = {
                "title": title,
                "items": items,
                "total_items": len(items),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "checklist": checklist,
                "message": f"📋 Checklist '{title}' created with {len(items)} items"
            }
            
        except Exception as e:
            return {
                "checklist": {"title": title, "items": [], "total_items": 0},
                "error": str(e),
                "message": "❌ Failed to create checklist"
            }
    
    def analyze_content(self, content: str, analysis_type: str = "general", **kwargs) -> Dict[str, Any]:
        """Analyze content for insights."""
        
        prompt = f"""Analyze this content and provide key insights and important points:

{content}

Provide a structured analysis with clear sections."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "analysis": analysis,
                "analysis_type": analysis_type,
                "message": f"🔍 Content analysis completed successfully"
            }
            
        except Exception as e:
            return {
                "analysis": f"Error during analysis: {str(e)}",
                "error": str(e),
                "message": "❌ Content analysis failed"
            }
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all created tasks."""
        return self.tasks
    
    def get_reports(self) -> List[Dict[str, Any]]:
        """Get all generated reports."""
        return self.reports 