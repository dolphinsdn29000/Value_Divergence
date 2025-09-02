#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compute the a2 in (0,1) that maximizes Player 1's utility by calling
optimize_a2.optimize_a2_for_player1 (your package under /src/optimize_a2).

Package root added to sys.path:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src
"""

import sys
from pathlib import Path

# --- Make sure the /src package root is importable ---
SRC_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# --- Import from your package (try __init__ export first, then module file) ---
try:
    from optimize_a2 import optimize_a2_for_player1, OptimizationResult  # type: ignore
except Exception:
    from optimize_a2.optimize_a2 import optimize_a2_for_player1, OptimizationResult  # type: ignore


def main() -> None:
    # ---- Example parameter configuration ----
    a1  = 0.50
    p1x = 1.00
    p1y = 1.00
    p2x = 1.00
    p2y = 1.00
    c1  = 1.00
    c2  = 1.00

    # ---- Optimize a2 (this calls your canonical solver internally each trial) ----
    res = optimize_a2_for_player1(
        a1=a1,
        p1x=p1x, p1y=p1y,
        p2x=p2x, p2y=p2y,
        c1=c1, c2=c2,
        a2_lo=1e-6, a2_hi=1.0-1e-6,   # a2 ∈ (0,1)
        tol=1e-5, max_iter=200,
        solver_tol=1e-10, solver_verbose=False,
    )

    # ---- Print results ----
    print("=== Optimize a2 for Player 1 ===")
    # Some package versions expose 'solver_source'; guard with hasattr
    if hasattr(res, "solver_source"):
        print(f"Solver source: {getattr(res, 'solver_source')}")
    print(f"Best a2:      {res.best_a2:.6f}")
    print(f"U1 at best:   {res.u1_at_best:.8f}")
    if hasattr(res, "chosen_mask"):
        print(f"Chosen mask:  {getattr(res, 'chosen_mask')}")

    # If you want to see a few sampled points from the search, uncomment:
    # for (a2, u1, mask) in getattr(res, "samples", [])[:10]:
    #     print(f"a2={a2:.6f}, U1={u1:.8f}, mask={mask}")

if __name__ == "__main__":
    main()
