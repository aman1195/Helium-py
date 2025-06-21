import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import json
import asyncio

# Set Windows event loop policy if on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import agents
try:
    from agents import Zane, Mira, Chloe, Axel
except ImportError as e:
    print(f"Error importing agents: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(title="Helium AI", description="Multi-agent AI Research Assistant")

# Set up templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Initialize agents
zane = Zane()
mira = Mira()
chloe = Chloe()
axel = Axel()

# Set up the team
zane.add_team_member(mira)
zane.add_team_member(chloe)
zane.add_team_member(axel)

# Store conversation history as a global variable
conversation_history = []

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    print("Helium AI Web Interface is starting up...")
    # Any initialization code can go here

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request, "history": conversation_history})

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """Handle chat messages and return agent responses."""
    try:
        # Process the message with Zane (who will delegate as needed)
        result = await zane.process(message)
        
        # Format the response
        response = {
            "success": result.success,
            "message": result.content,
            "agent": "Zane (Team Leader)",
            "timestamp": str(utcnow())
        }
        
        # Add to conversation history
        conversation_history.append({
            "type": "user",
            "content": message,
            "timestamp": str(utcnow())
        })
        conversation_history.append({
            "type": "assistant",
            "content": response,
            "timestamp": str(utcnow())
        })
        
        # Keep only the last 20 messages
        global conversation_history
        conversation_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    """Get the conversation history."""
    return {"history": conversation_history}

# Utility function to get current UTC time
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

# Create necessary directories
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

def create_web_interface():
    """Create the web interface files if they don't exist."""
    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Create CSS file
    css_path = os.path.join(static_dir, "style.css")
    if not os.path.exists(css_path):
        with open(css_path, "w") as f:
            f.write("""
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
            """)
    
    # Create JavaScript file
    js_path = os.path.join(static_dir, "script.js")
    if not os.path.exists(js_path):
        with open(js_path, "w") as f:
            f.write("""
            document.addEventListener('DOMContentLoaded', function() {
                const chatMessages = document.getElementById('chat-messages');
                const userInput = document.getElementById('user-input');
                const sendButton = document.getElementById('send-button');
                const typingIndicator = document.getElementById('typing-indicator');
                
                // Auto-scroll to bottom of chat
                function scrollToBottom() {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                // Add a message to the chat
                function addMessage(content, isUser = false) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                    
                    const senderDiv = document.createElement('div');
                    senderDiv.className = 'message-sender';
                    senderDiv.textContent = isUser ? 'You' : 'Helium AI';
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    
                    // Check if content is an object (from the API response)
                    if (typeof content === 'object') {
                        contentDiv.textContent = JSON.stringify(content, null, 2);
                    } else {
                        contentDiv.textContent = content;
                    }
                    
                    const timeDiv = document.createElement('div');
                    timeDiv.className = 'message-time';
                    timeDiv.textContent = new Date().toLocaleTimeString();
                    
                    messageDiv.appendChild(senderDiv);
                    messageDiv.appendChild(contentDiv);
                    messageDiv.appendChild(timeDiv);
                    
                    chatMessages.appendChild(messageDiv);
                    scrollToBottom();
                }
                
                // Send message to the server
                async function sendMessage() {
                    const message = userInput.value.trim();
                    if (!message) return;
                    
                    // Add user message to chat
                    addMessage(message, true);
                    userInput.value = '';
                    
                    // Show typing indicator
                    typingIndicator.style.display = 'block';
                    scrollToBottom();
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: `message=${encodeURIComponent(message)}`
                        });
                        
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        
                        const data = await response.json();
                        
                        // Add assistant's response to chat
                        if (data.success && data.message) {
                            addMessage(data.message);
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
                        const response = await fetch('/api/history');
                        const data = await response.json();
                        
                        if (data.history && Array.isArray(data.history)) {
                            data.history.forEach(item => {
                                if (item.type === 'user') {
                                    addMessage(item.content, true);
                                } else if (item.type === 'assistant') {
                                    addMessage(item.content.content);
                                }
                            });
                        }
                    } catch (error) {
                        console.error('Error loading history:', error);
                    }
                }
                
                loadHistory();
            });
            """)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create HTML template
    html_path = os.path.join(templates_dir, "index.html")
    if not os.path.exists(html_path):
        with open(html_path, "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Helium AI - Multi-agent Research Assistant</title>
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div class="chat-container">
                    <div class="chat-header">
                        Helium AI Research Assistant
                    </div>
                    <div id="chat-messages" class="chat-messages">
                        <div id="typing-indicator" class="typing-indicator">
                            Helium AI is typing...
                        </div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="user-input" placeholder="Type your message here..." autofocus>
                        <button id="send-button">Send</button>
                    </div>
                </div>
                <script src="/static/script.js"></script>
            </body>
            </html>
            """)

# Create the web interface files
create_web_interface()

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server with uvicorn."""
    config = uvicorn.Config(
        "web_app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        print(f"\n🚀 Starting Helium AI server at http://{host}:{port}")
        print("Press Ctrl+C to stop\n")
        server.run()
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
