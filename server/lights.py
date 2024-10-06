from rich import print
import params
import sim
import threading


class Lights:
    def __init__(self, sim_lights=0):
        if sim_lights > 0:
            self.sim = sim.LightSim(sim_lights)
        else:
            self.sim = False

    def set_params(
        self,
        params,
    ):
        # TODO: Call the pixelblaze websocket API to update the pattern parameters.
        # https://electromage.com/docs/websockets-api
        if self.sim:
            self.sim.set_params(params)
