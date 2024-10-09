import h5py
import pandas as pd
import sqlite3

# Load the HDF5 file
file_path = "C:/Users/tmysi/Documents/DAT640/MusicCSRTiTo/data/msd_summary_file.h5"
file = h5py.File(file_path, 'r')

# Load datasets into pandas DataFrames
analysis_df = pd.DataFrame(file['analysis/songs'][:])
metadata_df = pd.DataFrame(file['metadata/songs'][:])
musicbrainz_df = pd.DataFrame(file['musicbrainz/songs'][:])

# Reset the index of each DataFrame
metadata_df.reset_index(drop=True, inplace=True)
analysis_df.reset_index(drop=True, inplace=True)
musicbrainz_df.reset_index(drop=True, inplace=True)

# Combine the datasets horizontally
combined_df = pd.concat([metadata_df, analysis_df, musicbrainz_df], axis=1)

# Define the subset of columns you want to keep
desired_columns = [
    'song_id',             # From metadata
    'title',               # From metadata
    'artist_name',         # From metadata
    'release',             # From metadata
    'genre',               # From metadata
    'danceability',        # From analysis
    'energy',              # From analysis
    'loudness',            # From analysis
    'tempo',               # From analysis
    'key',                 # From analysis
    'year'                 # From musicbrainz
]

# Create a new DataFrame with only the desired columns
combined_df = combined_df[desired_columns]

text_columns = ['song_id', 'title', 'artist_name', 'release', 'genre']  # Adjust as necessary

for column in text_columns:
    combined_df[column] = combined_df[column].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

# Preview the filtered DataFrame
print(combined_df.head())

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('music_data.db')  # Creates a new database file

# Create a new table
conn.execute('''
CREATE TABLE IF NOT EXISTS songs (
    song_id TEXT,
    title TEXT,
    artist_name TEXT,
    release TEXT,
    genre TEXT,
    danceability REAL,
    energy REAL,
    loudness REAL,
    tempo REAL,
    key REAL,
    year INTEGER
);
''')

# Insert data into the table
combined_df.to_sql('songs', conn, if_exists='append', index=False)

# Commit the changes and close the connection
conn.commit()
conn.close()


# Example of querying the SQLite database
conn = sqlite3.connect('music_data.db')
query_result = pd.read_sql_query("SELECT * FROM songs LIMIT 10;", conn)
print(query_result)
conn.close()
