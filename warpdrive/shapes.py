"""Bubble shape functions f(r) and their radial derivatives.

All shapes are 1 at the ship (r = 0) and 0 far away, monotone decreasing in r,
so the shift is beta^x = -v * f(r) and the ship rides inside the bubble.

Two families are implemented because the energy budget of a warp bubble is
governed almost entirely by df/dr:

  * Alcubierre tanh wall   -- the 1994 shape; wall thickness ~ 1/sigma,
                              no compact support (tails go to infinity).
  * compact smootherstep   -- C2 profile with exact support [r_in, r_out];
                              f == 1 inside r_in, f == 0 beyond r_out.

The optimizer in optimize.py trades these against each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class Shape:
    name: str
    f: Callable[[float | np.ndarray], np.ndarray]
    dfdr: Callable[[float | np.ndarray], np.ndarray]
    r_ship: float        # radius over which f ~ 1 (the payload lives here)
    r_outer: float       # radius beyond which f has essentially vanished
    params: dict

    def __call__(self, r):
        return self.f(r)


def alcubierre_tanh(R: float = 1.0, sigma: float = 8.0) -> Shape:
    """f(r) = [tanh(s(r+R)) - tanh(s(r-R))] / (2 tanh(sR))   (Alcubierre 1994, eq. 6).

    R      half-width of the flat interior,
    sigma  inverse wall thickness.
    """
    if R <= 0 or sigma <= 0:
        raise ValueError("R and sigma must be positive")
    norm = 2.0 * np.tanh(sigma * R)

    def f(r):
        r = np.asarray(r, dtype=float)
        return (np.tanh(sigma * (r + R)) - np.tanh(sigma * (r - R))) / norm

    def dfdr(r):
        r = np.asarray(r, dtype=float)
        sech2 = lambda x: 1.0 / np.cosh(np.clip(x, -40.0, 40.0)) ** 2
        return sigma * (sech2(sigma * (r + R)) - sech2(sigma * (r - R))) / norm

    return Shape(
        name=f"alcubierre_tanh(R={R:g},sigma={sigma:g})",
        f=f,
        dfdr=dfdr,
        r_ship=R,
        r_outer=R + 4.0 / sigma,   # tanh tail is < 2e-3 beyond this
        params={"R": R, "sigma": sigma},
    )


def compact_smoothstep(r_in: float = 1.0, r_out: float = 2.0) -> Shape:
    """C2 compact shape: f = 1 - smootherstep((r - r_in)/(r_out - r_in))."""
    if not 0 < r_in < r_out:
        raise ValueError("need 0 < r_in < r_out")
    width = r_out - r_in

    def f(r):
        r = np.asarray(r, dtype=float)
        u = np.clip((r - r_in) / width, 0.0, 1.0)
        return 1.0 - (6 * u**5 - 15 * u**4 + 10 * u**3)

    def dfdr(r):
        r = np.asarray(r, dtype=float)
        u = np.clip((r - r_in) / width, 0.0, 1.0)
        dsdu = 30 * u**2 * (u - 1) ** 2          # d/du smootherstep
        return -dsdu / width

    return Shape(
        name=f"compact_smoothstep({r_in:g},{r_out:g})",
        f=f,
        dfdr=dfdr,
        r_ship=r_in,
        r_outer=r_out,
        params={"r_in": r_in, "r_out": r_out},
    )


def gaussian_shell(r_scale: float = 1.0, power: int = 4) -> Shape:
    """f = exp(-(r/r_scale)^power) — very smooth, but with infinite tails."""
    if r_scale <= 0 or power < 2:
        raise ValueError("bad parameters")

    def f(r):
        r = np.asarray(r, dtype=float)
        return np.exp(-((r / r_scale) ** power))

    def dfdr(r):
        r = np.asarray(r, dtype=float)
        return -power * r ** (power - 1) / r_scale**power * np.exp(-((r / r_scale) ** power))

    return Shape(
        name=f"gaussian_shell(r={r_scale:g},p={power})",
        f=f,
        dfdr=dfdr,
        r_ship=r_scale / 2,
        r_outer=r_scale * 1.6,
        params={"r_scale": r_scale, "power": power},
    )