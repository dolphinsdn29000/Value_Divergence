#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Overlay_a1_vs_a2star_by_scale.py

Goal:
  Make two overlay visuals of a1 -> a2*(a1) while keeping comparative advantage fixed
  and varying ONLY the opponent's absolute strength (5 curves, distinct colors).

  Panel A: Opponent relatively better at X (r2 > 1), scales S = {0.5, 0.75, 1.0, 1.5, 2.0}
  Panel B: Opponent relatively better at Y (r2 < 1), same scales

Fixed:
  p1x = 1, p1y = 1, c1 = 1, c2 = 1

Notes:
  - We import your optimizer from:
      /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/optimize_a2/optimize_a2.py
  - If 'optimize_a2_for_player1_grid' exists, we use it with n=301 (faster).
    Otherwise we call 'optimize_a2_for_player1' (your robust version).
  - Outputs are saved under:
      /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs
"""

import sys
from pathlib import Path
import math
import matplotlib.pyplot as plt
import numpy as np

# ---------- Absolute, project-specific paths ----------
SRC_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src")
OUT_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ---------- Import optimizer (prefer grid if available; else robust) ----------
from optimize_a2 import optimize_a2_for_player1 as opt_robust  # type: ignore
# Optional speed-up: if present, use brute-force grid with small n
try:
    from optimize_a2 import optimize_a2_for_player1_grid as opt_grid  # type: ignore
except Exception:
    opt_grid = None

def a2_star(a1: float, p1x: float, p1y: float, p2x: float, p2y: float,
            c1: float = 1.0, c2: float = 1.0) -> float:
    """Return a2* maximizing U1 at given a1 and productivities, calling your canonical solver inside."""
    if opt_grid is not None:
        res = opt_grid(
            a1=a1, p1x=p1x, p1y=p1y, p2x=p2x, p2y=p2y, c1=c1, c2=c2,
            a2_lo=1e-6, a2_hi=1.0-1e-6, n=301,  # dense enough, much faster than huge coarse scans
            solver_tol=1e-10, solver_verbose=False,
        )
    else:
        res = opt_robust(
            a1=a1, p1x=p1x, p1y=p1y, p2x=p2x, p2y=p2y, c1=c1, c2=c2,
            a2_lo=1e-6, a2_hi=1.0-1e-6, tol=1e-5, max_iter=200,
            solver_tol=1e-10, solver_verbose=False,
        )
    return float(res.best_a2)

# ---------- Fixed player-1 and costs ----------
P1X, P1Y = 1.0, 1.0
C1, C2   = 1.0, 1.0

# ---------- a1 grid (kept modest for speed; increase if you want smoother curves) ----------
A1_GRID = np.linspace(0.001, 0.999, 121)  # 121 points ~ fast but clear

# ---------- Five absolute-strength levels (scales) ----------
SCALES = [0.5, 0.75, 1.0, 1.5, 2.0]  # 5 curves

# ---------- Helper to compute and plot one overlay ----------
def overlay_for_fixed_ratio(r2: float, tag: str):
    """
    Keep comparative advantage fixed at r2 = p2x/p2y.
    For each absolute scale s in SCALES, set p2 = s * (r2, 1) and overlay a2*(a1) curve.
    """
    plt.figure()
    for s in SCALES:
        p2x = s * r2
        p2y = s * 1.0

        # compute curve
        ys = []
        for a1 in A1_GRID:
            ys.append(a2_star(a1, P1X, P1Y, p2x, p2y, C1, C2))

        label = f"s={s:g}  (p2x={p2x:g}, p2y={p2y:g})"
        plt.plot(A1_GRID, ys, label=label)  # default colors cycle; distinct across five curves

    adv = "X-advantage" if r2 > 1.0 else ("Y-advantage" if r2 < 1.0 else "balanced")
    plt.xlabel("a1")
    plt.ylabel("a2*(a1)")
    plt.title(f"Overlay: a1 vs a2*(a1) | Opponent {adv} (r2={r2:g}), p1=(1,1), c=(1,1)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save with parameters in filename
    out_png = OUT_DIR / f"overlay_a1_vs_a2star__{tag}__r2-{r2:g}__p1x-1_p1y-1.png"
    plt.savefig(str(out_png), dpi=200)
    plt.close()
    print("Saved:", out_png)

def main():
    # Panel A: Opponent relatively better at X (fix r2>1)
    R2_X = 2.0    # choose a clear X-advantage
    overlay_for_fixed_ratio(R2_X, tag="Xadv")

    # Panel B: Opponent relatively better at Y (fix r2<1)
    R2_Y = 0.5    # choose a clear Y-advantage
    overlay_for_fixed_ratio(R2_Y, tag="Yadv")

if __name__ == "__main__":
    main()
