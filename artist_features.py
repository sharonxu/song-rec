import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials

def get_artist_features(artists, sp):

    count = 0
    rows_list = []
    rows_list_genre = []

    for index, row in artists.iterrows():

        result = sp.artist(row['uri'])
        rows_list.append(
            {'artist_uri': row['uri'],
             'artist': row['artist'],
             'followers': result['followers']['total'],
             'popularity': result['popularity']
            })

        for genre in result['genres']:
            rows_list_genre.append(
                {'artist_uri': row['uri'],
                 'artist': row['artist'],
                 'genre': genre
                })

        if (count % 1000 == 0):
            print(count)
        count += 1

    artist_features = pd.DataFrame(rows_list)
    artist_features_genre = pd.DataFrame(rows_list_genre)

    return [artist_features, artist_features_genre]


def main():

    import argparse

    default_output_dir = ''
    default_output_path = 'artist_features.csv'
    default_output_path_genre = 'artist_features_genre.csv'
    parser = argparse.ArgumentParser("Request artist features (genres, popularity, etc) from Spotify API.")
    parser.add_argument("artist_csv", help="path to comma separated data with columns artist,uri. Expects a header row.")
    parser.add_argument("client_id", help="client id for Spotify API")
    parser.add_argument("client_secret", help="client secret for Spotify API")
    parser.add_argument("--output_dir", help="directory for output files. Default is " + default_output_dir)
    parser.add_argument("--output_path", help="where to save artist features. Default is " + default_output_path)
    parser.add_argument("--output_path_genre", help="where to save artist features for genre. Default is " + default_output_path_genre)
    args = parser.parse_args()

    client_credentials_manager = SpotifyClientCredentials(client_id=args.client_id, 
                                                          client_secret=args.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    artists = pd.read_csv(args.artist_csv)

    print("Getting artist features. "  + str(len(artists)) + " artists total.")
    artist_features, artist_features_genre = get_artist_features(artists, sp)

    output_dir = args.output_dir  + "/"  if args.output_dir else  default_output_dir
    output_path = args.output_path or default_output_path
    output_path_genre = args.output_path_genre or default_output_path_genre

    artist_features.to_csv(output_dir + output_path, index=False)
    artist_features_genre.to_csv(output_dir + output_path_genre, index=False)

if __name__ == "__main__":
    main()