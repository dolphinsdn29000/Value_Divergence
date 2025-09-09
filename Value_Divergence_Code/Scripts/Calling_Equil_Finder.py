#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My words: This allows you to input parameters and it will output equilbirums. This is for single set of paramteter values


Simple runner: NO CLI FLAGS, NO JSON.
Edits happen here in PARAMS. Then click Run.

Solvere lives at:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/Equil_finder/Finding_Equilibrium_1.py
"""

import sys
from typing import Dict, Any

# --- Make src importable (NO BLANK PATHS) ---
SRC_DIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src"
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- Import the solver ---
from Equil_finder.Finding_Equilibrium_1 import solve_two_task_cobb_douglas_equilibrium  # noqa: E402

# ======= EDIT THESE NUMBERS TO TRY DIFFERENT PARAMETER VECTORS =======
PARAMS = {
    "a1": 0.45, "a2": 0.55,
    "c1": 1.0,  "c2": 1.2,
    "p1x": 1.0, "p1y": 1.1,
    "p2x": 0.9, "p2y": 1.3
}
# =====================================================================

def pretty_print_solution(sol: Dict[str, Any]) -> None:
    mask = sol.get("mask")
    print("=" * 72)
    print(f" Mask: {mask}")
    print("-" * 72)
    if "r" in sol and sol["r"] is not None:
        print(f" r (Y/X): {sol['r']:.12g}")
    if "XY" in sol:
        XY = sol["XY"]
        print(f" X: {XY.get('X', float('nan')):.12g}   "
              f"Y: {XY.get('Y', float('nan')):.12g}   "
              f"Y/X (recomputed): {XY.get('ratio', float('nan')):.12g}")
    print(" Efforts:")
    print(f"   x1 = {sol.get('x1', float('nan')):.12g}   y1 = {sol.get('y1', float('nan')):.12g}")
    print(f"   x2 = {sol.get('x2', float('nan')):.12g}   y2 = {sol.get('y2', float('nan')):.12g}")
    if "totals" in sol:
        print(" Totals:")
        print(f"   s1 = {sol['totals'].get('s1', float('nan')):.12g}   "
              f"s2 = {sol['totals'].get('s2', float('nan')):.12g}")
    if "diagnostics" in sol and "checks" in sol["diagnostics"]:
        checks = sol["diagnostics"]["checks"]
        print(" Checks:")
        if "ratio_identity_abs_error" in checks:
            print(f"   |(Y/X) - r| = {checks['ratio_identity_abs_error']:.3e}")
        af = checks.get("active_foc_residuals", {})
        if af:
            print("   Active FOC residuals (≈ 0 expected):")
            for k, v in af.items():
                print(f"     {k:>3s}: {v:.3e}")
        ik = checks.get("inactive_kkt_margins", {})
        if ik:
            print("   Inactive KKT margins (≤ 0 expected):")
            for k, v in ik.items():
                print(f"     {k:>3s}: {v:.3e}")
    print("=" * 72)

def main() -> None:
    print("=== Input Parameters (from PARAMS dict) ===")
    for k in ["a1","a2","c1","c2","p1x","p1y","p2x","p2y"]:
        print(f" {k:>3s} = {PARAMS[k]}")
    res = solve_two_task_cobb_douglas_equilibrium(
        PARAMS["a1"], PARAMS["a2"], PARAMS["c1"], PARAMS["c2"],
        PARAMS["p1x"], PARAMS["p1y"], PARAMS["p2x"], PARAMS["p2y"],
        tol=1e-10, verbose=True
    )
    print("\n=== Solver Output ===")
    if res.get("multiple_matches", False):
        print(f"Multiple matches detected: {res.get('masks', [])}")
        for m, sol in res.get("solutions_by_mask", {}).items():
            print(f"\n>>> Mask {m}")
            pretty_print_solution(sol)
    elif res.get("mask") is not None:
        pretty_print_solution(res)
    else:
        print("No feasible mask under the PDF inequalities.")
        for cand in res.get("candidates", []):
            print(f"  Mask {cand['mask']:>3s}: passed={cand['passed']}, margins={cand.get('margins')}")

if __name__ == "__main__":
    main()
