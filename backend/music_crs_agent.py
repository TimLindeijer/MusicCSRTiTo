from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.dialogue_act import DialogueAct
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.agent import Agent
from dialoguekit.participant.participant import DialogueParticipant
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
import logging

logging.basicConfig(level=logging.INFO)  # Set the level to INFO
logger = logging.getLogger(__name__)  # Create a logger

class MusicCRSAgent(Agent):
    def __init__(self, id: str):
        super().__init__(id)
        self.playlist = []

        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            "Hello! I'm MusicCRS. You can add, remove, view, or clear songs from your playlist. What would you like to do?",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye!",
            dialogue_acts=[DialogueAct(intent=self.stop_intent)],
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def receive_utterance(self, utterance: Utterance) -> None:
        """Handles user commands to manage the playlist."""
        user_input = utterance.text.lower()
        
        if "add" in user_input:
            song = user_input.split("add")[-1].strip()
            search_results = self.sp.search(q=song, type='track', limit=1)
            if search_results['tracks']['items']:
                track = search_results['tracks']['items'][0]
                cleaned_title = search_results['tracks']['items'][0]['name'].lower()  # Convert to lowercase
                self.playlist.append(cleaned_title)
                response = f"Added '{track['name']}' by {track['artists'][0]['name']} to your playlist."
            else:
                response = "Did not find the song on Spotify."
        
        elif "remove" in user_input:
            song = user_input.split("remove")[-1].strip() 
            if song in self.playlist:
                self.playlist.remove(song)
                response = f"Removed '{song}' from your playlist."
            else:
                response = f"Song '{song}' does not exist in your playlist."


        elif "list" in user_input:
            response = "'" + "' | '".join(self.playlist) + "'"

        elif "when was album" in user_input:
            # Extract the relevant part of the user input
            album_info = user_input.split("when was album")[-1].strip()
            
            # Split to get album name and artist name
            parts = album_info.split("by")
            if len(parts) == 2:
                album_name = parts[0].strip()
                artist_name = parts[1].strip()  # Capture the artist name
            else:
                album_name = album_info  # Fallback if "by" is not provided
                artist_name = None  # No artist specified

            # Get the release year, potentially passing the artist name
            year = self.get_album_release_year(album_name, artist_name)  
            response = year


        elif "how many albums has artist" in user_input:
            artist_name = user_input.split("how many albums has artist")[-1].strip()
            response = self.count_artist_discography(artist_name)  

        elif "which album features song" in user_input:
            song_info = user_input.split("which album features song")[-1].strip()
            if "by" in song_info:
                song_name, artist_name = song_info.split("by", 1)
                song_name = song_name.strip()
                artist_name = artist_name.strip()
            else:
                song_name = song_info
                artist_name = None  # No artist provided

            album_info = self.find_album_for_song(song_name, artist_name)  
            response = album_info
        else:
            response = "Message not understood."
        
        response = AnnotatedUtterance(
            "(MusicCRS) " + response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)
    
    def get_album_release_year(self, album_name, artist_name=None):
        """Get the release year of an album from Discogs."""
        # Search with or without the artist name
        if artist_name:
            search_query = f"{album_name} by {artist_name}"  # Combine album and artist for search
        else:
            search_query = album_name

        results = self.sp.search(search_query, type='album')  # Adjusting to use Spotipy
        if results['albums']['items']:
            release = results['albums']['items'][0]  # Get the first result
            return f"Release year for the album '{release['name']}' is {release['release_date'][:4]}"
        
        return "Release year not found."


    def fetch_artist(self, artist_name):
        """Fetch the artist object from Spotify."""
        results = self.sp.search(q=artist_name, type='artist', limit=1)
        if results['artists']['items']:
            return results['artists']['items'][0]  # Return the first matching artist
        return None

    def fetch_all_releases(self, artist_id, album_type):
        """Fetch all releases of a specific type for the artist."""
        releases = []
        offset = 0
        while True:
            response = self.sp.artist_albums(artist_id, album_type=album_type, limit=50, offset=offset)
            releases.extend(response['items'])
            if len(response['items']) < 50:  # If less than 50, we're done
                break
            offset += 50  # Move to the next page
        return releases

    def count_artist_discography(self, artist_name):
        """Count the number of releases in an artist's discography (albums, singles, and EPs)."""
        artist = self.fetch_artist(artist_name)
        if not artist:
            return f"The artist '{artist_name}' was not found."

        # Define the types of albums to fetch
        album_types = ['album', 'single', 'ep', 'compilation']
        all_releases = []

        # Fetch all releases for each album type
        for album_type in album_types:
            releases = self.fetch_all_releases(artist['id'], album_type)
            all_releases.extend(releases)

        # Collect unique release titles
        release_titles = set(release['name'] for release in all_releases)

        # Prepare the response
        if not release_titles:
            return f"The artist '{artist_name}' has no discography releases."
        
        return f"The artist '{artist_name}' has {len(release_titles)} releases in their discography: {', '.join(release_titles)}"

    def find_album_for_song(self, song_name, artist_name=None):
        """Find the album that features a song, optionally filtering by artist."""
        query = f"{song_name}"
        if artist_name:
            query += f" artist:{artist_name}"  # Include artist in the search if provided

        results = self.sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            album_name = track['album']['name']
            album_artist = track['album']['artists'][0]['name']  # Get the album artist
            return f"The song '{song_name}' is featured in the album '{album_name}' by {album_artist}."
        return "Song not found."
