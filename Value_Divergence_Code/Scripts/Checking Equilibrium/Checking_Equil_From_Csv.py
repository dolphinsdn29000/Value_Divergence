#!/usr/bin/env python3
# -*- coding: utf-8 -*-



"""
My words: This takes the csv we generate from "calling_equil_finder) and checks for each paramter...whether it a local best response (a nash in equilbrium)


Batch checker: read a CSV of parameters + efforts and test each row for LOCAL Nash equilibrium
in the Two-Task Cobb–Douglas Team game.

Input CSV (must have these headers):
  a1,a2,c1,c2,p1x,p1y,p2x,p2y,x1,y1,x2,y2   [order doesn't matter]

Output CSV (same columns + 3 booleans):
  a1,a2,c1,c2,p1x,p1y,p2x,p2y,x1,y1,x2,y2,IsBR_P1,IsBR_P2,IsLocalNash

Paths (NO BLANKS):
  Input : /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_quota_min.csv
  Output: /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_quota_min_checked.csv
"""

import csv
import math
import os
from typing import Dict, Tuple, List

# ------------ CONFIG (edit if you want different files or step/tol) ------------
INPUT_CSV  = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_quota_min.csv"
OUTPUT_CSV = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_quota_min_checked.csv"

# Local-search step and tolerance:
DELTA = 1e-4       # size of +/- step on each own variable for the BR check
TOL   = 1e-10      # treat |ΔU| ≤ TOL as "no change"
# -----------------------------------------------------------------------------

# Required columns
REQUIRED_COLS = ["a1","a2","c1","c2","p1x","p1y","p2x","p2y","x1","y1","x2","y2"]

def parse_row(row: Dict[str, str]) -> Dict[str, float]:
    """Convert required fields to float."""
    vals = {}
    for k in REQUIRED_COLS:
        if k not in row:
            raise KeyError(f"Missing required column '{k}' in input CSV.")
        vals[k] = float(row[k])
    return vals

def U1(vals: Dict[str, float]) -> float:
    """Player 1 utility for the Cobb–Douglas team game."""
    X = vals["p1x"]*vals["x1"] + vals["p2x"]*vals["x2"]
    Y = vals["p1y"]*vals["y1"] + vals["p2y"]*vals["y2"]
    a1, c1 = vals["a1"], vals["c1"]
    if X <= 0.0 or Y <= 0.0:
        # outside the log-domain-like power domain; treat as -inf so it won't be profitable
        return -float("inf")
    return (X ** (1.0 - a1)) * (Y ** a1) - 0.5 * c1 * (vals["x1"] + vals["y1"])**2

def U2(vals: Dict[str, float]) -> float:
    """Player 2 utility for the Cobb–Douglas team game."""
    X = vals["p1x"]*vals["x1"] + vals["p2x"]*vals["x2"]
    Y = vals["p1y"]*vals["y1"] + vals["p2y"]*vals["y2"]
    a2, c2 = vals["a2"], vals["c2"]
    if X <= 0.0 or Y <= 0.0:
        return -float("inf")
    return (X ** (1.0 - a2)) * (Y ** a2) - 0.5 * c2 * (vals["x2"] + vals["y2"])**2

def all_step_combinations(n: int):
    """Yield all non-zero vectors in {-1,0,+1}^n (exclude the all-zero vector)."""
    steps = [-1, 0, +1]
    if n == 1:
        for s0 in steps:
            if s0 != 0:
                yield (s0,)
        return
    for s0 in steps:
        for s1 in steps:
            if n == 2:
                if (s0, s1) != (0, 0):
                    yield (s0, s1)
            else:
                raise ValueError("This checker expects exactly 2 own variables per player.")

def apply_steps(base: Dict[str, float], var_names: List[str], steps: Tuple[int, int], delta: float) -> Dict[str, float]:
    """Return a new dict where 'var_names' have been shifted by steps * delta."""
    new_vals = dict(base)
    for name, s in zip(var_names, steps):
        new_vals[name] = base[name] + delta * float(s)
    return new_vals

def check_local_best_response(u_func, base_vals: Dict[str, float], own_vars: List[str],
                              delta: float, tol: float) -> bool:
    """
    Local BR: no move in {-1,0,+1}^k \ {0,...,0} on OWN variables alone yields ΔU > tol,
    with feasibility enforced: x_i, y_i >= 0. Opponent variables are held fixed.
    """
    U0 = u_func(base_vals)

    for steps in all_step_combinations(len(own_vars)):
        # candidate move
        moved = apply_steps(base_vals, own_vars, steps, delta)

        # --- ENFORCE FEASIBILITY: own variables cannot go negative ---
        feasible = True
        for name in own_vars:
            if moved[name] < -1e-15:  # genuinely negative -> infeasible
                feasible = False
                break
            if moved[name] < 0.0:     # tiny negative from FP -> clamp to 0
                moved[name] = 0.0
        if not feasible:
            continue  # skip this move entirely

        # evaluate improvement
        U_new = u_func(moved)
        if (U_new - U0) > tol:
            return False  # found a profitable local deviation

    return True  # no feasible local improvement found


def main() -> None:
    # Ensure output folder exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    kept_rows = 0
    wrote = 0

    with open(INPUT_CSV, "r", newline="", encoding="utf-8") as fin, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        # Validate required columns exist
        for col in REQUIRED_COLS:
            if col not in reader.fieldnames:
                raise KeyError(f"Input CSV missing required column: {col}")

        fieldnames = REQUIRED_COLS + ["IsBR_P1","IsBR_P2","IsLocalNash"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            vals = parse_row(row)

            # Player 1 owns (x1, y1); Player 2 owns (x2, y2)
            is_br_p1 = check_local_best_response(U1, vals, own_vars=["x1","y1"], delta=DELTA, tol=TOL)
            is_br_p2 = check_local_best_response(U2, vals, own_vars=["x2","y2"], delta=DELTA, tol=TOL)
            is_local_nash = is_br_p1 and is_br_p2

            out_row = {
                **{k: vals[k] for k in REQUIRED_COLS},
                "IsBR_P1": "Yes" if is_br_p1 else "No",
                "IsBR_P2": "Yes" if is_br_p2 else "No",
                "IsLocalNash": "Yes" if is_local_nash else "No",
            }
            writer.writerow(out_row)
            wrote += 1

    print("=== Local BR batch check complete ===")
    print(f"Input : {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Rows processed: {wrote}")
    print(f"Step δ = {DELTA}, tolerance = {TOL}")

if __name__ == "__main__":
    main()
