"""
A minimal web interface for Helium AI using Flask.
"""
from flask import Flask, render_template_string, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Global variable for conversation history
conversation_history = []

# Mock agent class for demonstration
class MockAgent:
    def process(self, task):
        """Process a task and return a response."""
        responses = {
            "hello": "Hello! I'm Helium AI. How can I help you today?",
            "hi": "Hi there! I'm Helium AI. What would you like to know?",
            "help": "I can help you with various tasks. Try asking me something!",
            "default": "I'm a simple AI assistant. In a full version, I would process your request with advanced AI capabilities."
        }
        
        task_lower = task.lower()
        for key in responses:
            if key in task_lower:
                return {"content": responses[key], "success": True}
        return {"content": responses["default"], "success": True}

# Initialize a mock agent
agent = MockAgent()

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Helium AI - Minimal Web Interface</title>
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
            Helium AI - Minimal Demo
        </div>
        <div id="chat-messages" class="chat-messages">
            <div class="message assistant-message">
                <div>Hello! I'm a minimal version of Helium AI. Try saying 'hello' or 'help'.</div>
                <div class="message-time">Just now</div>
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
            
            // Function to add a message to the chat
            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.textContent = content;
                
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = new Date().toLocaleTimeString();
                
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
                }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
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
def chat():
    """Handle chat messages."""
    global conversation_history  # Declare as global at the start of the function
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Process the message with the mock agent
        response = agent.process(message)
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": message, "timestamp": str(datetime.now())})
        conversation_history.append({"role": "assistant", "content": response["content"], "timestamp": str(datetime.now())})
        
        # Keep only the last 20 messages
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return jsonify({
            "success": True,
            "response": response["content"]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("\n🚀 Starting Helium AI (Minimal Version) at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
