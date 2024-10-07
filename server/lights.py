from rich import print
import params
import threading

# TODO: Create a pixelblaze backed using the pixelblaze websocket API to update the pattern parameters.
# https://electromage.com/docs/websockets-api


class Lights:
    def __init__(self, backend):
        # I'm putting the imports here so we don't
        # load the raylib library unnecessarily.

        if backend == "debug":
            import debug

            self.display = debug.Display()

        elif backend == "fullscreen":
            import fullscreen

            self.display = fullscreen.Display()

        elif backend == "pixelblaze":
            import pixelblaze

            self.display = pixelblaze.Display()

        else:
            raise ValueError(
                f"'{backend}' is not a recognized backend. Options are 'debug', 'fullscreen', and 'pixelblaze'"
            )

    def set_params(self, params):
        self.display.set_params(params)
