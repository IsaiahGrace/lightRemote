import math
import numpy as np


class Algorithm:
    def __init__(self, config, params):
        self.params = params
        self.config = config
        self.rng = np.random.default_rng()

        self.force = np.ones(1)

        self.hue_vel = np.zeros(1)
        self.linear_sat_vel = np.zeros(1)
        self.linear_val_vel = np.zeros(1)

        self.linear_sat = np.zeros(1)
        self.linear_val = np.zeros(1)

        self.hue = self.rng.random(1)
        self.sat = np.zeros(1)
        self.val = np.zeros(1)

        self.hue_snake = np.full(self.config.num_pixels, self.hue[0])
        self.sat_snake = np.zeros(self.config.num_pixels)
        self.val_snake = np.zeros(self.config.num_pixels)

    def set_params(self, params):
        self.params = params
        self.params.s = math.pow(self.params.s, 1.0 / self.config.scaling_root)
        self.params.v = math.pow(self.params.v, 1.0 / self.config.scaling_root)

    def update(self):
        for position, velocity, target, tolerance, wraps in (
            (self.hue, self.hue_vel, self.params.h, self.params.dh, True),
            (self.linear_sat, self.linear_sat_vel, self.params.s, self.params.ds, False),
            (self.linear_val, self.linear_val_vel, self.params.v, self.params.dv, False),
        ):
            # Sometimes the fastest way to get to the target is to decriment
            # the hue, and wrap around from 0 -> 1. The "inverse target" is
            # the opposite point on the hue circle. By adding or subtracting
            # 1, we make the comparisons below simpler. Because we wrap the
            # values at the end of this function, the offset here doesn't
            # effect the final value.
            inverse_target = (target + 0.5) % 1
            if wraps:
                if inverse_target > target:
                    np.subtract(position, 1.0, where=position > inverse_target, out=position)
                else:
                    np.add(position, 1.0, where=position < inverse_target, out=position)

            # Calculate random forces on the pixel due to temperature
            self.rng.random(1, out=self.force)
            np.subtract(self.force, self.params.t, out=self.force)
            np.clip(self.force, None, 0.0, out=self.force)
            np.add(self.force, self.params.t / 2.0, where=self.force != 0, out=self.force)
            np.sign(self.force, out=self.force)
            np.multiply(self.force, self.config.delta, out=self.force)

            # Apply restoring forces
            restoring_delta = self.config.delta * self.config.restoring_force
            if wraps or target == 0.0:
                np.subtract(self.force, restoring_delta, where=position > target + tolerance, out=self.force)

            np.add(self.force, restoring_delta, where=position < target - tolerance, out=self.force)

            # Acceleration = Force / Mass
            np.divide(self.force, self.config.mass, out=self.force)

            # Velocity += Acceleration
            np.add(velocity, self.force, out=velocity)

            # Position += Velocity
            np.add(position, velocity, out=position)

            # Velocity *= friction
            np.multiply(velocity, self.config.friction, out=velocity)

            if wraps:
                np.mod(position, 1.0, out=position)
            else:
                np.clip(position, 0.0, 1.0, out=position)

        np.power(self.linear_sat, 1.0 / self.config.scaling_root, out=self.sat)
        np.power(self.linear_val, 1.0 / self.config.scaling_root, out=self.val)

        self.hue_snake = np.roll(self.hue_snake, 1)
        self.sat_snake = np.roll(self.sat_snake, 1)
        self.val_snake = np.roll(self.val_snake, 1)
        self.hue_snake[0] = self.hue[0]
        self.sat_snake[0] = self.sat[0]
        self.val_snake[0] = self.val[0]
