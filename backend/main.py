from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Initialize the FastAPI app
app = FastAPI()

# Create a Socket.IO server with CORS settings
sio = socketio.AsyncServer(
    cors_allowed_origins=["http://localhost:3000"],  # Allow connections from this origin
    async_mode="asgi"  # Use ASGI for compatibility with FastAPI
)

# Mount the Socket.IO app at the specified path
app.mount("/socket.io", socketio.ASGIApp(sio))

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow the frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Example event handler for a connection
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

# Example event handler for messages
@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    # Echo the message back to the client
    await sio.send(sid, f"Echo: {data}")

# Example event handler for disconnection
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# A sample HTTP endpoint for testing
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Socket.IO server!"}

# To run the FastAPI app, use the command:
# uvicorn main:app --host 127.0.0.1 --port 5000 --reload
