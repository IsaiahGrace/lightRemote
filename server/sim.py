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
temp = 0.5
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

        self.dbg_cnt = 0

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

        self.camera = rl.Camera3D(
            rl.Vector3(2, 1, 2),
            rl.Vector3(0, 0, 0),
            rl.Vector3(0, 1, 0),
            60.0,
            rl.CameraProjection.CAMERA_PERSPECTIVE,
        )

        while not rl.window_should_close():
            try:
                self.params = self.param_updates.get(block=False)
            except queue.Empty:
                pass
            self.update()
            self.render()

        rl.close_window()

    def render(self):
        # rl.update_camera(self.camera, rl.CameraMode.CAMERA_ORBITAL)

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode_3d(self.camera)

        for i, h, s, v in zip(self.idx, self.hue, self.sat, self.val):
            posX = (i * pixel_size) % window_size
            posZ = (i // (window_size // pixel_size)) * pixel_size
            red, green, blue = colorsys.hsv_to_rgb(h, s, v)
            color = rl.Color(
                int(red * 255),
                int(green * 255),
                int(blue * 255),
                255,
            )
            rl.draw_plane(
                rl.Vector3((posX / 100) - 5, 0, (posZ / 100) - 5),
                rl.Vector2(pixel_size / 100, pixel_size / 100),
                color,
            )
            rl.draw_cube_v(
                rl.Vector3(
                    v * s * math.cos(h * 2 * math.pi),
                    v,
                    v * s * math.sin(h * 2 * math.pi),
                ),
                rl.Vector3(0.05, 0.05, 0.05),
                color,
            )
        rl.end_mode_3d()
        rl.end_drawing()

    def update(self):
        if self.dbg_cnt % 60 == 0:
            print(f"hue: {self.hue[0]:0.4f}, sat: {self.sat[0]:0.4f}, val: {self.val[0]:0.4f}")
        self.dbg_cnt += 1

        for component, target, tolerance, wraps in (
            (self.hue, self.params.h, self.params.dh, True),
            (self.sat, self.params.s, self.params.ds, False),
            (self.val, self.params.v, self.params.dv, False),
        ):
            for i in range(len(component)):
                c = component[i]
                if random.random() < temp:
                    if random.random() > 0.5:
                        c += delta
                    else:
                        c -= delta

                if wraps:
                    dc = target - c
                    # TODO: Re-think these cases
                    if dc > 0.5 and c > (target + tolerance) % 1.0:
                        c -= delta
                    elif dc < -0.5 and c < (target - tolerance) % 1.0:
                        c += delta
                    elif dc > -0.5 and c > target + tolerance:
                        c -= delta
                    elif dc < 0.5 and c < target - tolerance:
                        c += delta
                else:
                    if c > target + tolerance:
                        c -= delta
                    if c < target - tolerance:
                        c += delta

                if wraps:
                    if c > 1.0:
                        c -= 1.0
                    if c < 0.0:
                        c += 1.0
                else:
                    c = max(c, 0.0)
                    c = min(c, 1.0)

                component[i] = c
