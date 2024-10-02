from dialoguekit.platforms import FlaskSocketPlatform
from sample_agents.parrot_agent import ParrotAgent
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for all origins

@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is in the templates folder

@socketio.on('chat message')
def handle_message(message):
    print(f"Message received: {message}")
    response = f"Server response: You said '{message}'"
    print(f"Sending response: {response}")
    socketio.emit('chat response', response)  # Send the response back to the frontend

if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000)
    platform = FlaskSocketPlatform(ParrotAgent)
    platform.start()

