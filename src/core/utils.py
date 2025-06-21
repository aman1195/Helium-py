import json
from typing import Any, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise

def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        raise

def validate_response(response: Any, expected_type: type) -> bool:
    """Validate that a response matches the expected type."""
    if not isinstance(response, expected_type):
        logger.warning(
            f"Unexpected response type. Expected {expected_type.__name__}, "
            f"got {type(response).__name__}"
        )
        return False
    return True

def format_agent_response(success: bool, content: Any, **metadata) -> Dict[str, Any]:
    """Format a standardized response from an agent."""
    return {
        "success": success,
        "content": content,
        "metadata": metadata or {}
    }
