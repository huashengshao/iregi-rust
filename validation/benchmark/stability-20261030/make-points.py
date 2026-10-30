#!/usr/bin/env python3
"""Seeded random phase-space points for the binary64 stability study.

Setup follows the stability study of Hirschi and Peraro (arXiv:1604.01363,
sect. 7.2 and figs. 2-4): flat (RAMBO) phase space at sqrt(s) = 1 TeV with
p_T > 50 GeV for every final-state gluon and Delta R > 0.5 between final-state
gluons. Each point defines the shifts q_i = sum_{j<=i} k_j (all-incoming
momenta k_j in loop order, q_0 = 0) of one top-quark loop integral,
m_t = 173 GeV, mu = 1 TeV. Inputs are binary64; every code reads the same
binary64 values (the quadruple-precision reference converts them exactly).

usage: make-points.py OUTPUT_JSON
"""
import json
import math
import random
import sys

SQRT_S = 1000.0
MT2 = 173.0 ** 2
MH = 125.0
MU = 1000.0
SEED = 20261030
PT_MIN, DR_MIN = 50.0, 0.5

# id, external final state (gluon "g" or Higgs "H"), loop order of the
# final-state legs, rank, number of points.
INTEGRALS = [
    ("box-r4", "gg -> HH, top-loop box, rank 4", ["H", "H"], 4, 10000),
    ("box-r6", "gg -> HH kinematics, top-loop box, rank 6", ["H", "H"], 6, 10000),
    ("pentagon-r5", "gg -> Hgg, top-loop pentagon (g g g H g), rank 5", ["g", "H", "g"], 5, 5000),
    ("hexagon-r6", "gg -> gggg, top-loop hexagon, rank 6", ["g", "g", "g", "g"], 6, 2000),
]


def rambo_massless(n, energy, rng):
    q = []
    for _ in range(n):
        c = 2 * rng.random() - 1
        phi = 2 * math.pi * rng.random()
        e = -math.log(rng.random() * rng.random())
        s = math.sqrt(1 - c * c)
        q.append([e, e * s * math.cos(phi), e * s * math.sin(phi), e * c])
    total = [sum(v[i] for v in q) for i in range(4)]
    mass = math.sqrt(total[0] ** 2 - total[1] ** 2 - total[2] ** 2 - total[3] ** 2)
    b = [-total[i] / mass for i in (1, 2, 3)]
    gamma = total[0] / mass
    a = 1 / (1 + gamma)
    x = energy / mass
    out = []
    for v in q:
        bq = b[0] * v[1] + b[1] * v[2] + b[2] * v[3]
        e = x * (gamma * v[0] + bq)
        out.append([e] + [x * (v[i + 1] + b[i] * v[0] + a * bq * b[i]) for i in range(3)])
    return out


def rambo(masses, energy, rng):
    """Massive RAMBO (Kleiss, Stirling, Ellis): rescale massless momenta."""
    p = rambo_massless(len(masses), energy, rng)
    if not any(masses):
        return p
    xi = math.sqrt(1 - (sum(masses) / energy) ** 2)
    for _ in range(100):
        f = sum(math.sqrt(m * m + xi * xi * v[0] ** 2) for m, v in zip(masses, p)) - energy
        df = sum(xi * v[0] ** 2 / math.sqrt(m * m + xi * xi * v[0] ** 2) for m, v in zip(masses, p))
        step = f / df
        xi -= step
        if abs(step) < 1e-16:
            break
    return [[math.sqrt(m * m + xi * xi * v[0] ** 2)] + [xi * c for c in v[1:]] for m, v in zip(masses, p)]


def pt(v):
    return math.hypot(v[1], v[2])


def eta_phi(v):
    p = math.sqrt(v[1] ** 2 + v[2] ** 2 + v[3] ** 2)
    return 0.5 * math.log((p + v[3]) / (p - v[3])), math.atan2(v[2], v[1])


def passes(final, kinds):
    gluons = [v for v, k in zip(final, kinds) if k == "g"]
    if any(pt(v) < PT_MIN for v in gluons):
        return False
    for i in range(len(gluons)):
        for j in range(i + 1, len(gluons)):
            (ei, pi), (ej, pj) = eta_phi(gluons[i]), eta_phi(gluons[j])
            dphi = abs(pi - pj)
            dphi = min(dphi, 2 * math.pi - dphi)
            if math.hypot(ei - ej, dphi) < DR_MIN:
                return False
    return True


def point(kinds, rng):
    masses = [MH if k == "H" else 0.0 for k in kinds]
    while True:
        final = rambo(masses, SQRT_S, rng)
        if passes(final, kinds):
            break
    half = SQRT_S / 2
    incoming = [[half, 0.0, 0.0, half], [half, 0.0, 0.0, -half]]
    legs = incoming + [[-c for c in v] for v in final]
    shifts, running = [], [0.0] * 4
    for leg in legs[:-1]:
        shifts.append(list(running))
        running = [a + b for a, b in zip(running, leg)]
    shifts.append(list(running))
    return shifts[: len(legs)]


def main():
    rng = random.Random(SEED)
    out = {"seed": SEED, "sqrt_s": SQRT_S, "mt2": MT2, "mh": MH, "mu": MU, "pt_min": PT_MIN, "dr_min": DR_MIN,
           "integrals": []}
    for ident, label, kinds, rank, count in INTEGRALS:
        n = 2 + len(kinds)
        points = [point(kinds, rng) for _ in range(count)]
        out["integrals"].append({"id": ident, "label": label, "n": n, "rank": rank, "final_state": kinds,
                                 "masses_squared": [MT2] * n, "mu": MU, "points": points})
    with open(sys.argv[1], "w") as sink:
        json.dump(out, sink)
        sink.write("\n")


if __name__ == "__main__":
    main()
