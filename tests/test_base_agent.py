import pytest
from src.agents.base_agent import BaseAgent, AgentResponse

class TestAgent(BaseAgent):
    """A test implementation of BaseAgent for testing purposes."""
    
    async def process(self, task: str, context: dict = None) -> AgentResponse:
        """Echo the task back as a response."""
        return AgentResponse(
            success=True,
            content={"echo": task, "context": context or {}}
        )

@pytest.mark.asyncio
async def test_base_agent_initialization():
    """Test that a BaseAgent can be initialized."""
    agent = TestAgent("TestAgent", "Tester")
    assert agent.name == "TestAgent"
    assert agent.role == "Tester"
    assert len(agent.memory) == 0

@pytest.mark.asyncio
async def test_base_agent_process():
    """Test the process method of a BaseAgent implementation."""
    agent = TestAgent("TestAgent", "Tester")
    task = "test task"
    context = {"test": "value"}
    
    response = await agent.process(task, context)
    
    assert response.success is True
    assert response.content["echo"] == task
    assert response.content["context"] == context

@pytest.mark.asyncio
async def test_memory_functions():
    """Test the memory-related functions of BaseAgent."""
    agent = TestAgent("TestAgent", "Tester")
    
    # Test adding to memory
    agent.add_to_memory("Test memory content", {"type": "test"})
    assert len(agent.memory) == 1
    assert agent.memory[0]["content"] == "Test memory content"
    assert agent.memory[0]["metadata"]["type"] == "test"
    
    # Test retrieving all memories
    memories = agent.get_memory()
    assert len(memories) == 1
    
    # Test querying memories
    matching = agent.get_memory("memory content")
    assert len(matching) == 1
    
    non_matching = agent.get_memory("nonexistent")
    assert len(non_matching) == 0
