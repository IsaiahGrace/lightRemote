from rich import print
import params
import sim
import threading


class Lights:
    def __init__(self):
        self.sim = sim.LightSim()

    def set_params(self, params):
        # TODO: Call the pixelblaze websocket API to update the pattern parameters.
        # https://electromage.com/docs/websockets-api
        self.sim.set_params(params)
