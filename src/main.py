import asyncio
import logging
import json
from dotenv import load_dotenv
from agents.zane import Zane
from agents.mira import Mira
from agents.chloe import Chloe
from agents.axel import Axel
from core.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HeliumAI:
    """Main Helium AI application class."""
    
    def __init__(self):
        """Initialize the Helium AI application with all agents."""
        self.zane = None
        self.mira = None
        self.chloe = None
        self.axel = None
    
    async def initialize(self):
        """Initialize all agents and set up the team."""
        logger.info("Initializing Helium AI...")
        
        # Initialize all agents
        self.zane = Zane()
        self.mira = Mira()
        self.chloe = Chloe()
        self.axel = Axel()
        
        # Add team members to Zane (Team Leader)
        self.zane.add_team_member(self.mira)
        self.zane.add_team_member(self.chloe)
        self.zane.add_team_member(self.axel)
        
        logger.info("Helium AI initialization complete")
    
    async def process_task(self, task: str) -> dict:
        """Process a task using the Helium AI team."""
        logger.info(f"Processing task: {task}")
        
        # Start with Zane (Team Leader)
        result = await self.zane.process(task)
        
        # Format the response
        response = {
            "task": task,
            "success": result.success,
            "result": result.content,
            "agent": "Zane (Team Leader)"
        }
        
        return response

async def demo():
    """Run a demo of Helium AI's capabilities."""
    try:
        # Initialize the application
        helium_ai = HeliumAI()
        await helium_ai.initialize()
        
        # Example tasks to demonstrate different capabilities
        tasks = [
            "Analyze the competitive landscape for AI-powered research tools",
            "What's the market size for AI in financial services?",
            "Create a business model for a startup in the AI research space"
        ]
        
        # Process each task
        for i, task in enumerate(tasks, 1):
            print(f"\n{'='*50}")
            print(f"TASK {i}: {task}")
            print(f"{'='*50}")
            
            result = await helium_ai.process_task(task)
            
            # Print the result in a readable format
            print("\nRESULT:")
            print(json.dumps(result, indent=2, default=str))
            
            # Add a small delay between tasks for better readability
            if i < len(tasks):
                print("\n" + "-"*50)
                input("Press Enter to continue to the next task...")
        
        print("\nDemo complete!")
        
    except Exception as e:
        logger.error(f"An error occurred during the demo: {str(e)}", exc_info=True)
        return 1
    
    return 0

async def main():
    """Main entry point for the Helium AI application."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Validate configuration
        Config.validate()
        
        # Run the demo
        return await demo()
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
