from rich import print
from spotipy.oauth2 import SpotifyOAuth
import json
import lights
import os
import params
import spotipy
import sys
import time


class FSM:
    def __init__(self, spotipy):
        self.sp = spotipy
        self.playing = False
        self.lights = lights.Lights()
        self.fetch_track()

    def fetch_track(self):
        self.track = self.sp.current_playback()
        if not self.track:
            self.track = {
                "item": {"id": None},
                "is_playing": False,
            }
        if not self.track["item"]:
            self.track["item"] = {"id": None}

    def run(self):
        state = self.stop_playback
        while True:
            state = state()

    def idle(self):
        old_track_id = self.track["item"]["id"]

        self.fetch_track()

        if not self.playing and self.track["is_playing"] and self.track["item"]["id"]:
            self.playing = True
            return self.start_playback

        if self.playing and not self.track["is_playing"]:
            self.playing = False
            return self.stop_playback

        if old_track_id != self.track["item"]["id"]:
            return self.start_playback

        time.sleep(1)
        return self.idle

    def start_playback(self):
        audio = self.sp.audio_features(self.track["item"]["id"])[0]
        track_name = self.track["item"]["name"]
        artists = ", ".join(artist["name"] for artist in self.track["item"]["artists"])
        album = self.track["item"]["album"]["name"]
        print(f"[bold][green]{track_name}[/green] : [blue]{album}[/blue] : [cyan]{artists}[/cyan][/bold]")
        self.lights.set_params(
            params.Params(
                h=audio["valence"],
                s=1.0,
                v=1.0,
                dh=0.05,
                ds=0.2,
                dv=0.2,
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
