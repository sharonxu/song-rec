
import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials


def get_albums(artists, sp):

    print("Getting album URIs. "  + str(len(artists)) + " artists total.")
    count = 0
    rows_list = []
    for index, row in artists.iterrows():

        artist = row['artist']
        artist_uri = row['uri']
        sp_albums = sp.artist_albums(artist_uri, album_type='album')

        for i in range(len(sp_albums['items'])):
            rows_list.append(
            {'artist_uri': artist_uri, 'artist': artist, 
             'album_name': sp_albums['items'][i]['name'],
             'album_uri': sp_albums['items'][i]['uri']})
        if (count % 5000 == 0):
            print(count)
        count += 1
            
    albums = pd.DataFrame(rows_list)
    return albums

def get_songs(albums, sp):

    print("Getting song IDs. " + str(len(albums)) + " albums total.")
    count = 0
    rows_list = []
    for index, row in albums.iterrows():
        
        album = row['album_uri']
        tracks = sp.album_tracks(album)
        
        for i in range(len(tracks['items'])):
            rows_list.append({
                'artist_uri': row['artist_uri'],
                'artist': row['artist'],
                'album_name': row['album_name'],
                'album_uri': album,
                'track_id': tracks['items'][i]['id'],
                'track_name': tracks['items'][i]['name']
            })
            
        if (count % 5000 == 0):
            print(count)
        count += 1
                
    songs = pd.DataFrame(rows_list)
    return songs

def get_audio_features(songs, sp):

    print("Getting audio features. " + str(len(songs)) + " songs total.")

    n = 100
    song_list = [songs.track_id.tolist()[i * n:(i + 1) * n] for i in range((len(songs.track_id) + n - 1) // n )] 

    count = 0
    audio_features = []
    for l in song_list:
        audio_features.extend(sp.audio_features(l))
        if (count % 100 == 0):
            print(count*100)
        count += 1    

    audio_features = pd.DataFrame(audio_features)
    return audio_features[['id', 'acousticness', 'danceability', 'energy', 'instrumentalness',
    'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']]


def main():

    import argparse

    default_output_dir = ''
    default_output_path_albums = 'albums.csv.gz'
    default_output_path_songs = 'songs.csv.gz'
    default_output_path_audio_features = 'audio_features.csv.gz'
    parser = argparse.ArgumentParser("Request album URIs, song IDs, and audio features from Spotify API.")
    parser.add_argument("artist_csv", help="path to comma separated data with columns artist,uri. Expects a header row.")
    parser.add_argument("client_id", help="client id for Spotify API")
    parser.add_argument("client_secret", help="client secret for Spotify API")
    parser.add_argument("--output_dir", help="directory for output files. Default is " + default_output_dir)
    parser.add_argument("--output_path_albums", help="where to save song data (gzip). Default is " + default_output_path_albums)
    parser.add_argument("--output_path_songs", help="where to save song data (gzip). Default is " + default_output_path_songs)
    parser.add_argument("--output_path_audio_features", help="where to save audio feature data (gzip). Default is " + default_output_path_audio_features)
    args = parser.parse_args()

    client_credentials_manager = SpotifyClientCredentials(client_id=args.client_id, 
                                                          client_secret=args.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    artists = pd.read_csv(args.artist_csv)

    output_dir = args.output_dir  + "/"  if args.output_dir else  default_output_dir
    output_path_albums = args.output_path_albums or default_output_path_albums
    output_path_songs = args.output_path_songs or default_output_path_songs
    output_path_audio_features = args.output_path_audio_features or default_output_path_audio_features

    albums = get_albums(artists, sp)
    albums.to_csv(output_dir + output_path_albums, index=False, compression='gzip')

    songs = get_songs(albums, sp)
    songs.to_csv(output_dir + output_path_songs, index=False, compression='gzip')

    audio_features = get_audio_features(songs, sp)
    audio_features.to_csv(output_dir + output_path_audio_features, index=False, compression='gzip')

if __name__ == "__main__":
    main()

