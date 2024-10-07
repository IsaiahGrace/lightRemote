from rich import print
from spotipy.oauth2 import SpotifyOAuth
import json
import lights
import math
import os
import params
import spotipy
import sys
import time

none_track = {"item": {"id": None}, "is_playing": False}


class FSM:
    def __init__(self, spotipy):
        self.sp = spotipy
        self.playing = False
        self.lights = lights.Lights()
        self.track = none_track

    def fetch_track(self):
        self.track = self.sp.current_playback()
        if not self.track:
            self.track = none_track
        if not self.track["item"]:
            self.track["item"] = {"id": None}

    def run(self):
        state = self.stop_playback
        while True:
            state = state()

    def idle(self):
        old_playing = self.track["is_playing"]
        old_track_id = self.track["item"]["id"]

        self.fetch_track()

        new = old_track_id != self.track["item"]["id"]
        playing = self.track["is_playing"]
        started = not old_playing and playing
        stopped = old_playing and not playing
        valid = self.track["item"]["id"]

        if new and valid and playing:
            return self.start_playback

        if started and valid:
            return self.start_playback

        if stopped:
            return self.stop_playback

        time.sleep(1)
        return self.idle

    def start_playback(self):
        audio = self.sp.audio_features(self.track["item"]["id"])[0]
        track_name = self.track["item"]["name"]
        artists = ", ".join(artist["name"] for artist in self.track["item"]["artists"])
        album = self.track["item"]["album"]["name"]
        valence = audio["valence"]
        energy = math.pow(audio["energy"], 1)
        danceability = math.pow(audio["danceability"], 1)
        print(f"[bold][green]{track_name}[/green] : [blue]{album}[/blue] : [cyan]{artists}[/cyan][/bold]")
        print(f"valence: {audio['valence']:0.4f} energy: {energy:0.4f} danceability: {danceability:0.4f}")
        self.lights.set_params(
            params.Params(
                h=audio["valence"],
                s=energy,
                v=danceability,
                dh=0.05,
                ds=0.0,
                dv=0.0,
                t=0.5,
            )
        )
        return self.idle

    def stop_playback(self):
        print("stop playback")
        # We set the hue tolerance to 1 so that the pixels retain their hue as they turn off.
        self.lights.set_params(params.Params(dh=1.0))
        return self.idle


def main(args):
    with open(os.path.expanduser("~/.spotipy_secrets.json")) as f:
        for env, val in json.load(f).items():
            os.environ[env] = val

    scope = "user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    fsm = FSM(sp)
    try:
        fsm.run()
    except KeyboardInterrupt:
        raise
    except:
        print(fsm.track)
        raise


if __name__ == "__main__":
    main(sys.argv)
