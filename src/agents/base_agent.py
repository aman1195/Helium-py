from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    """Standard response format for agent operations."""
    success: bool
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent(ABC):
    """Base class for all Helium AI agents."""
    
    def __init__(self, name: str, role: str, llm_config: Optional[Dict] = None):
        """Initialize the base agent.
        
        Args:
            name: The name of the agent (e.g., 'Zane', 'Mira')
            role: The role of the agent (e.g., 'Team Leader', 'Data Scientist')
            llm_config: Configuration for the language model
        """
        self.name = name
        self.role = role
        self.llm_config = llm_config or {}
        self.memory = []  # Simple in-memory storage, can be replaced with a vector DB
    
    @abstractmethod
    async def process(self, task: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a task with optional context.
        
        Args:
            task: The task to process
            context: Additional context for the task
            
        Returns:
            AgentResponse containing the result of processing
        """
        pass
    
    def add_to_memory(self, content: Any, metadata: Optional[Dict] = None) -> None:
        """Add information to the agent's memory.
        
        Args:
            content: The content to remember
            metadata: Additional metadata about the content
        """
        self.memory.append({
            'content': content,
            'metadata': metadata or {}
        })
    
    def get_memory(self, query: Optional[str] = None) -> List[Dict]:
        """Retrieve relevant memories.
        
        Args:
            query: Optional query to filter memories
            
        Returns:
            List of relevant memories
        """
        # Simple implementation - can be enhanced with vector similarity search
        if query is None:
            return self.memory
        return [m for m in self.memory if query.lower() in str(m).lower()]
