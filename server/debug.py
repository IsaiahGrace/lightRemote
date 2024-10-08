import algorithm
import colorsys
import math
import params
import pyray as rl
import queue
import threading

window_size = 1000

config = params.Config(
    delta=(1.0 / 2000.0),
    num_pixels=400,
    scaling_root=1.2,
    restoring_force=0.1,
)


class Display:
    def __init__(self):
        self.param_updates = queue.Queue()
        self.frame = 0
        self.algorithm = algorithm.Algorithm(config, params.Params())

        self.red = [0] * config.num_pixels
        self.green = [0] * config.num_pixels
        self.blue = [0] * config.num_pixels

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def set_params(self, params):
        self.param_updates.put(params)

    def run(self):
        rl.init_window(window_size, window_size, "musical lights simulator")
        rl.set_target_fps(60)
        rl.clear_background(rl.RAYWHITE)

        self.camera_3d = rl.Camera3D(
            [2, -2, 2],
            [0, 0, 0],
            [0, 1, 0],
            60.0,
            rl.CameraProjection.CAMERA_PERSPECTIVE,
        )
        self.texture_3d = rl.load_render_texture(window_size // 2, window_size // 2)

        while not rl.window_should_close():
            self.frame += 1
            self.update_params()
            self.algorithm.update()
            self.update_rgb()
            self.render()
        rl.unload_render_texture(self.texture_3d)
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
            self.red[i] = int(r * 255)
            self.green[i] = int(g * 255)
            self.blue[i] = int(b * 255)

    def render(self):
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        self.draw_hsv_cylinder()
        self.draw_preview()
        self.draw_hs_plot()
        self.draw_vs_plot()
        self.draw_h_line()

        rl.draw_text(f"Hue\n\n{self.algorithm.params.h:0.4f}", 5, 5, 30, rl.DARKGRAY)
        rl.draw_rectangle_v([window_size // 2 - 5, 0], [10, window_size], rl.LIGHTGRAY)
        rl.draw_rectangle_v([0, window_size // 2 - 5], [window_size, 10], rl.LIGHTGRAY)

        rl.end_drawing()

    def draw_h_line(self):
        params = self.algorithm.params
        for r, g, b, h in zip(self.red, self.green, self.blue, self.algorithm.hue):
            rl.draw_circle(540 + int(h * 440), 900, 6, [r, g, b, 255])

        # main axis, ticks at 0 & 1
        rl.draw_line_v([540 - 10, 920], [540 + 440 + 10, 920], rl.LIGHTGRAY)
        rl.draw_line_v([540, 910], [540, 930], rl.LIGHTGRAY)
        rl.draw_line_v([540 + 440, 910], [540 + 440, 930], rl.LIGHTGRAY)
        rl.draw_text("0", 540, 940, 30, rl.DARKGRAY)
        rl.draw_text("1", 540 + 430, 940, 30, rl.DARKGRAY)

        # Hue target value
        rl.draw_line_v(
            [540 + int(440 * params.h), 910],
            [540 + int(440 * params.h), 930],
            rl.DARKGRAY,
        )
        rl.draw_text(f"{params.h:0.4f}", 500 + int(440 * params.h), 940, 30, rl.DARKGRAY)

        # Hue bounds:
        rl.draw_line_v(
            [540 + int(440 * ((params.h - params.dh) % 1)), 910],
            [540 + int(440 * ((params.h - params.dh) % 1)), 930],
            rl.DARKGRAY,
        )
        rl.draw_line_v(
            [540 + int(440 * ((params.h + params.dh) % 1)), 910],
            [540 + int(440 * ((params.h + params.dh) % 1)), 930],
            rl.DARKGRAY,
        )

        # Opposite Hue
        rl.draw_line_v(
            [540 + int(440 * ((params.h + 0.5) % 1)), 890],
            [540 + int(440 * ((params.h + 0.5) % 1)), 930],
            rl.BLACK,
        )

    def draw_vs_plot(self):
        params = self.algorithm.params
        s = math.pow(params.s, 1.0 / config.scaling_root)
        v = math.pow(params.v, 1.0 / config.scaling_root)
        x = 500 + int(s * 500)
        y = int(500 - v * 500)
        rl.draw_line_v([x, 0], [x, 500], rl.DARKGRAY)
        rl.draw_line_v([500, y], [1000, y], rl.DARKGRAY)

        for r, g, b, s, v in zip(self.red, self.green, self.blue, self.algorithm.sat, self.algorithm.val):
            x = 500 + int(s * 500)
            y = int(500 - v * 500)
            rl.draw_circle(x, y, 5, [r, g, b, 255])

    def draw_hs_plot(self):
        params = self.algorithm.params
        x = 250 + int(245 * math.cos(params.h * 2 * math.pi))
        y = 250 + int(245 * math.sin(params.h * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.DARKGRAY)

        x = 250 + int(245 * math.cos((params.h - params.dh) * 2 * math.pi))
        y = 250 + int(245 * math.sin((params.h - params.dh) * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.LIGHTGRAY)

        x = 250 + int(245 * math.cos((params.h + params.dh) * 2 * math.pi))
        y = 250 + int(245 * math.sin((params.h + params.dh) * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.LIGHTGRAY)

        s = math.pow(params.s, 1.0 / config.scaling_root)
        rl.draw_circle_lines(250, 250, 240 * s, rl.LIGHTGRAY)
        rl.draw_circle_lines(250, 250, 240, rl.LIGHTGRAY)

        for r, g, b, h, s in zip(self.red, self.green, self.blue, self.algorithm.hue, self.algorithm.sat):
            x = 250 + int(240 * s * math.cos(h * 2 * math.pi))
            y = 250 + int(240 * s * math.sin(h * 2 * math.pi))
            rl.draw_circle(x, y, 5, [r, g, b, 255])

    def draw_preview(self):
        pixel_size = 25
        preview_size = 500
        for i, (r, g, b) in enumerate(zip(self.red, self.green, self.blue)):
            x = (i * pixel_size) % preview_size
            y = 500 + (i // (preview_size // pixel_size)) * pixel_size
            rl.draw_rectangle_v([x, y], [pixel_size, pixel_size], [r, g, b, 255])

    def draw_hsv_cylinder(self):
        rl.begin_texture_mode(self.texture_3d)
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode_3d(self.camera_3d)

        rl.draw_cylinder_wires([0, -1, 0], 1, 1, 1, 16, rl.LIGHTGRAY)

        for r, g, b, h, s, v in zip(
            self.red,
            self.green,
            self.blue,
            self.algorithm.hue,
            self.algorithm.sat,
            self.algorithm.val,
        ):
            rl.draw_cube_v(
                [s * math.cos(h * 2 * math.pi), -v, s * math.sin(h * 2 * math.pi)],
                [0.05, 0.05, 0.05],
                [r, g, b, 255],
            )

        rl.end_mode_3d()
        rl.end_texture_mode()
        rl.draw_texture(self.texture_3d.texture, window_size // 2, window_size // 2, rl.WHITE)
