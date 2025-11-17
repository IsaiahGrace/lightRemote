from rich import print
from spotipy.oauth2 import SpotifyOAuth
import functools
import json
import lights
import math
import os
import params
import spotipy
import sys
import time
import zlib

none_track = {"item": {"id": None}, "is_playing": False}


class FSM:
    def __init__(self, spotipy, backend):
        self.sp = spotipy
        self.playing = False
        self.lights = lights.Lights(backend)
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
        old_valid = self.track["item"]["id"]

        self.fetch_track()

        new = old_track_id != self.track["item"]["id"]
        playing = self.track["is_playing"]
        started = not old_playing and playing
        stopped = old_valid and old_playing and not playing
        valid = self.track["item"]["id"]
        invalidated = old_valid and not valid

        if new and valid and playing:
            return self.start_playback

        if started and valid:
            return self.start_playback

        if stopped:
            return self.stop_playback

        if invalidated:
            return self.stop_playback

        time.sleep(1)
        return self.idle

    def start_playback(self):
        track_name = self.track["item"]["name"]
        artist_names = ", ".join(artist["name"] for artist in self.track["item"]["artists"])
        album = self.track["item"]["album"]["name"]

        artists = [self.sp.artist(a["id"]) for a in self.track["item"]["artists"]]
        genres = set()
        for a in artists:
            for g in a["genres"]:
                genres.add(g)
            if not a["genres"]:
                genres.add(a["name"])

        genre_hash = functools.reduce(
            lambda a, b: a ^ b,
            (zlib.crc32(g.encode("utf-8")) for g in genres),
        )
        hue = float(genre_hash & 0x0000FF) / float(0x0000FF)
        sat = float(genre_hash & 0x00FF00) / float(0x00FF00)
        val = float(genre_hash & 0xFF0000) / float(0xFF0000)

        print(f"[bold][green]{track_name}[/green] : [blue]{album}[/blue] : [cyan]{artist_names}[/cyan][/bold]")
        print(f"[bold purple]Artist genres: {', '.join(genres)}")
        print(f"[bold red]{hue} {sat} {val}")

        self.lights.set_params(
            params.Params(
                h=hue,
                s=sat,
                v=val,
                dh=0.05,
                ds=0.0,
                dv=0.0,
                t=0.15,
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

    fsm = FSM(sp, args[1])

    try:
        fsm.run()
    except KeyboardInterrupt:
        raise
    except:
        print(fsm.track)
        raise


if __name__ == "__main__":
    main(sys.argv)
