"""
A simple web interface for Helium AI using Flask (lighter than FastAPI for Windows).
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.agents import Zane, Mira, Chloe, Axel
except ImportError as e:
    print(f"Error importing agents: {e}")
    print("Make sure you're running from the project root directory and have installed the requirements.")
    sys.exit(1)

app = Flask(__name__)

# Initialize agents
try:
    zane = Zane()
    mira = Mira()
    chloe = Chloe()
    axel = Axel()
    
    # Set up the team
    zane.add_team_member(mira)
    zane.add_team_member(chloe)
    zane.add_team_member(axel)
    
except Exception as e:
    print(f"Error initializing agents: {e}")
    sys.exit(1)

# Store conversation history
conversation_history = []

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Helium AI - Simple Web Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: #4a6fa5;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
        }
        .chat-messages {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }
        .assistant-message {
            background: #f1f1f1;
            margin-right: auto;
            border-bottom-left-radius: 0;
        }
        .message-sender {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .message-time {
            font-size: 0.7em;
            color: #666;
            text-align: right;
            margin-top: 5px;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background: #f9f9f9;
            border-top: 1px solid #eee;
        }
        #user-input {
            flex-grow: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        #send-button {
            background: #4a6fa5;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 0 20px;
            margin-left: 10px;
            cursor: pointer;
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
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            Helium AI Research Assistant
        </div>
        <div id="chat-messages" class="chat-messages">
            <div id="typing-indicator" class="typing-indicator">
                Helium AI is thinking...
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type your message here..." autofocus>
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const typingIndicator = document.getElementById('typing-indicator');
            
            // Function to add a message to the chat
            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                
                const senderDiv = document.createElement('div');
                senderDiv.className = 'message-sender';
                senderDiv.textContent = isUser ? 'You' : 'Helium AI';
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.textContent = content;
                
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = new Date().toLocaleTimeString();
                
                messageDiv.appendChild(senderDiv);
                messageDiv.appendChild(contentDiv);
                messageDiv.appendChild(timeDiv);
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Function to send a message
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, true);
                userInput.value = '';
                
                // Show typing indicator
                typingIndicator.style.display = 'block';
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    const data = await response.json();
                    
                    // Add assistant's response to chat
                    if (data.success && data.response) {
                        addMessage(data.response);
                    } else {
                        addMessage('I encountered an error processing your request.');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error connecting to the server.');
                } finally {
                    // Hide typing indicator
                    typingIndicator.style.display = 'none';
                }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Load any existing conversation history
            async function loadHistory() {
                try {
                    const response = await fetch('/history');
                    const data = await response.json();
                    
                    if (data.history && Array.isArray(data.history)) {
                        data.history.forEach(item => {
                            if (item.role === 'user') {
                                addMessage(item.content, true);
                            } else if (item.role === 'assistant') {
                                addMessage(item.content);
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error loading history:', error);
                }
            }
            
            loadHistory();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the chat interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
async def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Process the message with Zane
        response = await zane.process(message)
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": str(response.content)})
        
        # Keep only the last 20 messages
        global conversation_history
        conversation_history = conversation_history[-20:]
        
        return jsonify({
            "success": True,
            "response": str(response.content)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/history')
def history():
    """Get the conversation history."""
    return jsonify({"history": conversation_history})

def start_server(host='0.0.0.0', port=5000):
    """Start the Flask server."""
    print(f"\n🚀 Starting Helium AI server at http://{host}:{port}")
    print("Press Ctrl+C to stop\n")
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    start_server()
