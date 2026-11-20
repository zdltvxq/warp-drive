"""Units and conversions.

In geometric units (G = c = 1) every quantity is expressed in metres:
mass -> G*M/c^2, energy -> G*E/c^4, time -> c*t.
"""

G = 6.67430e-11        # m^3 kg^-1 s^-2
C = 299792458.0        # m/s
M_SUN = 1.98847e30     # kg
J_PER_KG = C**2        # 8.98755e16 J/kg

M_SUN_GEOM = G * M_SUN / C**2      # 1476.6 m   (one solar mass as a length)
METRE_IN_JOULES = C**4 / G         # 1.2136e44 J (one metre of geometric energy)
LIGHT_YEAR = 9.4607304725808e15    # m
AU = 1.495978707e11                # m
YEAR = 3.15576e7                   # s


def geom_energy_to_joules(e_geom: float) -> float:
    return e_geom * METRE_IN_JOULES


def geom_energy_to_solar_masses(e_geom: float) -> float:
    return e_geom / M_SUN_GEOM


def joules_to_solar_masses(j: float) -> float:
    return j / J_PER_KG / M_SUN


if __name__ == "__main__":
    print(f"M_sun (geom)      = {M_SUN_GEOM:.3f} m")
    print(f"1 m of energy     = {METRE_IN_JOULES:.6e} J")
    print(f"1 ly              = {LIGHT_YEAR:.6e} m")