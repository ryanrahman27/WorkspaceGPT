from typing import List, Dict, Any
import openai
from openai import OpenAI
import json
import re


class PlannerAgent:
    """Agent responsible for breaking down user queries into actionable steps."""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.agent_name = "Planner"
        
        # System prompt for the planner
        self.system_prompt = """You are a smart planning agent in a multi-agent AI assistant system. Your role is to analyze user queries and break them down into clear, actionable steps that other agents can execute.

The system has these agents available:
1. Retriever Agent: Can search and retrieve relevant information from PDF documents
2. Executor Agent: Can perform actions like create_task(), summarize(), create_checklist(), analyze_content(), etc.

Your task is to:
1. Analyze the user's request
2. Break it down into logical steps
3. Assign each step to the appropriate agent
4. Provide clear instructions for each step

Return your response as a JSON object with this structure:
{
    "analysis": "Brief analysis of the user's request",
    "steps": [
        {
            "step_number": 1,
            "agent": "Retriever|Executor",
            "action": "search|summarize|create_task|create_checklist|analyze_content",
            "description": "Clear description of what needs to be done",
            "parameters": {
                "query": "specific search terms for retriever",
                "title": "title for tasks/checklists",
                "content": "content to process for executor"
            }
        }
    ],
    "expected_outcome": "What the user should expect as final result"
}

Guidelines:
- For document searches, use specific keywords (e.g., "onboarding", "benefits", "policies") not generic phrases
- Use "create_checklist" action for creating checklists, not "create_task"
- Use "create_task" only for individual tasks
- Always include a "title" parameter for create_task and create_checklist actions
- Be specific about what each step should accomplish
- Keep steps logical and sequential
- Make sure the final steps lead to the user's desired outcome"""

    def plan(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a plan for the given user query."""
        
        # Prepare the prompt
        user_prompt = f"""User Query: "{user_query}"

Please analyze this query and create a step-by-step plan to fulfill the user's request."""

        # Add context if available
        if context:
            user_prompt += f"\n\nAdditional Context: {json.dumps(context, indent=2)}"

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                plan = json.loads(content)
                
                # Validate the plan structure
                if self._validate_plan(plan):
                    return {
                        "success": True,
                        "plan": plan,
                        "raw_response": content
                    }
                else:
                    return {
                        "success": False,
                        "error": "Generated plan has invalid structure",
                        "raw_response": content
                    }
                    
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        plan = json.loads(json_match.group())
                        if self._validate_plan(plan):
                            return {
                                "success": True,
                                "plan": plan,
                                "raw_response": content
                            }
                    except json.JSONDecodeError:
                        pass
                
                return {
                    "success": False,
                    "error": "Could not parse response as JSON",
                    "raw_response": content
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}",
                "raw_response": None
            }
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate that the plan has the required structure."""
        required_fields = ["analysis", "steps", "expected_outcome"]
        
        # Check top-level fields
        if not all(field in plan for field in required_fields):
            return False
        
        # Check steps structure
        if not isinstance(plan["steps"], list) or len(plan["steps"]) == 0:
            return False
        
        # Validate each step
        for step in plan["steps"]:
            step_fields = ["step_number", "agent", "action", "description"]
            if not all(field in step for field in step_fields):
                return False
            
            # Validate agent names
            if step["agent"] not in ["Retriever", "Executor"]:
                return False
        
        return True
    
    def refine_plan(self, original_plan: Dict[str, Any], 
                   feedback: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Refine an existing plan based on feedback."""
        
        # Prepare the refinement prompt
        refinement_prompt = f"""Original Plan:
{json.dumps(original_plan, indent=2)}

Feedback: {feedback}

Please refine the plan based on the feedback provided. Return the updated plan in the same JSON format."""
        
        # Add context if available
        if context:
            refinement_prompt += f"\n\nAdditional Context: {json.dumps(context, indent=2)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": refinement_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                refined_plan = json.loads(content)
                
                if self._validate_plan(refined_plan):
                    return {
                        "success": True,
                        "plan": refined_plan,
                        "raw_response": content
                    }
                else:
                    return {
                        "success": False,
                        "error": "Refined plan has invalid structure",
                        "raw_response": content
                    }
                    
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        refined_plan = json.loads(json_match.group())
                        if self._validate_plan(refined_plan):
                            return {
                                "success": True,
                                "plan": refined_plan,
                                "raw_response": content
                            }
                    except json.JSONDecodeError:
                        pass
                
                return {
                    "success": False,
                    "error": "Could not parse refined response as JSON",
                    "raw_response": content
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API error during refinement: {str(e)}",
                "raw_response": None
            }
    
    def get_step_details(self, plan: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """Get details for a specific step in the plan."""
        if "steps" not in plan or not isinstance(plan["steps"], list):
            return {"error": "Invalid plan structure"}
        
        for step in plan["steps"]:
            if step.get("step_number") == step_number:
                return step
        
        return {"error": f"Step {step_number} not found in plan"} 