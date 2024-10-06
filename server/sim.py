import colorsys
import math
import params
import pyray as rl
import queue
import random
import threading


pixel_size = 50
pixels_per_side = 20
pixels_per_window = pixels_per_side * pixels_per_side
window_size = pixel_size * pixels_per_side

fps = 60
temp = 0.1
delta = 1.0 / 300.0


class LightSim:
    def __init__(self, num_lights):
        self.hue = [0] * num_lights
        self.sat = [1] * num_lights
        self.val = [0] * num_lights
        self.idx = list(range(pixels_per_window))
        random.shuffle(self.idx)
        self.param_updates = queue.Queue()
        self.params = params.Params()

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def set_params(self, params):
        print(params)
        self.param_updates.put(params)

    def run(self):
        print("Starting light sim")

        # rl.set_config_flags(rl.FLAG_WINDOW_TRANSPARENT)
        rl.init_window(window_size, window_size, "musical lights simulator")
        rl.set_target_fps(fps)
        # rl.set_window_state(rl.FLAG_WINDOW_UNDECORATED)
        rl.clear_background(rl.RAYWHITE)

        while not rl.window_should_close():
            try:
                self.params = self.param_updates.get(block=False)
            except queue.Empty:
                pass
            self.update()
            self.render()

        rl.close_window()

    def render(self):
        rl.begin_drawing()
        for i, h, s, v in zip(self.idx, self.hue, self.sat, self.val):
            posX = (i * pixel_size) % window_size
            posY = (i // (window_size // pixel_size)) * pixel_size
            red, green, blue = colorsys.hsv_to_rgb(h, s, v)
            rl.draw_rectangle(
                posX,
                posY,
                pixel_size,
                pixel_size,
                rl.Color(
                    int(red * 255),
                    int(green * 255),
                    int(blue * 255),
                    255,
                ),
            )
        rl.end_drawing()

    def update(self):
        for component, target, tolerance in (
            (self.hue, self.params.h, self.params.dh),
            (self.sat, self.params.s, self.params.ds),
            (self.val, self.params.v, self.params.dv),
        ):
            for i in range(len(component)):
                c = component[i]
                if random.random() < temp:
                    if random.random() > 0.5:
                        c += delta
                    else:
                        c -= delta
                if c > target + tolerance:
                    c -= delta
                if c < target - tolerance:
                    c += delta
                c = max(c, 0.0)
                c = min(c, 1.0)
                component[i] = c
