import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotipy with your client credentials
client_id = '649c272abdf4452ab94e1a92bee61715'  # Replace with your client ID
client_secret = 'ce2bc98ce0784baf9c88caa19df12ce1'  # Replace with your client secret

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def fetch_artist(artist_name):
    """Fetch the artist object from Spotify."""
    results = sp.search(q=artist_name, type='artist', limit=1)
    if results['artists']['items']:
        return results['artists']['items'][0]  # Return the first matching artist
    return None

def fetch_all_releases(artist_id, album_type):
    """Fetch all releases of a specific type for the artist."""
    releases = []
    offset = 0
    while True:
        response = sp.artist_albums(artist_id, album_type=album_type, limit=50, offset=offset)
        releases.extend(response['items'])
        if len(response['items']) < 50:  # If less than 50, we're done
            break
        offset += 50  # Move to the next page
    return releases

def count_artist_discography(artist_name):
    """Count the number of releases in an artist's discography (albums, singles, and EPs)."""
    artist = fetch_artist(artist_name)
    if not artist:
        return f"The artist '{artist_name}' was not found."

    # Define the types of albums to fetch
    album_types = ['album', 'single', 'ep', 'compilation']
    all_releases = []

    # Fetch all releases for each album type
    for album_type in album_types:
        releases = fetch_all_releases(artist['id'], album_type)
        all_releases.extend(releases)

    # Collect unique release titles
    release_titles = set(release['name'] for release in all_releases)

    # Prepare the response
    if not release_titles:
        return f"The artist '{artist_name}' has no discography releases."
    
    return f"The artist '{artist_name}' has {len(release_titles)} releases in their discography: {', '.join(release_titles)}"

# Example usage
artist_name = '(G)I-DLE'  # Replace with your desired artist name
print(count_artist_discography(artist_name))
