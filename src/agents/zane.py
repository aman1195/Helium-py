from typing import Dict, Any, Optional, List
from ..core.config import Config
from .base_agent import BaseAgent, AgentResponse
import logging

logger = logging.getLogger(__name__)

class Zane(BaseAgent):
    """Zane - The Team Leader Agent"""
    
    def __init__(self, llm_config: Optional[Dict] = None):
        super().__init__(
            name="Zane",
            role="Team Leader",
            llm_config=llm_config or Config.get_llm_config()
        )
        self.team_members = {}  # Will store references to other agents
    
    async def process(self, task: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a task by delegating to the appropriate team member."""
        logger.info(f"Zane received task: {task}")
        
        # Simple task routing based on keywords
        # This can be enhanced with more sophisticated routing logic
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ["data", "analyze", "collect"]):
            return await self.delegate_to("Mira", task, context)
        elif any(keyword in task_lower for keyword in ["financial", "market size", "valuation"]):
            return await self.delegate_to("Chloe", task, context)
        elif any(keyword in task_lower for keyword in ["strategy", "competitive", "business model"]):
            return await self.delegate_to("Axel", task, context)
        else:
            # If no clear delegation, handle it directly
            return await self.handle_directly(task, context)
    
    async def delegate_to(self, agent_name: str, task: str, context: Optional[Dict] = None) -> AgentResponse:
        """Delegate a task to a specific team member."""
        if agent_name not in self.team_members:
            return AgentResponse(
                success=False,
                content=f"Error: {agent_name} is not part of the team yet."
            )
        
        logger.info(f"Delegating to {agent_name}: {task}")
        try:
            agent = self.team_members[agent_name]
            result = await agent.process(task, context or {})
            
            # Log the delegation
            self.add_to_memory({
                "type": "delegation",
                "to": agent_name,
                "task": task,
                "result": "success" if result.success else "failed"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in delegation to {agent_name}: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Error processing task with {agent_name}: {str(e)}"
            )
    
    async def handle_directly(self, task: str, context: Optional[Dict] = None) -> AgentResponse:
        """Handle a task directly when no clear delegation is possible."""
        logger.info(f"Handling task directly: {task}")
        task_lower = task.lower().strip()
        
        # Simple response mapping for common greetings
        greetings = ["hi", "hello", "hey", "greetings"]
        if any(greeting == task_lower for greeting in greetings):
            return AgentResponse(
                success=True,
                content={
                    "message": "Hello! I'm Zane, your team leader. I can help you with:"
                             "\n• Data analysis and research (ask Mira)"
                             "\n• Financial insights and valuations (ask Chloe)"
                             "\n• Business strategy and planning (ask Axel)"
                             "\n\nHow can I assist you today?",
                    "suggestions": [
                        "Analyze market data",
                        "Financial projections",
                        "Business strategy"
                    ]
                }
            )
        
        # Check for specific types of queries
        if any(word in task_lower for word in ["data", "analyze", "research"]):
            return AgentResponse(
                success=True,
                content={
                    "message": f"I'll connect you with Mira, our Data Scientist, to help with: {task}",
                    "action": "delegate",
                    "delegate_to": "Mira",
                    "original_task": task
                }
            )
        elif any(word in task_lower for word in ["financial", "market", "valuation", "revenue"]):
            return AgentResponse(
                success=True,
                content={
                    "message": f"I'll connect you with Chloe, our Financial Analyst, to help with: {task}",
                    "action": "delegate",
                    "delegate_to": "Chloe",
                    "original_task": task
                }
            )
        elif any(word in task_lower for word in ["strategy", "business", "plan", "market", "competitive"]):
            return AgentResponse(
                success=True,
                content={
                    "message": f"I'll connect you with Axel, our Business Strategist, to help with: {task}",
                    "action": "delegate",
                    "delegate_to": "Axel",
                    "original_task": task
                }
            )
            
        # For other tasks, provide a general response
        return AgentResponse(
            success=True,
            content={
                "message": f"I've received your request about: {task}"
                          "\n\nI can help connect you with the right expert. "
                          "Could you tell me more about what you're looking for?",
                "suggestions": [
                    "I need data analysis",
                    "I need financial insights",
                    "I need business strategy"
                ]
            }
        )
    
    def add_team_member(self, agent) -> None:
        """Add a team member that Zane can delegate to."""
        self.team_members[agent.name] = agent
        logger.info(f"Added team member: {agent.name} ({agent.role})")
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get the status of the team."""
        return {
            "team_members": list(self.team_members.keys()),
            "recent_activities": self.memory[-5:],  # Last 5 activities
            "status": "operational"
        }
