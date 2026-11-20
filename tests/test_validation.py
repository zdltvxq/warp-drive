"""Validation of the solver against Alcubierre 1994, eq. 18 and the free integral.

Run:  .venv/Scripts/python.exe -m unittest discover -s tests -v
"""

import unittest

import numpy as np

from warpdrive import alcubierre, flatslice, shapes, units


class TestFlatSliceSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shape = shapes.alcubierre_tanh(R=1.0, sigma=4.0)
        cls.v = 0.5
        cls.n = 241
        cls.domain = 4.0
        cls.sol = flatslice.solve_flat_slice(
            alcubierre.beta_field(cls.shape, cls.v),
            alcubierre.alpha_unity,
            domain=cls.domain,
            n=cls.n,
        )

    def test_pointwise_energy_density_matches_closed_form(self):
        x, y, z = self.sol.grid
        exact = alcubierre.rho_exact(self.shape, self.v, x, y, z)
        inner = (slice(6, -6),) * 3
        # scale by the local density scale: |rho| / (v^2 f'^2 / 32pi)
        ref = np.abs(exact[inner]).max()
        err = np.abs(self.sol.rho[inner] - exact[inner]).max() / ref
        self.assertLess(err, 5e-4, f"pointwise rho error {err:.2e}")

    def test_expansion_matches_divergence_of_shift(self):
        x, y, z = self.sol.grid
        exact = alcubierre.theta_exact(self.shape, self.v, x, y, z)
        inner = (slice(6, -6),) * 3
        err = np.abs(self.sol.theta[inner] - exact[inner]).max() / np.abs(exact[inner]).max()
        self.assertLess(err, 5e-4, f"theta error {err:.2e}")

    def test_total_energy_matches_radial_integral(self):
        e_grid = self.sol.total_energy()
        e_int = alcubierre.total_energy(self.shape, self.v)
        rel = abs(e_grid - e_int) / abs(e_int)
        self.assertLess(rel, 0.02, f"total energy mismatch {rel:.2%} (grid {e_grid:.5f} vs {e_int:.5f})")

    def test_dropping_resolution_converges_at_fourth_order(self):
        sh, v = self.shape, self.v
        errs = []
        for n in (121, 241):
            sol = flatslice.solve_flat_slice(
                alcubierre.beta_field(sh, v), alcubierre.alpha_unity, domain=self.domain, n=n
            )
            x, y, z = sol.grid
            exact = alcubierre.rho_exact(sh, v, x, y, z)
            inner = (slice(6, -6),) * 3
            errs.append(np.abs(sol.rho[inner] - exact[inner]).max())
        order = np.log2(errs[0] / errs[1]) / np.log2(2)
        self.assertGreater(order, 3.0, f"observed order {order:.2f}")

    def test_energy_is_negative_everywhere(self):
        self.assertTrue(flatslice.weak_energy_condition_violated(self.sol))


class TestScalingLaws(unittest.TestCase):
    def test_energy_scales_as_velocity_squared(self):
        sh = shapes.alcubierre_tanh(R=1.0, sigma=6.0)
        e1 = alcubierre.total_energy(sh, 1.0)
        e10 = alcubierre.total_energy(sh, 10.0)
        self.assertAlmostEqual(e10 / e1, 100.0, delta=1e-6 * 100)

    def test_energy_scales_linearly_with_radius(self):
        # E ~ v^2 R / wall-fraction: fixed R/sigma ratio means E proportional to R
        e1 = alcubierre.total_energy(shapes.alcubierre_tanh(R=1.0, sigma=6.0), 1.0)
        e10 = alcubierre.total_energy(shapes.alcubierre_tanh(R=10.0, sigma=0.6), 1.0)
        self.assertAlmostEqual(e10 / e1, 10.0, delta=1e-6 * 10)

    def test_thicker_wall_costs_less_energy(self):
        thin = abs(alcubierre.total_energy(shapes.alcubierre_tanh(R=1.0, sigma=20.0), 1.0))
        thick = abs(alcubierre.total_energy(shapes.alcubierre_tanh(R=1.0, sigma=2.0), 1.0))
        self.assertLess(thick, thin)


class TestUnits(unittest.TestCase):
    def test_solar_mass_in_metres(self):
        self.assertAlmostEqual(units.M_SUN_GEOM, 1476.6, delta=1.0)

    def test_round_trip_energy_conversion(self):
        e = 1.0
        j = units.geom_energy_to_joules(e)
        self.assertAlmostEqual(units.joules_to_solar_masses(j) * units.M_SUN_GEOM, e, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)