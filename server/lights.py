from rich import print
import debug
import fullscreen
import params
import pixelblaze
import threading

# TODO: Create a pixelblaze backed using the pixelblaze websocket API to update the pattern parameters.
# https://electromage.com/docs/websockets-api


class Lights:
    def __init__(self, backend):
        self.display = {
            "debug": debug.Display,
            "fullscreen": fullscreen.Display,
            "pixelblaze": pixelblaze.Display,
        }[backend]()

    def set_params(self, params):
        self.display.set_params(params)
