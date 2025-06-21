"""
Integration test for Helium AI

This script tests the integration between all agents in the Helium AI system.
"""

import asyncio
import json
import logging
from src.agents import Zane, Mira, Chloe, Axel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestHeliumAI:
    """Integration test class for Helium AI."""
    
    def __init__(self):
        """Initialize the test class with all agents."""
        self.zane = Zane()
        self.mira = Mira()
        self.chloe = Chloe()
        self.axel = Axel()
        
        # Set up the team
        self.zane.add_team_member(self.mira)
        self.zane.add_team_member(self.chloe)
        self.zane.add_team_member(self.axel)
    
    async def run_test(self, task: str):
        """Run a test with the given task."""
        print(f"\n{'='*80}")
        print(f"TESTING TASK: {task}")
        print(f"{'='*80}")
        
        # Process the task with Zane (who will delegate as needed)
        result = await self.zane.process(task)
        
        # Print the result
        print("\nRESULT:")
        print(json.dumps(result.content, indent=2, default=str))
        print(f"\nSuccess: {result.success}")
        
        # Print agent's memory
        print("\nZane's memory:")
        for i, memory in enumerate(self.zane.memory[-3:], 1):  # Show last 3 memories
            print(f"{i}. {memory}")

async def main():
    """Main test function."""
    tester = TestHeliumAI()
    
    # Test cases
    test_cases = [
        "Find recent trends in AI research",
        "What's the financial outlook for AI startups?",
        "Analyze the competitive landscape for AI tools in healthcare",
        "Create a business strategy for an AI-powered research platform"
    ]
    
    for task in test_cases:
        await tester.run_test(task)
        
        # Add a separator between tests
        if task != test_cases[-1]:
            input("\nPress Enter to run the next test...")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
