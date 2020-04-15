import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

USERNAME = 'Isaiah Robert Grace'
USER_ID = '12149734788' # Isaiah Robert Grace
CLIENT_ID = '9b6ff36aec5442088e9043520640f941'
CLIENT_SECRET = 'e5baf7417df54c979cb2be7e67a337f2'
REDIRECT_URI = 'http://localhost:8080'
PORT_NUMBER = 8080
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = sp.user_playlists(USERNAME)
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
