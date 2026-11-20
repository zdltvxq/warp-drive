"""Warp Engine audit: what the design space costs.

Prints three tables that the design documents quote, and writes two figures:

  tab1  minimum |E| bubble for a fixed payload radius, vs cruise speed
  tab2  minimum |E| vs how much room the wall is allowed to take
  tab3  shape families compared at identical constraints
  figs/rho_axis.png     energy density slice through the bubble
  figs/energy_curves.png  |E| vs wall thickness and vs outer radius

Run:  .venv/Scripts/python.exe scripts/audit.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warpdrive import alcubierre, optimize, shapes, units  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
FIGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figs")


def fmt_energy(e_geom: float) -> str:
    return (
        f"{e_geom:+.4e} m   "
        f"{units.geom_energy_to_solar_masses(e_geom):+.3e} M_sun   "
        f"{units.geom_energy_to_joules(e_geom):+.3e} J   "
        f"|E|/c^2 = {abs(units.geom_energy_to_joules(e_geom)) / units.C**2:.3e} kg"
    )


def write_csv(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fields: list[str] = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def tab1_speed(r_ship: float, ratio: float | None = None) -> list[dict]:
    label = f"envelope {ratio:g} x r_ship" if ratio else "cheapest over envelope"
    print(f"\n[tab1] payload radius r_ship = {r_ship:g} m, {label}")
    rows = []
    for v in (0.01, 0.1, 1.0, 10.0, 100.0):
        if ratio is None:
            best, r_ratio = optimize.cheapest(r_ship, v)
        else:
            best, r_ratio = optimize.min_energy(r_ship, r_ship * ratio, v), ratio
        row = best.report(v)
        row["r_out_over_r_ship"] = r_ratio
        rows.append(row)
        print(
            f"  v = {v:6g} c  r_out/r_ship = {r_ratio:6.2f}  "
            f"{best.label:38s} E = {fmt_energy(best.energy)}"
        )
    return rows


def tab2_room(r_ship: float, v: float) -> list[dict]:
    print(f"\n[tab2] payload radius r_ship = {r_ship:g} m at v = {v:g} c")
    rows = optimize.sweep_outer_ratio(r_ship, v)
    for row in rows:
        print(
            f"  r_out/r_ship = {row['r_out_over_r_ship']:5.1f}  {row['shape']:40s} "
            f"E = {fmt_energy(row['E_geom_m'])}"
        )
    return rows


def tab3_families(r_ship: float, r_out: float, v: float) -> list[dict]:
    print(f"\n[tab3] families at r_ship = {r_ship:g} m, r_out = {r_out:g} m, v = {v:g} c")
    rows = []
    for family in ("tanh", "compact", "gaussian"):
        try:
            best = optimize.min_energy(r_ship, r_out, v, families=(family,))
        except RuntimeError as exc:
            print(f"  {family:9s} inadmissible: {exc}")
            continue
        row = best.report(v)
        row["family"] = family
        rows.append(row)
        print(f"  {family:9s} {best.label:44s} E = {fmt_energy(best.energy)}")
    return rows


def tab4_quantum_inequality(r_ship: float, v: float) -> list[dict]:
    print(
        f"\n[tab4] wall thickness forced by the quantum inequality "
        f"(Pfenning & Ford 1997), r_ship = {r_ship:g} m, v = {v:g} c"
    )
    rows = optimize.qi_audit(r_ship, v)
    for row in rows:
        print(
            f"  wall = {row['wall_planck_lengths']:6.0f} l_P  "
            f"{fmt_energy(row['E_geom_m'])}"
        )
    return rows


def figures(r_ship: float = 10.0):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIGS, exist_ok=True)

    sh = shapes.alcubierre_tanh(R=r_ship, sigma=1.0 / (0.2 * r_ship))
    v = 1.0
    lin = np.linspace(-2.5 * r_ship, 2.5 * r_ship, 801)
    zero = np.zeros_like(lin)
    rho_axis = alcubierre.rho_exact(sh, v, lin, zero, zero)
    rho_off = alcubierre.rho_exact(sh, v, zero, lin, zero)   # transverse line

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(lin / r_ship, rho_axis, label="x axis (line of travel)")
    ax.plot(lin / r_ship, rho_off, label="y axis (transverse)")
    ax.set_xlabel("r / r_ship")
    ax.set_ylabel(r"$\rho_E$  [1/m$^2$, $G=c=1$]")
    ax.set_title(f"Eulerian energy density, v = {v:g}c, tanh wall")
    ax.axhline(0.0, color="k", lw=0.6)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "rho_axis.png"), dpi=140)
    plt.close(fig)

    sigmas = np.geomspace(0.5 / r_ship, 40.0 / r_ship, 80)
    energies = [abs(alcubierre.total_energy(shapes.alcubierre_tanh(R=r_ship, sigma=s), v)) for s in sigmas]
    ratios = np.linspace(1.15, 12.0, 60)
    ratio_e, ratio_fit = [], []
    for ratio in ratios:
        r_out = r_ship * ratio
        best = optimize.min_energy(r_ship, r_out, v)
        ratio_e.append(abs(best.energy))
        ratio_fit.append(r_out / r_ship)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    axes[0].loglog(sigmas * r_ship, [units.geom_energy_to_solar_masses(e) for e in energies])
    axes[0].set_xlabel(r"$\sigma \, r_{ship}$  (thin wall $\rightarrow$)")
    axes[0].set_ylabel("|E|  [M$_{\\odot}$]")
    axes[0].set_title("energy budget vs wall thickness")
    axes[0].grid(alpha=0.3, which="both")

    axes[1].loglog(ratio_fit, [units.geom_energy_to_solar_masses(e) for e in ratio_e], marker="o", ms=3)
    axes[1].set_xlabel(r"$r_{out} / r_{ship}$")
    axes[1].set_ylabel("|E|  [M$_{\\odot}$]")
    axes[1].set_title("cheapest bubble vs allowed vehicle extent")
    axes[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "energy_curves.png"), dpi=140)
    plt.close(fig)
    print(f"\nfigures written to {FIGS}")


def mission(v: float, r_ship: float, ratio: float, distance_ly: float = 4.246):
    best = optimize.min_energy(r_ship, r_ship * ratio, v)
    t = distance_ly / v
    print(f"\n[mission] {distance_ly:g} ly at v = {v:g} c, r_ship = {r_ship:g} m")
    print(f"  travel time            {t:.3f} yr")
    print(f"  cheapest admissible    {best.label}")
    print(f"  bubble energy          {fmt_energy(best.energy)}")


if __name__ == "__main__":
    r_ship = 10.0
    rows = tab1_speed(r_ship, ratio=None)
    rows += tab2_room(r_ship, v=1.0)
    rows += tab3_families(r_ship, r_out=2.0 * r_ship, v=1.0)
    rows += tab4_quantum_inequality(r_ship, v=1.0)
    write_csv(os.path.join(OUT, "energy_audit.csv"), rows)
    mission(10.0, r_ship, 2.0)
    figures(r_ship)