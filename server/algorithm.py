import math
import numpy as np


class Algorithm:
    def __init__(self, config, params):
        self.params = params
        self.config = config
        self.rng = np.random.default_rng()

        self.entropy = np.ones(self.config.num_pixels)

        self.hue_vel = np.zeros(self.config.num_pixels)
        self.linear_sat_vel = np.zeros(self.config.num_pixels)
        self.linear_val_vel = np.zeros(self.config.num_pixels)

        self.linear_sat = np.zeros(self.config.num_pixels)
        self.linear_val = np.zeros(self.config.num_pixels)

        self.hue = self.rng.random(self.config.num_pixels)
        self.sat = np.zeros(self.config.num_pixels)
        self.val = np.zeros(self.config.num_pixels)

    def set_params(self, params):
        self.params = params
        self.params.s = math.pow(self.params.s, self.config.scaling_root)
        self.params.v = math.pow(self.params.v, self.config.scaling_root)

    def update(self):
        for position, velocity, target, tolerance, wraps in (
            (self.hue, self.hue_vel, self.params.h, self.params.dh, True),
            (self.linear_sat, self.linear_sat_vel, self.params.s, self.params.ds, False),
            (self.linear_val, self.linear_val_vel, self.params.v, self.params.dv, False),
        ):
            self.rng.random(self.config.num_pixels, out=self.entropy)
            inverse_target = (target + 0.5) % 1
            for i in range(self.config.num_pixels):
                p = position[i]
                v = velocity[i]

                if self.entropy[i] < self.params.t:
                    if self.entropy[i] > self.params.t / 2.0:
                        v += self.config.delta
                    else:
                        v -= self.config.delta

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
                    v -= self.config.delta * 0.1
                if p < target - tolerance:
                    v += self.config.delta * 0.1

                p += v
                v *= 0.85  # friction, sensitive

                if wraps:
                    p %= 1
                else:
                    p = p if p > 0.0 else 0.0
                    p = p if p < 1.0 else 1.0

                position[i] = p
                velocity[i] = v

        for i in range(self.config.num_pixels):
            self.sat[i] = math.pow(self.linear_sat[i], 1.0 / self.config.scaling_root)
            self.val[i] = math.pow(self.linear_val[i], 1.0 / self.config.scaling_root)
