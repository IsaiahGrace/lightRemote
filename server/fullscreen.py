import algorithm
import colorsys
import math
import numpy as np
import params
import pyray as rl
import queue
import threading

pixel_size = 50

config = params.Config(
    delta=(1.0 / 2000.0),
    num_pixels=0,
    scaling_root=1.2,
    restoring_force=0.1,
)


class Display:
    def __init__(self):
        self.param_updates = queue.Queue()
        self.window_width = 500
        self.window_height = 500
        self.display_width = self.window_width
        self.display_height = self.window_height

        self.thread = threading.Thread(target=self.setup)
        self.thread.start()

    def set_params(self, params):
        self.param_updates.put(params)

    def setup(self):
        rl.init_window(self.window_width, self.window_height, "Musical Lights")
        rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
        rl.set_target_fps(60)
        rl.clear_background(rl.RAYWHITE)

        monitor_count = rl.get_monitor_count()
        max_width = max(rl.get_monitor_width(m) for m in range(monitor_count))
        max_height = max(rl.get_monitor_height(m) for m in range(monitor_count))

        self.pixels_per_row = (max_width // pixel_size) + 1 * int(bool(max_width % pixel_size))
        self.pixels_per_col = (max_height // pixel_size) + 1 * int(bool(max_height % pixel_size))
        config.num_pixels = self.pixels_per_row * self.pixels_per_col

        print(f"rows: {self.pixels_per_row} cols: {self.pixels_per_col} pixels: {config.num_pixels}")

        self.algorithm = algorithm.Algorithm(config, params.Params())

        self.red = np.zeros(config.num_pixels, dtype=np.uint8)
        self.green = np.zeros(config.num_pixels, dtype=np.uint8)
        self.blue = np.zeros(config.num_pixels, dtype=np.uint8)

        self.run()

    def run(self):
        while not rl.window_should_close():
            self.update_params()
            self.algorithm.update()
            self.update_rgb()
            self.update_fullscreen()
            self.render()
        rl.close_window()

    def update_params(self):
        try:
            params = self.param_updates.get(block=False)
            self.algorithm.set_params(params)
        except queue.Empty:
            pass

    def update_rgb(self):
        for i, (h, s, v) in enumerate(zip(self.algorithm.hue, self.algorithm.sat, self.algorithm.val)):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            self.red[i] = r * 255
            self.green[i] = g * 255
            self.blue[i] = b * 255

    def update_fullscreen(self):
        if rl.is_key_pressed(rl.KEY_SPACE):
            if rl.is_window_fullscreen():
                rl.toggle_fullscreen()
                rl.set_window_size(self.window_width, self.window_height)

            else:
                self.window_width = rl.get_screen_width()
                self.window_height = rl.get_screen_height()

                monitor = rl.get_current_monitor()
                rl.set_window_size(
                    rl.get_monitor_width(monitor),
                    rl.get_monitor_height(monitor),
                )
                rl.toggle_fullscreen()

    def render(self):
        rl.begin_drawing()
        rl.clear_background(rl.RED)

        width = rl.get_render_width()
        height = rl.get_render_height()

        for i, (r, g, b) in enumerate(zip(self.red, self.green, self.blue)):
            x = (i % self.pixels_per_row) * pixel_size
            y = (i // self.pixels_per_row) * pixel_size

            if x > width:
                continue
            if y > height:
                break

            rl.draw_rectangle_v([x, y], [pixel_size, pixel_size], [r, g, b, 255])

        rl.draw_fps(5, height - 20)

        rl.end_drawing()
