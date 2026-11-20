"""Closed-form Alcubierre results (validation reference).

Alcubierre 1994, Class. Quantum Grav. 11, L73 (arXiv:gr-qc/0009013), eq. 18:

    T^ab n_a n_b = alpha^2 T^00 = G^00 / 8pi
                 = -(v^2 / 8pi) * (Y^2 + Z^2) / (4 r^2) * (df/dr)^2

with r = |x - x_s(t)| and (Y, Z) the transverse offsets. Written with the
Eulerian density rho_E:

    rho_E(x, y, z) = -(v^2 / 32 pi) * (y^2 + z^2) / r^2 * f'(r)^2        (*)

Integrating (*) over all space gives the total Eulerian energy of the bubble.
The angular factor has the exact average <(y^2+z^2)/r^2> = 2/3 over the sphere,
so

    E = -(v^2 / 12) * INT_0^inf f'(r)^2 r^2 dr                          (**)

Both (*) and (**) are reproduced numerically by the grid solver in
flatslice.py; tests/test_validation.py checks the agreement.
"""

from __future__ import annotations

import numpy as np

from .shapes import Shape


def rho_exact(shape: Shape, v: float, x, y, z) -> np.ndarray:
    """Eulerian energy density of a flat-slice bubble, geometric units."""
    x, y, z = np.broadcast_arrays(
        np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(z, dtype=float)
    )
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2)
    safe = np.where(r > 0, r, 1.0)
    radial = (y * y + z * z) / np.where(r2 > 0, r2, 1.0)
    df = shape.dfdr(safe)
    rho = -(v * v) / (32.0 * np.pi) * radial * df * df
    return np.where(r > 0, rho, 0.0)


def theta_exact(shape: Shape, v: float, x, y, z) -> np.ndarray:
    """Volume expansion theta = -alpha tr K = -div(beta) = v (x/r) f'(r)."""
    x, y, z = np.broadcast_arrays(
        np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(z, dtype=float)
    )
    r = np.sqrt(x * x + y * y + z * z)
    safe = np.where(r > 0, r, 1.0)
    return v * (x / safe) * shape.dfdr(safe)


def total_energy(shape: Shape, v: float, n: int = 20001, r_max: float | None = None) -> float:
    """Total Eulerian energy E = -(v^2/12) INT f'(r)^2 r^2 dr  (geometric units).

    For a wall much thinner than the bubble radius the radial factor r^2 is
    constant across the wall and the integral has the closed form

        INT f'^2 r^2 dr  ~  sigma R^2 / (3 tanh^2(sigma R))

    which is used whenever the wall is too thin to resolve on the sampling grid
    (a Planck-scale wall would otherwise integrate to zero).
    """
    r_max = r_max if r_max is not None else 6.0 * shape.r_outer
    sigma = shape.params.get("sigma")
    R = shape.params.get("R")
    if sigma is not None and R is not None and sigma * R > 1e3:
        integral = sigma * R * R / (3.0 * np.tanh(sigma * R) ** 2)
        return float(-(v * v) / 12.0 * integral)
    r = np.linspace(0.0, r_max, n)
    integrand = shape.dfdr(r) ** 2 * r**2
    return float(-(v * v) / 12.0 * np.trapezoid(integrand, r))


def beta_field(shape: Shape, v: float):
    """Return beta(x, y, z) for the grid solver: a bubble centred at the origin."""

    def _beta(x, y, z):
        r = np.sqrt(x * x + y * y + z * z)
        bx = -v * shape.f(r)
        zeros = np.zeros_like(r)
        return np.stack([bx, zeros, zeros])

    return _beta


def alpha_unity(x, y, z):
    return np.ones_like(np.sqrt(x * x + y * y + z * z))