"""Warp Engine — numerical core.

Everything here works in geometric units G = c = 1: lengths in metres,
energies in metres, velocities as a fraction of c.
"""

from . import units, shapes, flatslice, alcubierre, optimize

__all__ = ["units", "shapes", "flatslice", "alcubierre", "optimize"]