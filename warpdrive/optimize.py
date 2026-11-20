"""Energy budget of a warp bubble: what the design space actually costs.

The total Eulerian energy

    E = -(v^2 / 12) * INT f'(r)^2 r^2 dr

is negative for every admissible shape, and for a fixed wall *fraction*
Delta / r_ship it scales as

    |E| ~ v^2 * r_ship^2 / Delta      (Delta = wall thickness)

so there are only three knobs: speed (v), payload size (r_ship) and wall
thickness (Delta). The physical constraints bound them:

    payload radius   r_ship : f(r) ~ 1 for r <= r_ship
    vehicle extent   r_out  : f(r) ~ 0 for r >= r_out     =>  Delta <= r_out - r_ship
    quantum inequality       : Delta is bounded from ABOVE by QFT (Pfenning & Ford
                               1997: a few hundred Planck lengths), not below

min_energy() returns the cheapest bubble that satisfies the first two, i.e. the
thickest wall the vehicle envelope allows. planck_wall_energy() evaluates the
opposite corner of the design space: the thin wall that the quantum inequality
demands.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import alcubierre, shapes, units

EPS = 1e-3            # "the shift has vanished" tolerance on f
PLANCK_LENGTH = 1.616255e-35


@dataclass
class Candidate:
    label: str
    shape: shapes.Shape
    energy: float          # geometric units (negative)

    def report(self, v: float) -> dict:
        e = self.energy
        return {
            "shape": self.label,
            "v_c": v,
            "E_geom_m": e,
            "E_solar": units.geom_energy_to_solar_masses(e),
            "E_joules": units.geom_energy_to_joules(e),
            "abs_E_over_c2_kg": abs(units.geom_energy_to_joules(e)) / units.C**2,
            "r_ship_m": self.shape.r_ship,
            "r_outer_m": self.shape.r_outer,
        }


def sigma_min_tanh(r_ship: float, r_out: float, eps: float = EPS) -> float:
    """Smallest sigma whose tanh wall has decayed to f(r_out) <= eps.

    f(r_out) decreases monotonically in sigma, so a log-space bisection lands on
    the thickest admissible wall.
    """
    lo, hi = 1e-6 / r_ship, 1e3 / r_ship
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        f = float(shapes.alcubierre_tanh(R=r_ship, sigma=mid).f(r_out))
        if f > eps:
            lo = mid
        else:
            hi = mid
        if hi / lo - 1.0 < 1e-12:
            break
    return float(hi)


def tanh_candidate(r_ship: float, r_out: float, v: float) -> Candidate:
    sh = shapes.alcubierre_tanh(R=r_ship, sigma=sigma_min_tanh(r_ship, r_out))
    return Candidate(sh.name, sh, alcubierre.total_energy(sh, v))


def compact_candidate(r_ship: float, r_out: float, v: float) -> Candidate:
    sh = shapes.compact_smoothstep(r_ship, r_out)
    return Candidate(sh.name, sh, alcubierre.total_energy(sh, v))


def gaussian_candidate(r_ship: float, r_out: float, v: float) -> Candidate | None:
    """f = exp(-(r/s)^4): needs s >= 5.6 r_ship for f(r_ship) >= 1-1e-3."""
    r_scale = r_ship / (np.log(1.0 / (1.0 - EPS)) ** 0.25)
    sh = shapes.gaussian_shell(r_scale=float(r_scale), power=4)
    if float(sh.f(r_out)) > EPS:
        return None
    return Candidate(sh.name, sh, alcubierre.total_energy(sh, v))


def min_energy(
    r_ship: float, r_out: float, v: float, families: tuple = ("tanh", "compact", "gaussian")
) -> Candidate:
    pool: list[Candidate] = []
    if "tanh" in families:
        pool.append(tanh_candidate(r_ship, r_out, v))
    if "compact" in families:
        pool.append(compact_candidate(r_ship, r_out, v))
    if "gaussian" in families:
        cand = gaussian_candidate(r_ship, r_out, v)
        if cand is not None:
            pool.append(cand)
    if not pool:
        raise RuntimeError("no shape satisfies the constraints; widen r_out or drop the family")
    return max(pool, key=lambda c: c.energy)      # least negative = cheapest


def sweep_outer_ratio(r_ship: float, v: float, ratios=(1.2, 1.5, 2.0, 3.0, 5.0, 10.0)) -> list[dict]:
    rows = []
    for ratio in ratios:
        best = min_energy(r_ship, r_ship * ratio, v)
        row = best.report(v)
        row["r_out_over_r_ship"] = ratio
        rows.append(row)
    return rows


def cheapest(r_ship: float, v: float, ratio_lo: float = 1.02, ratio_hi: float = 50.0,
             points: int = 80) -> tuple[Candidate, float]:
    """Least |E| over the vehicle envelope, with the optimum envelope ratio.

    |E| is *not* monotone in the envelope size: widening r_out allows a thicker
    wall (cheaper) but drags the exponential tail of f out to larger r, where the
    r^2 weight in INT f'^2 r^2 dr dominates. The scan finds the crossover.
    """
    best: tuple[Candidate, float] | None = None
    for ratio in np.geomspace(ratio_lo, ratio_hi, points):
        try:
            cand = min_energy(r_ship, r_ship * ratio, v)
        except RuntimeError:
            continue
        if best is None or cand.energy > best[0].energy:
            best = (cand, float(ratio))
    if best is None:
        raise RuntimeError("no admissible bubble")
    return best


def planck_wall_energy(r_ship: float, v: float, thickness: float) -> Candidate:
    """Bubble whose wall is `thickness` metres — the regime QI restrictions force."""
    if thickness <= 0:
        raise ValueError("thickness must be positive")
    sh = shapes.alcubierre_tanh(R=r_ship, sigma=1.0 / thickness)
    return Candidate(f"wall={thickness:.3e} m", sh, alcubierre.total_energy(sh, v))


def qi_audit(r_ship: float, v: float, planck_lengths=(10.0, 100.0, 1000.0)) -> list[dict]:
    rows = []
    for n in planck_lengths:
        cand = planck_wall_energy(r_ship, v, n * PLANCK_LENGTH)
        row = cand.report(v)
        row["wall_planck_lengths"] = n
        rows.append(row)
    return rows