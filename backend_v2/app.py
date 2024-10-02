from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Socket.IO server running"

# Log the connection events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Handle messages from the frontend and send the same message back
@socketio.on('message')
def handle_message(data):
    print(f"Message received: {data}")  # Logs the message from the frontend
    emit('message', data)  # Sends the same message back to the frontend

if __name__ == '__main__':
    socketio.run(app, debug=True)
