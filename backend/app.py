# socket_platform.py
from dialoguekit.platforms import FlaskSocketPlatform
from music_crs_agent import MusicCRSAgent  # Import the agent class

# Initialize the platform with the MusicCRS agent
platform = FlaskSocketPlatform(MusicCRSAgent)
platform.start()  # This will start your Flask app and listen for socket connections
