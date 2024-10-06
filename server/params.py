from dataclasses import dataclass


@dataclass
class Params:
    h: float = 0.0
    s: float = 0.0
    v: float = 0.0
    dh: float = 0.0
    ds: float = 0.0
    dv: float = 0.0
