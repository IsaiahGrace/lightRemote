import colorsys
import math
import params
import pyray as rl
import queue
import random
import threading

window_size = 1000
fps = 60
delta = 1.0 / 2000.0
num_pixels = 400
scaling_root = 2


class LightSim:
    def __init__(self):
        self.hue_vel = [random.random() for _ in range(num_pixels)]
        self.linear_sat_vel = [0] * num_pixels
        self.linear_val_vel = [0] * num_pixels

        self.linear_sat = [0] * num_pixels
        self.linear_val = [0] * num_pixels

        self.hue = [0] * num_pixels
        self.sat = [0] * num_pixels
        self.val = [0] * num_pixels

        self.red = [0] * num_pixels
        self.green = [0] * num_pixels
        self.blue = [0] * num_pixels

        self.param_updates = queue.Queue()
        self.params = params.Params()
        self.frame = 0

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def set_params(self, params):
        self.param_updates.put(params)

    def run(self):
        rl.init_window(window_size, window_size, "musical lights simulator")
        rl.set_target_fps(fps)
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
            self.update_pixels()
            self.update_rgb()
            self.render()
        rl.unload_render_texture(self.texture_3d)
        rl.close_window()

    def update_params(self):
        try:
            self.params = self.param_updates.get(block=False)
            self.params.s = math.pow(self.params.s, scaling_root)
            self.params.v = math.pow(self.params.v, scaling_root)
        except queue.Empty:
            pass

    def update_pixels(self):
        for position, velocity, target, tolerance, wraps in (
            (self.hue, self.hue_vel, self.params.h, self.params.dh, True),
            (self.linear_sat, self.linear_sat_vel, self.params.s, self.params.ds, False),
            (self.linear_val, self.linear_val_vel, self.params.v, self.params.dv, False),
        ):
            inverse_target = (target + 0.5) % 1
            for i in range(len(position)):
                p = position[i]
                v = velocity[i]

                if random.random() < self.params.t:
                    if random.random() > 0.5:
                        v += delta
                    else:
                        v -= delta

                # Sometimes the fastest way to get to the target is to decriment
                # the hue, and wrap around from 0 -> 1. The "inverse target" is
                # the opposite point on the hue circle. By adding or subtracting
                # 1, we make the comparisons below simpler. Because we wrap the
                # values at the end of this function, the offset here doesn't
                # effect the final value.
                if wraps:
                    if inverse_target > target and p > inverse_target:
                        p -= 1
                    elif inverse_target < target and p < inverse_target:
                        p += 1

                if (wraps or target == 0.0) and p > target + tolerance:
                    v -= delta * 0.1
                if p < target - tolerance:
                    v += delta * 0.1

                p += v
                v *= 0.85  # friction, sensitive

                if wraps:
                    p %= 1
                else:
                    p = max(p, 0.0)
                    p = min(p, 1.0)

                position[i] = p
                velocity[i] = v

    def update_rgb(self):
        for linear, tuned in (
            (self.linear_sat, self.sat),
            (self.linear_val, self.val),
        ):
            for i, l in enumerate(linear):
                tuned[i] = math.pow(l, 1.0 / scaling_root)

        for i, (h, s, v) in enumerate(zip(self.hue, self.sat, self.val)):
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

        rl.draw_text(f"Hue\n\n{self.params.h:0.4f}", 5, 5, 30, rl.DARKGRAY)
        rl.draw_rectangle_v([window_size // 2 - 5, 0], [10, window_size], rl.LIGHTGRAY)
        rl.draw_rectangle_v([0, window_size // 2 - 5], [window_size, 10], rl.LIGHTGRAY)

        rl.end_drawing()

    def draw_h_line(self):
        for r, g, b, h in zip(self.red, self.green, self.blue, self.hue):
            rl.draw_circle(540 + int(h * 440), 900, 6, [r, g, b, 255])

        # main axis, ticks at 0 & 1
        rl.draw_line_v([540 - 10, 920], [540 + 440 + 10, 920], rl.LIGHTGRAY)
        rl.draw_line_v([540, 910], [540, 930], rl.LIGHTGRAY)
        rl.draw_line_v([540 + 440, 910], [540 + 440, 930], rl.LIGHTGRAY)
        rl.draw_text("0", 540, 940, 30, rl.DARKGRAY)
        rl.draw_text("1", 540 + 430, 940, 30, rl.DARKGRAY)

        # Hue target value
        rl.draw_line_v([540 + int(440 * self.params.h), 910], [540 + int(440 * self.params.h), 930], rl.DARKGRAY)
        rl.draw_text(f"{self.params.h:0.4f}", 500 + int(440 * self.params.h), 940, 30, rl.DARKGRAY)

        # Hue bounds:
        rl.draw_line_v(
            [540 + int(440 * ((self.params.h - self.params.dh) % 1)), 910],
            [540 + int(440 * ((self.params.h - self.params.dh) % 1)), 930],
            rl.DARKGRAY,
        )
        rl.draw_line_v(
            [540 + int(440 * ((self.params.h + self.params.dh) % 1)), 910],
            [540 + int(440 * ((self.params.h + self.params.dh) % 1)), 930],
            rl.DARKGRAY,
        )

        # Opposite Hue
        rl.draw_line_v(
            [540 + int(440 * ((self.params.h + 0.5) % 1)), 890],
            [540 + int(440 * ((self.params.h + 0.5) % 1)), 930],
            rl.BLACK,
        )

    def draw_vs_plot(self):
        s = math.pow(self.params.s, 1.0 / scaling_root)
        v = math.pow(self.params.v, 1.0 / scaling_root)
        x = 500 + int(s * 500)
        y = int(500 - v * 500)
        rl.draw_line_v([x, 0], [x, 500], rl.DARKGRAY)
        rl.draw_line_v([500, y], [1000, y], rl.DARKGRAY)

        for r, g, b, s, v in zip(self.red, self.green, self.blue, self.sat, self.val):
            x = 500 + int(s * 500)
            y = int(500 - v * 500)
            rl.draw_circle(x, y, 5, [r, g, b, 255])

    def draw_hs_plot(self):
        x = 250 + int(245 * math.cos(self.params.h * 2 * math.pi))
        y = 250 + int(245 * math.sin(self.params.h * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.DARKGRAY)

        x = 250 + int(245 * math.cos((self.params.h - self.params.dh) * 2 * math.pi))
        y = 250 + int(245 * math.sin((self.params.h - self.params.dh) * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.LIGHTGRAY)

        x = 250 + int(245 * math.cos((self.params.h + self.params.dh) * 2 * math.pi))
        y = 250 + int(245 * math.sin((self.params.h + self.params.dh) * 2 * math.pi))
        rl.draw_line_v([250, 250], [x, y], rl.LIGHTGRAY)

        s = math.pow(self.params.s, 1.0 / scaling_root)
        rl.draw_circle_lines(250, 250, 240 * s, rl.LIGHTGRAY)
        rl.draw_circle_lines(250, 250, 240, rl.LIGHTGRAY)

        for r, g, b, h, s in zip(self.red, self.green, self.blue, self.hue, self.sat):
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

        for r, g, b, h, s, v in zip(self.red, self.green, self.blue, self.hue, self.sat, self.val):
            rl.draw_cube_v(
                [s * math.cos(h * 2 * math.pi), -v, s * math.sin(h * 2 * math.pi)],
                [0.05, 0.05, 0.05],
                [r, g, b, 255],
            )

        rl.end_mode_3d()
        rl.end_texture_mode()
        rl.draw_texture(self.texture_3d.texture, window_size // 2, window_size // 2, rl.WHITE)
