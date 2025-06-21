"""
Helium AI - Main Application

This is the main entry point for the Helium AI application.
It initializes all agents and sets up the web interface.
"""
import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents
from src.agents.zane import Zane
from src.agents.mira import Mira
from src.agents.chloe import Chloe
from src.agents.axel import Axel
from src.core.config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Initialize agents
agents = {}
conversation_history = []

class AgentManager:
    """Manages the lifecycle and interactions of all agents"""
    
    def __init__(self):
        self.agents = {}
        self.zane = None
        
    async def initialize(self):
        """Initialize all agents and set up their relationships"""
        try:
            # Load configuration
            Config.validate()
            llm_config = Config.get_llm_config()
            
            # Initialize agents
            self.zane = Zane(llm_config=llm_config)
            mira = Mira(llm_config=llm_config)
            chloe = Chloe(llm_config=llm_config)
            axel = Axel(llm_config=llm_config)
            
            # Set up the team
            self.zane.add_team_member(mira)
            self.zane.add_team_member(chloe)
            self.zane.add_team_member(axel)
            
            # Store agents for direct access
            self.agents = {
                'zane': self.zane,
                'mira': mira,
                'chloe': chloe,
                'axel': axel
            }
            
            logger.info("All agents initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}", exc_info=True)
            return False
    
    def get_agent(self, agent_id: str):
        """Get an agent by ID"""
        return self.agents.get(agent_id, self.zane)  # Default to Zane if agent not found
    
    async def process_message(self, message: str, agent_id: str, context: Optional[Dict] = None) -> Dict:
        """Process a message with the specified agent"""
        try:
            agent = self.get_agent(agent_id)
            response = await agent.process(message, context or {})
            return {
                "success": True,
                "response": {
                    "content": response.content,
                    "metadata": response.metadata
                }
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }

# Initialize the agent manager
agent_manager = AgentManager()

def initialize_agents():
    """Initialize all Helium AI agents"""
    try:
        # Run the async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(agent_manager.initialize())
        loop.close()
        
        if not success:
            logger.error("Failed to initialize agents")
            return False
            
        # Store agents in the global agents dict for backward compatibility
        global agents
        agents = agent_manager.agents
        return True
        
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}", exc_info=True)
        return False

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Helium AI - Multi-Agent System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #4a6fa5, #3a5a80);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 20px;
        }
        .chat-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 20px;
        }
        .chat-header {
            background: #4a6fa5;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-messages {
            height: 60vh;
            overflow-y: auto;
            padding: 20px;
            background-color: #f9fafc;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
            line-height: 1.4;
            position: relative;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            color: #0d47a1;
        }
        .assistant-message {
            background: white;
            margin-right: auto;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        .message-header {
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 0.9em;
        }
        .message-time {
            font-size: 0.75em;
            color: #757575;
            text-align: right;
            margin-top: 4px;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        #user-input {
            flex-grow: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 24px;
            outline: none;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        #user-input:focus {
            border-color: #4a6fa5;
            box-shadow: 0 0 0 2px rgba(74, 111, 165, 0.2);
        }
        #send-button {
            background: #4a6fa5;
            color: white;
            border: none;
            border-radius: 24px;
            padding: 0 24px;
            margin-left: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.3s;
        }
        #send-button:hover {
            background: #3a5a80;
        }
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            color: #666;
            font-style: italic;
        }
        .agent-selector {
            padding: 8px 12px;
            border-radius: 16px;
            border: 1px solid #ddd;
            margin-right: 10px;
            background: white;
            outline: none;
        }
        .status-bar {
            background: #f5f5f5;
            padding: 8px 15px;
            font-size: 0.85em;
            color: #666;
            border-top: 1px solid #eee;
        }
        .agent-tag {
            display: inline-block;
            background: #e3f2fd;
            color: #1565c0;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Helium AI</h1>
        <p>Multi-Agent Collaboration Platform</p>
    </div>
    
    <div class="chat-container">
        <div class="chat-header">
            <div>Agent Conversation</div>
            <div class="status" id="status">Connected</div>
        </div>
        
        <div id="chat-messages" class="chat-messages">
            <div class="message assistant-message">
                <div class="message-header">Helium AI <span class="agent-tag">System</span></div>
                <div>Hello! I'm your Helium AI assistant. How can I help you today?</div>
                <div class="message-time">Just now</div>
            </div>
        </div>
        
        <div class="input-area">
            <select id="agent-selector" class="agent-selector">
                <option value="zane">Zane (Team Leader)</option>
                <option value="mira">Mira (Data Scientist)</option>
                <option value="chloe">Chloe (Financial Analyst)</option>
                <option value="axel">Axel (Business Strategist)</option>
            </select>
            <input type="text" id="user-input" placeholder="Type your message here..." autofocus>
            <button id="send-button">Send</button>
        </div>
        
        <div class="status-bar">
            <span id="connection-status">Status: Connected</span>
            <span style="float: right;">Agents: <span id="active-agents">4/4</span></span>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const agentSelector = document.getElementById('agent-selector');
            const statusElement = document.getElementById('status');
            const connectionStatus = document.getElementById('connection-status');
            
            // Function to add a message to the chat
            function addMessage(content, isUser = false, agentName = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                
                let header = '';
                if (isUser) {
                    header = `<div class="message-header">You <span class="agent-tag">${agentName || 'User'}</span></div>`;
                } else if (agentName) {
                    header = `<div class="message-header">${agentName} <span class="agent-tag">${getAgentRole(agentName)}</span></div>`;
                }
                
                const contentDiv = document.createElement('div');
                contentDiv.innerHTML = header + content;
                
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = new Date().toLocaleTimeString();
                
                messageDiv.appendChild(contentDiv);
                messageDiv.appendChild(timeDiv);
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Helper function to get agent role
            function getAgentRole(agentId) {
                const roles = {
                    'zane': 'Team Leader',
                    'mira': 'Data Scientist',
                    'chloe': 'Financial Analyst',
                    'axel': 'Business Strategist'
                };
                return roles[agentId] || 'AI';
            }
            
            // Function to send a message
            async function sendMessage() {
                const message = userInput.value.trim();
                const agentId = agentSelector.value;
                
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, true, getAgentRole(agentId));
                userInput.value = '';
                
                try {
                    // Show typing indicator
                    statusElement.textContent = `${getAgentRole(agentId)} is thinking...`;
                    
                    // Send message to the server
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            agent: agentId
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    const data = await response.json();
                    
                    // Add assistant's response to chat
                    if (data.success && data.response) {
                        addMessage(data.response.content, false, agentId);
                    } else {
                        addMessage('I encountered an error processing your request.', false, 'System');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error connecting to the server.', false, 'System');
                } finally {
                    statusElement.textContent = 'Connected';
                }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Initial focus on input
            userInput.focus();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the main chat interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
async def chat():
    """Handle chat messages."""
    global conversation_history
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        agent_id = data.get('agent', 'zane')
        
        if not message:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Process the message with the selected agent
        response = await agent_manager.process_message(message, agent_id)
        
        # Get the agent's response content
        response_content = ""
        if response.get('success', False):
            response_data = response.get('response', {})
            
            # Extract content from different possible response formats
            if isinstance(response_data, dict):
                # Format financial data response
                if all(k in response_data for k in ['period', 'revenue', 'gross_profit_margin']):
                    # Format financial data in a clean, readable way
                    response_content = (
                        f"📊 **Financial Overview - {response_data.get('period')}**\n"
                        f"• Revenue: ${float(response_data['revenue']):,.2f}\n"
                        f"• Gross Profit Margin: {float(response_data['gross_profit_margin']) * 100:.1f}%\n"
                        f"• EBITDA Margin: {float(response_data.get('ebitda_margin', 0)) * 100:.1f}%\n"
                        f"• Net Income: ${float(response_data.get('net_income', 0)):,.2f}\n\n"
                        "📈 **Key Metrics**\n"
                    )
                    
                    # Add key metrics if available
                    if 'key_metrics' in response_data and isinstance(response_data['key_metrics'], dict):
                        metrics = response_data['key_metrics']
                        response_content += "\n".join(
                            f"• {k.replace('_', ' ').title()}: {v:.2f}" 
                            if isinstance(v, (int, float)) 
                            else f"• {k.replace('_', ' ').title()}: {v}" 
                            for k, v in metrics.items()
                        )
                    
                    # Add trends if available
                    if 'trends' in response_data and isinstance(response_data['trends'], list):
                        response_content += "\n\n📊 **Trends**\n• " + "\n• ".join(response_data['trends'])
                        
                # Handle message-based responses
                elif 'message' in response_data:
                    response_content = response_data['message']
                    
                    # Add suggestions if available
                    if 'suggestions' in response_data and isinstance(response_data['suggestions'], list):
                        response_content += "\n\n💡 Suggestions:\n• " + "\n• ".join(response_data['suggestions'])
                
                # Handle content field
                elif 'content' in response_data:
                    content = response_data['content']
                    if isinstance(content, dict):
                        # Format dictionary content as key-value pairs
                        response_content = '\n'.join(
                            f"• {k.replace('_', ' ').title()}: {v}" 
                            for k, v in content.items() 
                            if not k.startswith('_') and v is not None
                        )
                    else:
                        response_content = str(content)
                
                # If no specific content found, use the whole response
                else:
                    response_content = '\n'.join(
                        f"• {k.replace('_', ' ').title()}: {v}" 
                        for k, v in response_data.items() 
                        if not k.startswith('_') and v is not None
                    )
            else:
                response_content = str(response_data)
                
            # If we still don't have content, provide a default response
            if not response_content.strip():
                response_content = "I've processed your request. How can I assist you further?"
        else:
            response_content = response.get('error', 'An error occurred while processing your request.')
        
        # Add to conversation history
        conversation_entry = {
            "role": "user",
            "content": message,
            "agent": agent_id,
            "timestamp": str(datetime.now())
        }
        conversation_history.append(conversation_entry)
        
        # Add agent's response to history
        conversation_history.append({
            "role": "assistant",
            "content": response_content,
            "agent": agent_id,
            "timestamp": str(datetime.now())
        })
        
        # Keep only the last 50 messages
        if len(conversation_history) > 50:
            conversation_history = conversation_history[-50:]
        
        return jsonify({
            "success": True,
            "response": {
                "content": response_content,
                "metadata": response.get('metadata', {})
            }
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all available agents."""
    return jsonify({
        "success": True,
        "agents": [
            {"id": "zane", "name": "Zane", "role": "Team Leader"},
            {"id": "mira", "name": "Mira", "role": "Data Scientist"},
            {"id": "chloe", "name": "Chloe", "role": "Financial Analyst"},
            {"id": "axel", "name": "Axel", "role": "Business Strategist"}
        ]
    })

def main():
    """Main entry point for the application."""
    # Initialize agents
    if not initialize_agents():
        logger.error("Failed to initialize agents. Exiting...")
        return
    
    # Start the web server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Helium AI on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()
