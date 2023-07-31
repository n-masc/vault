import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import redirect

SPOTIPY_CLIENT_ID = "a3e3c739eb0a4ba0a4810d935e0be8ef"
SPOTIPY_CLIENT_SECRET = "0480cde8655a4a469186b011b0e734ef"
SPOTIPY_REDIRECT_URI = 'https://localhost:8888/callback'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

title = 'hollow knight'


def search_soundtrack(game_name):
    # game_name = title
    results = sp.search(q=game_name, type='album')

    album = results['albums']['items'][0]
    album_id = album['id']
    spotify_uri = f'spotify:album{album_id}'

    spotify_url = f'https://open.spotify.com/album/{album_id}'
    print(spotify_url)
    return redirect(spotify_url)

search_soundtrack(title)
