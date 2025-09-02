#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My words: This generates a bunch of random paramater values and that calls the FInding_Equibirum_1 to geenrate paramter values)

Minimal batch runner: guarantees ≥5 examples of every mask, then random remainder.
CSV columns: parameters, efforts (x1,y1,x2,y2), MultipleMatches (Yes/No).

Solver:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/Equil_finder/Finding_Equilibrium_1.py

Output:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_quota_min.csv
"""

import sys
import os
import csv
import random
from typing import Dict, Any, List, Tuple

# ---------------- config ----------------
N_TOTAL: int = 100
MIN_PER_MASK: int = 5
RANDOM_SEED: int = 424242
OUTPUT_CSV: str = (
    "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/"
    "Value_Divergence_Code/outputs/random_equilibria_quota_min.csv"
)
MAX_TRIES_PER_TARGET: int = 200000

# Parameter bounds
BOUNDS: Dict[str, Tuple[float, float]] = {
    "a1":  (0.05, 0.95),
    "a2":  (0.05, 0.95),
    "c1":  (0.50, 2.00),
    "c2":  (0.50, 2.00),
    "p1x": (0.50, 2.00),
    "p1y": (0.50, 2.00),
    "p2x": (0.50, 2.00),
    "p2y": (0.50, 2.00),
}
# ---------------------------------------

# Make src importable (NO BLANK PATHS)
SRC_DIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src"
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from Equil_finder.Finding_Equilibrium_1 import solve_two_task_cobb_douglas_equilibrium  # noqa: E402

MASKS = ["B,X", "X,B", "B,Y", "Y,B", "X,Y", "Y,X", "B,B"]

def _uniform(lo: float, hi: float) -> float:
    eps = 1e-12
    return random.uniform(lo + eps, hi - eps)

def draw_params() -> Dict[str, float]:
    return {k: _uniform(*BOUNDS[k]) for k in ["a1","a2","c1","c2","p1x","p1y","p2x","p2y"]}

def construct_params_BB() -> Dict[str, float]:
    """
    Construct parameters satisfying r1 == r2 to hit (B,B).
    r1 = (a1 p1y)/((1-a1) p1x), r2 = (a2 p2y)/((1-a2) p2x)
    Choose a1,a2,c1,c2,p1x,p1y,p2x; then set p2y so r2 == r1.
    Verify via solver; retry if out of bounds or not (B,B).
    """
    lo, hi = BOUNDS["p2y"]
    for _ in range(50000):
        a1 = _uniform(*BOUNDS["a1"])
        a2 = _uniform(*BOUNDS["a2"])
        c1 = _uniform(*BOUNDS["c1"])
        c2 = _uniform(*BOUNDS["c2"])
        p1x = _uniform(*BOUNDS["p1x"])
        p1y = _uniform(*BOUNDS["p1y"])
        p2x = _uniform(*BOUNDS["p2x"])
        r1 = (a1 * p1y) / ((1.0 - a1) * p1x)
        p2y = ((1.0 - a2) * p2x / a2) * r1
        if not (lo < p2y < hi):
            continue
        params = {"a1":a1,"a2":a2,"c1":c1,"c2":c2,"p1x":p1x,"p1y":p1y,"p2x":p2x,"p2y":p2y}
        res = solve_two_task_cobb_douglas_equilibrium(a1,a2,c1,c2,p1x,p1y,p2x,p2y,tol=1e-10,verbose=False)
        if res.get("multiple_matches", False):
            if "B,B" in res.get("masks", []):
                return params
        elif res.get("mask") == "B,B":
            return params
    raise RuntimeError("Could not construct (B,B) within attempts.")

def produced_masks(res: Dict[str, Any]) -> List[str]:
    if res.get("multiple_matches", False):
        return list(res.get("masks", []))
    if res.get("mask") is not None:
        return [res["mask"]]
    return []

def primary_efforts(res: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """Pick efforts to record. If multiple, choose first mask in sorted order for determinism."""
    if res.get("multiple_matches", False):
        masks = sorted(res.get("masks", []))
        sol = res.get("solutions_by_mask", {}).get(masks[0], {})
        return float(sol.get("x1", float("nan"))), float(sol.get("y1", float("nan"))), \
               float(sol.get("x2", float("nan"))), float(sol.get("y2", float("nan")))
    # single
    return float(res.get("x1", float("nan"))), float(res.get("y1", float("nan"))), \
           float(res.get("x2", float("nan"))), float(res.get("y2", float("nan")))

def row_from_res(params: Dict[str, float], res: Dict[str, Any]) -> List[Any]:
    x1,y1,x2,y2 = primary_efforts(res)
    mm = "Yes" if res.get("multiple_matches", False) else "No"
    return [
        params["a1"], params["a2"], params["c1"], params["c2"],
        params["p1x"], params["p1y"], params["p2x"], params["p2y"],
        x1, y1, x2, y2, mm
    ]

def main() -> None:
    random.seed(RANDOM_SEED)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    header = [
        "a1","a2","c1","c2","p1x","p1y","p2x","p2y",
        "x1","y1","x2","y2","MultipleMatches"
    ]

    rows: List[List[Any]] = []
    counts: Dict[str, int] = {m: 0 for m in MASKS}

    # Stage 1: meet quotas for each mask
    for target in MASKS:
        needed = max(0, MIN_PER_MASK - counts[target])
        tries = 0
        while needed > 0 and tries < MAX_TRIES_PER_TARGET:
            tries += 1
            params = construct_params_BB() if target == "B,B" else draw_params()
            res = solve_two_task_cobb_douglas_equilibrium(
                params["a1"], params["a2"], params["c1"], params["c2"],
                params["p1x"], params["p1y"], params["p2x"], params["p2y"],
                tol=1e-10, verbose=False
            )
            masks = produced_masks(res)
            if target in masks:
                rows.append(row_from_res(params, res))
                # credit all masks that appeared in this row up to quota
                for m in masks:
                    if m in counts and counts[m] < MIN_PER_MASK:
                        counts[m] += 1
                needed = max(0, MIN_PER_MASK - counts[target])
        if needed > 0:
            raise RuntimeError(f"Failed to meet quota for mask {target} in {tries} tries.")

    # Stage 2: random remainder until N_TOTAL rows
    while len(rows) < N_TOTAL:
        params = draw_params()
        res = solve_two_task_cobb_douglas_equilibrium(
            params["a1"], params["a2"], params["c1"], params["c2"],
            params["p1x"], params["p1y"], params["p2x"], params["p2y"],
            tol=1e-10, verbose=False
        )
        # ignore totally infeasible (should be rare)
        if (not res.get("multiple_matches", False)) and (res.get("mask") is None):
            continue
        rows.append(row_from_res(params, res))

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    # Print a tiny summary to console
    print(f"Wrote {len(rows)} rows to:\n  {OUTPUT_CSV}")
    print(f"Quotas satisfied (≥{MIN_PER_MASK} each). Remainder random. Seed={RANDOM_SEED}")

if __name__ == "__main__":
    main()

