"""ADM solver for flat-slice warp metrics.

Metric family handled here (all of it is the mainstream warp-drive literature):

    ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i + beta^i dt)(dx^j + beta^j dt)

with

    gamma_ij = delta_ij        (spatial slices are flat)
    alpha    = 1               (Eulerian observers are in free fall)
    beta^x   = -v f(r)         (shift; y, z components zero for a straight run)

Because gamma is flat and time independent, the 3-Ricci scalar vanishes and the
extrinsic curvature collapses to the flat-space symmetrised derivative

    K_ij = (1 / 2 alpha) (d_i beta_j + d_j beta_i)

so the Eulerian energy density is

    rho_E = T^{ab} n_a n_b = (K^2 - K_ij K^ij) / (16 pi)      [G = c = 1]

and the volume expansion of the Eulerian congruence is theta = -alpha tr K.

The engine is written against arbitrary shift *fields* on a grid (not against
any particular analytic shape), so new metric ansaetze plug in by supplying
beta and alpha; derivatives are 4th-order central differences in the interior
and 2nd-order one-sided at the boundary layers, which are excluded from the
integrated totals.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _d1(field: np.ndarray, h: float, axis: int) -> np.ndarray:
    """First derivative along one axis: 4th order inside, 2nd order at edges."""
    n = field.shape[axis]
    g = np.gradient(field, h, axis=axis, edge_order=2)
    if n >= 5:
        core = [slice(None)] * field.ndim
        core[axis] = slice(2, n - 2)

        def sl(off: int) -> tuple:
            return tuple(
                slice(2 + off, n - 2 + off) if d == axis else slice(None)
                for d in range(field.ndim)
            )

        g[tuple(core)] = (
            -field[sl(2)] + 8.0 * field[sl(1)] - 8.0 * field[sl(-1)] + field[sl(-2)]
        ) / (12.0 * h)
    return g


@dataclass
class Solution:
    rho: np.ndarray          # Eulerian energy density, geometric units
    theta: np.ndarray        # volume expansion of the Eulerian congruence
    K_tr: np.ndarray         # trace of extrinsic curvature
    K: np.ndarray            # K_ij, shape (3, 3, nx, ny, nz)
    grid: tuple              # (x, y, z) coordinate arrays
    h: float

    def total_energy(self, margin: int = 3) -> float:
        """Integral of rho over the cell-centred domain, boundary layers dropped."""
        core = (slice(margin, -margin),) * 3
        return float(self.rho[core].sum() * self.h**3)

    def peak_negative_density(self, margin: int = 3) -> float:
        core = (slice(margin, -margin),) * 3
        return float(self.rho[core].min())

    def interior_cells(self, margin: int = 3) -> int:
        return int(np.prod([n - 2 * margin for n in self.rho.shape]))


def solve_flat_slice(
    beta_field,
    alpha_field,
    domain: float,
    n: int,
    margin: int = 3,
) -> Solution:
    """Solve the constraint content of a flat-slice metric on an n^3 grid.

    beta_field(x, y, z) -> (3, nx, ny, nz) array of contravariant shift
    alpha_field(x, y, z) -> (nx, ny, nz) array of lapse
    domain: half-width of the cubic grid [-domain, domain]^3
    """
    lin = np.linspace(-domain, domain, n)
    h = lin[1] - lin[0]
    x, y, z = np.meshgrid(lin, lin, lin, indexing="ij")
    beta = np.asarray(beta_field(x, y, z), dtype=float)
    alpha = np.asarray(alpha_field(x, y, z), dtype=float)
    if np.any(alpha <= 0):
        raise ValueError("lapse must be positive")

    # dbeta[i][j] = d_i beta_j
    dbeta = [[_d1(beta[i], h, j) for j in range(3)] for i in range(3)]

    K = np.zeros((3, 3) + beta.shape[1:])
    for i in range(3):
        for j in range(3):
            K[i, j] = 0.5 * (dbeta[i][j] + dbeta[j][i]) / alpha

    K_tr = K[0, 0] + K[1, 1] + K[2, 2]
    K_sq = np.zeros_like(K_tr)
    for i in range(3):
        for j in range(3):
            K_sq += K[i, j] * K[i, j]        # gamma = delta, so K_ij K^ij = K_ij K_ij

    rho = (K_tr**2 - K_sq) / (16.0 * np.pi)
    theta = -alpha * K_tr

    return Solution(
        rho=rho,
        theta=theta,
        K_tr=K_tr,
        K=K,
        grid=(x, y, z),
        h=h,
    )


def weak_energy_condition_violated(sol: Solution, margin: int = 3) -> bool:
    """WEC holds iff rho >= 0 for every observer; one negative cell is enough."""
    return bool(sol.peak_negative_density(margin) < 0.0)