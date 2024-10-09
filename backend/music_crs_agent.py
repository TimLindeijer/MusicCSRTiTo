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
        self.used_features = set()  # Track used features

        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            """Hello! I'm MusicCRS.
               You can add, remove, or view your playlist. You can also see when an album was released, an artist's discography, or which album a song is from.
               If you wonder how to perform any of these functions, type: 'help'.
               What would you like to do?""",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        """Sends a goodbye message."""
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye!",
            dialogue_acts=[DialogueAct(intent=self.stop_intent)],
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def receive_utterance(self, utterance: Utterance) -> None:
        """Handles user commands to manage the playlist."""
        user_input = utterance.text.lower()
        response = None

        # Feature detection logic
        if "add" in user_input:
            self.used_features.add("add")
            song = user_input.split("add")[-1].strip()
            response = self.handle_add_song(song)

        elif "remove" in user_input:
            self.used_features.add("remove")
            song = user_input.split("remove")[-1].strip()
            response = self.handle_remove_song(song)

        elif "list" in user_input:
            self.used_features.add("list")
            response = self.handle_list_playlist()

        elif "when was album" in user_input:
            self.used_features.add("album_release")
            album_info = user_input.split("when was album")[-1].strip()
            response = self.handle_album_release_year(album_info)

        elif "how many albums has artist" in user_input:
            self.used_features.add("artist_discography")
            artist_name = user_input.split("how many albums has artist")[-1].strip()
            response = self.handle_artist_discography(artist_name)

        elif "which album features song" in user_input:
            self.used_features.add("album_for_song")
            song_info = user_input.split("which album features song")[-1].strip()
            response = self.handle_album_for_song(song_info)
        
        elif "how many tracks does album" in user_input:
            album_info = user_input.split("how many tracks does album")[-1].strip()

            # Check if the user provided an artist name
            if "by" in album_info:
                album_name, artist_name = album_info.split("by", 1)
                album_name = album_name.strip()
                artist_name = artist_name.strip()
            else:
                album_name = album_info
                artist_name = None  # No artist specified

            track_count = self.get_album_track_count(album_name, artist_name)
            response = track_count


        elif "what are the top 3 tracks of artist" in user_input:
            artist_name = user_input.split("what are the top 3 tracks of artist")[-1].strip()
            top_tracks = self.get_top_tracks(artist_name, 3)
            response = top_tracks

        elif "how many followers does artist" in user_input:
            artist_name = user_input.split("how many followers does artist")[-1].strip()
            followers = self.get_artist_followers(artist_name)
            response = followers

        elif "help" in user_input:
            self.used_features.add("help")
            response = self.handle_help()

        else:
            response = "Message not understood."

        # Suggest additional features dynamically
        response += self.suggest_unused_features()

        response = AnnotatedUtterance(
            "(MusicCRS) " + response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)

    def handle_add_song(self, song: str) -> str:
        search_results = self.sp.search(q=song, type='track', limit=1)
        if search_results['tracks']['items']:
            track = search_results['tracks']['items'][0]
            cleaned_title = track['name'].lower()
            self.playlist.append(cleaned_title)
            return f"Added '{track['name']}' by {track['artists'][0]['name']} to your playlist.\n" + self.suggest_song_questions(cleaned_title)
        return "Did not find the song on Spotify."

    def handle_remove_song(self, song: str) -> str:
        if song in self.playlist:
            self.playlist.remove(song)
            return f"Removed '{song}' from your playlist."
        return f"Song '{song}' does not exist in your playlist."

    def handle_list_playlist(self) -> str:
        return "'" + "' | '".join(self.playlist) + "'"

    def handle_album_release_year(self, album_info: str) -> str:
        parts = album_info.split("by")
        album_name = parts[0].strip()
        artist_name = parts[1].strip() if len(parts) == 2 else None
        return self.get_album_release_year(album_name, artist_name)

    def handle_artist_discography(self, artist_name: str) -> str:
        return self.count_artist_discography(artist_name)

    def handle_album_for_song(self, song_info: str) -> str:
        parts = song_info.split("by")
        song_name = parts[0].strip()
        artist_name = parts[1].strip() if len(parts) == 2 else None
        return self.find_album_for_song(song_name, artist_name)

    def handle_help(self) -> str:
        return """
            These are the chat manuals:
            To add a song to the playlist type: 'add <song>'.
            To remove a song from the playlist type: 'remove <song>'.
            To view your playlist type: 'list'.
            To find when an album was released type: 'when was album <album> (optional) by <artist>'.
            To count the albums of an artist type: 'how many albums has artist <artist>'.
            To find which album a song is featured in type: 'which album features song <song> (optional) by <artist>'.
            To count tracks in an album type: 'how many tracks does album <album> (optional) by <artist>'.
            To find the top tracks of an artist type: 'what are the top 3 tracks of artist <artist>'.
            To find how many followers an artist has type: 'how many followers does artist <artist>'.
        """

    def suggest_song_questions(self, song_name: str) -> str:
        """Suggest questions the user can ask about a song they added."""
        return f"Would you like to know which album '{song_name}' is from or the artist's discography?"

    def suggest_unused_features(self) -> str:
        """Suggest unused features in a non-intrusive manner."""
        all_features = {
            "add": "You can add songs to your playlist by typing 'add <song>'.",
            "remove": "You can remove songs by typing 'remove <song>'.",
            "list": "You can view your playlist by typing 'list'.",
            "album_release": "To find when an album was released, type 'when was album <album> by <artist>'.",
            "artist_discography": "To count the albums of an artist, type 'how many albums has artist <artist>'.",
            "album_for_song": "To find which album features a song, type 'which album features song <song> by <artist>'."
        }

        unused_features = set(all_features.keys()) - self.used_features
        if unused_features:
            return "\nYou might also like to try: " + " | ".join([all_features[feature] for feature in unused_features])

        return ""

    
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

    def get_album_track_count(self, album_name, artist_name=None):
        """Get the number of tracks in an album, optionally filtering by artist."""
        query = f"album:{album_name}"
        if artist_name:
            query += f" artist:{artist_name}"

        results = self.sp.search(q=query, type='album', limit=1)
        
        if results['albums']['items']:
            album = results['albums']['items'][0]
            total_tracks = album['total_tracks']
            album_title = album['name']
            artist = album['artists'][0]['name']  # Get the artist of the album
            return f"The album '{album_title}' by {artist} has {total_tracks} tracks."
        
        return "Album not found."


    def get_top_tracks(self, artist_name, limit=3):
        """Get the top tracks of an artist."""
        artist = self.fetch_artist(artist_name)
        if artist:
            top_tracks = self.sp.artist_top_tracks(artist['id'], country='US')
            track_list = [track['name'] for track in top_tracks['tracks'][:limit]]
            return f"Top {limit} tracks of {artist_name}: {', '.join(track_list)}."
        return f"Artist '{artist_name}' not found."

    def get_artist_followers(self, artist_name):
        """Get the number of followers of an artist."""
        artist = self.fetch_artist(artist_name)
        if artist:
            followers = artist['followers']['total']
            return f"Artist '{artist_name}' has {followers} followers."
        return f"Artist '{artist_name}' not found."
