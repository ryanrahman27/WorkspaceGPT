from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ContextEntry:
    """Represents a single entry in the conversation context."""
    timestamp: datetime
    agent: str
    action: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationContext:
    """Maintains the full context of a conversation session."""
    session_id: str
    user_query: str
    entries: List[ContextEntry] = field(default_factory=list)
    current_step: int = 0
    status: str = "active"  # active, completed, error
    
    def add_entry(self, agent: str, action: str, input_data: Dict[str, Any], 
                  output_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Add a new entry to the conversation context."""
        entry = ContextEntry(
            timestamp=datetime.now(),
            agent=agent,
            action=action,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata
        )
        self.entries.append(entry)
        self.current_step += 1
        return entry
    
    def get_agent_history(self, agent: str) -> List[ContextEntry]:
        """Get all entries for a specific agent."""
        return [entry for entry in self.entries if entry.agent == agent]
    
    def get_latest_output(self, agent: str) -> Optional[Dict[str, Any]]:
        """Get the latest output from a specific agent."""
        agent_entries = self.get_agent_history(agent)
        return agent_entries[-1].output_data if agent_entries else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_query": self.user_query,
            "current_step": self.current_step,
            "status": self.status,
            "entries": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "agent": entry.agent,
                    "action": entry.action,
                    "input_data": entry.input_data,
                    "output_data": entry.output_data,
                    "metadata": entry.metadata
                }
                for entry in self.entries
            ]
        }


class ContextManager:
    """Manages conversation contexts for the multi-agent system."""
    
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
        self.active_context: Optional[ConversationContext] = None
    
    def create_context(self, session_id: str, user_query: str) -> ConversationContext:
        """Create a new conversation context."""
        context = ConversationContext(session_id=session_id, user_query=user_query)
        self.contexts[session_id] = context
        self.active_context = context
        print(f"🚀 Created new conversation context: {session_id}")
        print(f"📝 User Query: {user_query}")
        return context
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get an existing conversation context."""
        return self.contexts.get(session_id)
    
    def set_active_context(self, session_id: str) -> bool:
        """Set the active conversation context."""
        if session_id in self.contexts:
            self.active_context = self.contexts[session_id]
            return True
        return False
    
    def log_agent_action(self, agent: str, action: str, input_data: Dict[str, Any], 
                        output_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Log an agent action to the active context."""
        if not self.active_context:
            raise ValueError("No active context available")
        
        entry = self.active_context.add_entry(agent, action, input_data, output_data, metadata)
        
        # Console logging
        print(f"\n{'='*60}")
        print(f"🤖 Agent: {agent}")
        print(f"⚡ Action: {action}")
        print(f"📥 Input: {json.dumps(input_data, indent=2)}")
        print(f"📤 Output: {json.dumps(output_data, indent=2)}")
        if metadata:
            print(f"🔍 Metadata: {json.dumps(metadata, indent=2)}")
        print(f"⏰ Timestamp: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        return entry
    
    def get_context_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of the conversation context."""
        context = self.active_context if session_id is None else self.get_context(session_id)
        if not context:
            return {}
        
        summary = {
            "session_id": context.session_id,
            "user_query": context.user_query,
            "total_steps": len(context.entries),
            "current_step": context.current_step,
            "status": context.status,
            "agents_involved": list(set(entry.agent for entry in context.entries)),
            "last_updated": context.entries[-1].timestamp.isoformat() if context.entries else None
        }
        
        return summary
    
    def export_context(self, session_id: str) -> Optional[str]:
        """Export context as JSON string."""
        context = self.get_context(session_id)
        if context:
            return json.dumps(context.to_dict(), indent=2)
        return None 