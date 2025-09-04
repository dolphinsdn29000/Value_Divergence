#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Overlay a1 -> a2*(a1) while holding ABSOLUTE strength fixed and letting COMPARATIVE advantage r2
span both sides (Y-adv -> balanced -> X-adv) in a single figure.

Fixed: p1=(1,1), c=(1,1).
Absolute strength "S" is held fixed under one of:
  MODE="gm":  p2x = S*sqrt(r2),  p2y = S/sqrt(r2)   (fix product p2x*p2y = S^2)
  MODE="l1":  p2x = 2S*r2/(1+r2), p2y = 2S/(1+r2)  (fix sum p2x+p2y = 2S)

Curves: r2_list below (edit as you like).
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# ---- project paths ----
SRC_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src")
OUT_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# prefer grid optimizer for speed if available
from optimize_a2 import optimize_a2_for_player1 as opt_robust  # type: ignore
try:
    from optimize_a2 import optimize_a2_for_player1_grid as opt_grid  # type: ignore
except Exception:
    opt_grid = None

# ---- fixed player-1 & costs ----
P1X = 1.0; P1Y = 1.0
C1  = 1.0; C2  = 1.0

# ---- a1 grid (keep modest for speed; increase if you want) ----
A1_GRID = np.linspace(0.001, 0.999, 101)

# ---- absolute-strength definition ----
MODE = "gm"   # "gm" (product fixed) or "l1" (sum fixed)
S    = 1.0    # absolute level to hold fixed

def p2_from(r2: float, mode: str, S: float) -> tuple[float, float]:
    if mode == "gm":
        return (S * (r2**0.5), S / (r2**0.5))           # p2x*p2y = S^2
    elif mode == "l1":
        return (2*S * r2/(1+r2), 2*S * 1/(1+r2))        # p2x+p2y = 2S
    else:
        raise ValueError("MODE must be 'gm' or 'l1'")

def a2_star(a1: float, p2x: float, p2y: float) -> float:
    if opt_grid is not None:
        res = opt_grid(
            a1=a1, p1x=P1X, p1y=P1Y, p2x=p2x, p2y=p2y, c1=C1, c2=C2,
            a2_lo=1e-6, a2_hi=1-1e-6, n=201, solver_tol=1e-10, solver_verbose=False,
        )
    else:
        res = opt_robust(
            a1=a1, p1x=P1X, p1y=P1Y, p2x=p2x, p2y=p2y, c1=C1, c2=C2,
            a2_lo=1e-6, a2_hi=1-1e-6, tol=1e-5, max_iter=200,
            solver_tol=1e-10, solver_verbose=False,
        )
    return float(res.best_a2)

def main():
    # r2 list spans Y-adv (<1), balanced (=1), X-adv (>1)
    r2_list = [0.3333333333, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]  # edit freely

    plt.figure()
    for r2 in r2_list:
        p2x, p2y = p2_from(r2, MODE, S)
        ys = [a2_star(a1, p2x, p2y) for a1 in A1_GRID]
        plt.plot(A1_GRID, ys, label=f"r2={r2:g}  (p2x={p2x:g}, p2y={p2y:g})")

    mode_text = "GM fixed (p2x·p2y=S^2)" if MODE=="gm" else "L1 fixed (p2x+p2y=2S)"
    plt.xlabel("a1")
    plt.ylabel("a2*(a1)")
    plt.title(f"a1 vs a2*(a1) | Opponent comparative advantage across both sides\n"
              f"p1=(1,1), c=(1,1); {mode_text}, S={S:g}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_png = OUT_DIR / f"overlay_ratio_across_both__{MODE}_S-{S:g}.png"
    plt.savefig(out_png, dpi=200)
    plt.close()
    print("Saved:", out_png)

if __name__ == "__main__":
    main()
