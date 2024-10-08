from dataclasses import dataclass


@dataclass
class Params:
    h: float = 0.0  # Hue
    s: float = 0.0  # Saturation
    v: float = 0.0  # Value
    dh: float = 0.0  # Hue tolerance (delta h)
    ds: float = 0.0  # Saturation tolerance (delta s)
    dv: float = 0.0  # Value tolerance (delta v)
    t: float = 0.0  # Pixel temperature


@dataclass
class Config:
    delta: float = 1.0 / 2000.0
    num_pixels: int = 400
    scaling_root: float = 2.0
    restoring_force: float = 0.1
    mass: float = 5.0
