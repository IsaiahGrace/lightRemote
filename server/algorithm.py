import math
import random


class Algorithm:
    def __init__(self, config, params):
        self.params = params
        self.config = config

        self.hue_vel = [random.random() for _ in range(self.config.num_pixels)]
        self.linear_sat_vel = [0] * self.config.num_pixels
        self.linear_val_vel = [0] * self.config.num_pixels

        self.linear_sat = [0] * self.config.num_pixels
        self.linear_val = [0] * self.config.num_pixels

        self.hue = [0] * self.config.num_pixels
        self.sat = [0] * self.config.num_pixels
        self.val = [0] * self.config.num_pixels

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
            inverse_target = (target + 0.5) % 1
            for i in range(len(position)):
                p = position[i]
                v = velocity[i]

                if random.random() < self.params.t:
                    if random.random() > 0.5:
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
                    p = max(p, 0.0)
                    p = min(p, 1.0)

                position[i] = p
                velocity[i] = v
