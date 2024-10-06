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
        self.track = self.sp.current_playback()
        self.lights = lights.Lights(400)

    def run(self):
        state = self.stop_playback
        while True:
            state = state()

    def idle(self):
        # print("fsm idle")

        old_track_id = self.track["item"]["id"]

        self.track = self.sp.current_playback()

        if not self.playing and self.track["is_playing"]:
            self.playing = True
            return self.start_playback

        if self.playing and not self.track["is_playing"]:
            self.playing = False
            return self.stop_playback

        if old_track_id != self.track["item"]["id"]:
            return self.start_playback

        # progress = self.track["progress_ms"] / self.track["item"]["duration_ms"]
        # remaining_ms = self.track["item"]["duration_ms"] - self.track["progress_ms"]
        # print(f"{progress:.4f} {remaining_ms}")

        time.sleep(1)
        return self.idle

    def start_playback(self):
        # print("fsm start playback")
        audio = self.sp.audio_features(self.track["item"]["id"])[0]
        print(f"[bold green]{self.track['item']['name']}[/bold green]")
        self.lights.set_params(
            params.Params(
                h=audio["valence"],
                s=1.0,
                v=1.0,
                dh=0.2,
                ds=0.2,
                dv=0.2,
            )
        )
        return self.idle

    def stop_playback(self):
        print("stop playback")
        self.lights.set_params(params.Params())
        return self.idle


def main(args):
    with open(os.path.expanduser("~/.spotipy_secrets.json")) as f:
        for env, val in json.load(f).items():
            os.environ[env] = val

    scope = "user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    fsm = FSM(sp)
    fsm.run()


if __name__ == "__main__":
    main(sys.argv)
