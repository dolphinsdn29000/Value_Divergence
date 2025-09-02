#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch runner: draws many random parameter vectors and records equilibrium outcomes.

Solver module:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/valued/Finding_Equilibrium_1.py

Output CSV:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs/random_equilibria_100.csv

Behavior:
  - Generates N_SAMPLES random parameter vectors within the BOUNDS below.
  - Calls solve_two_task_cobb_douglas_equilibrium() for each vector.
  - Writes one CSV row per draw with:
      params, mask(s), multiple_masks flag, equilibrium efforts (x1,y1,x2,y2) and r, X, Y,
      whether multiple-mask solutions are identical, and the maximum pairwise effort difference.
  - If multiple masks match, it lists them and summarizes per-mask efforts in a string column.
"""

import sys
import os
import csv
import random
from typing import Dict, Any, List, Tuple

# ---------- EDITABLE SETTINGS (no CLI; just change here and click Run) ----------
N_SAMPLES: int = 100
RANDOM_SEED: int = 12345
OUTPUT_CSV: str = (
    "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/"
    "Value_Divergence_Code/outputs/random_equilibria_100.csv"
)
TOL_COMPARE: float = 1e-9  # for "identical across masks" comparison

# Parameter bounds (open intervals respected by the solver: a_i in (0,1); others > 0)
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
# -------------------------------------------------------------------------------

# Make src importable (NO BLANK PATHS)
SRC_DIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src"
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the solver
from valued.Finding_Equilibrium_1 import solve_two_task_cobb_douglas_equilibrium  # noqa: E402


def _uniform(lo: float, hi: float) -> float:
    """Closed-open safety (never exactly hits endpoints for (0,1) intervals)."""
    # tiny epsilon keeps away from exact endpoints
    eps = 1e-12
    return random.uniform(lo + eps, hi - eps)


def draw_params() -> Dict[str, float]:
    """Draw one parameter vector uniformly from BOUNDS."""
    return {k: _uniform(*BOUNDS[k]) for k in ["a1", "a2", "c1", "c2", "p1x", "p1y", "p2x", "p2y"]}


def efforts_tuple(sol: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """(x1, y1, x2, y2) tuple from a solver solution dict."""
    return (float(sol.get("x1", 0.0)),
            float(sol.get("y1", 0.0)),
            float(sol.get("x2", 0.0)),
            float(sol.get("y2", 0.0)))


def max_pairwise_abs_diff(solutions: List[Dict[str, Any]]) -> float:
    """Max absolute difference across all pairs and all four efforts."""
    mx = 0.0
    for i in range(len(solutions)):
        xi = efforts_tuple(solutions[i])
        for j in range(i + 1, len(solutions)):
            xj = efforts_tuple(solutions[j])
            mx = max(mx, abs(xi[0] - xj[0]), abs(xi[1] - xj[1]),
                          abs(xi[2] - xj[2]), abs(xi[3] - xj[3]))
    return mx


def summarize_solutions_by_mask(sols_by_mask: Dict[str, Dict[str, Any]]) -> str:
    """
    Compact one-line summary listing per-mask efforts.
    Example: "B,X: x1=...,y1=...,x2=...,y2=... | B,B: x1=...,y1=...,x2=...,y2=..."
    """
    parts = []
    for m in sorted(sols_by_mask.keys()):
        s = sols_by_mask[m]
        parts.append(
            f"{m}: x1={s['x1']:.6g}, y1={s['y1']:.6g}, x2={s['x2']:.6g}, y2={s['y2']:.6g}"
        )
    return " | ".join(parts)


def main() -> None:
    # Reproducible randomness
    random.seed(RANDOM_SEED)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # CSV header
    header = [
        "idx",
        # parameters
        "a1", "a2", "c1", "c2", "p1x", "p1y", "p2x", "p2y",
        # mask & flags
        "mask", "multiple_masks", "no_feasible_mask",
        "solutions_identical_across_masks", "max_pairwise_effort_abs_diff",
        # equilibrium (primary / single-mask or first-mask when multiple)
        "x1", "y1", "x2", "y2", "r", "X", "Y",
        # summary string for multiple-mask case
        "solutions_by_mask_summary"
    ]

    rows = []
    mask_counts: Dict[str, int] = {}
    n_multiple = 0
    n_infeasible = 0

    for idx in range(1, N_SAMPLES + 1):
        params = draw_params()

        # Call solver (quiet)
        res = solve_two_task_cobb_douglas_equilibrium(
            params["a1"], params["a2"], params["c1"], params["c2"],
            params["p1x"], params["p1y"], params["p2x"], params["p2y"],
            tol=1e-10, verbose=False
        )

        # Defaults
        multiple_masks = False
        no_feasible = False
        sol_identical = True
        max_diff = 0.0
        mask_label = ""
        x1 = y1 = x2 = y2 = r = X = Y = float("nan")
        sols_summary = ""

        if res.get("multiple_matches", False):
            multiple_masks = True
            n_multiple += 1
            masks = res.get("masks", [])
            # Count each mask occurrence
            for m in masks:
                mask_counts[m] = mask_counts.get(m, 0) + 1
            mask_label = "|".join(masks)

            sols_by_mask = res.get("solutions_by_mask", {})
            sols_list = [sols_by_mask[m] for m in masks if m in sols_by_mask]

            # Are all solutions identical (by efforts)?
            if len(sols_list) >= 2:
                max_diff = max_pairwise_abs_diff(sols_list)
                sol_identical = (max_diff <= TOL_COMPARE)
            else:
                sol_identical = True
                max_diff = 0.0

            # Primary numbers: take the first mask’s values (documented)
            if sols_list:
                first = sols_list[0]
                x1, y1, x2, y2 = first["x1"], first["y1"], first["x2"], first["y2"]
                r = first.get("r", float("nan"))
                X = first.get("XY", {}).get("X", float("nan"))
                Y = first.get("XY", {}).get("Y", float("nan"))

            sols_summary = summarize_solutions_by_mask(sols_by_mask)

        elif res.get("mask") is None:
            # No feasible mask
            no_feasible = True
            n_infeasible += 1
            mask_label = ""
            # We still count candidate "passed" masks = none; nothing to do here.

        else:
            # Single match
            mask_label = res["mask"]
            mask_counts[mask_label] = mask_counts.get(mask_label, 0) + 1
            x1, y1, x2, y2 = res["x1"], res["y1"], res["x2"], res["y2"]
            r = res.get("r", float("nan"))
            X = res.get("XY", {}).get("X", float("nan"))
            Y = res.get("XY", {}).get("Y", float("nan"))

        row = [
            idx,
            params["a1"], params["a2"], params["c1"], params["c2"],
            params["p1x"], params["p1y"], params["p2x"], params["p2y"],
            mask_label, multiple_masks, no_feasible,
            sol_identical, max_diff,
            x1, y1, x2, y2, r, X, Y,
            sols_summary
        ]
        rows.append(row)

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    # Print a quick summary
    print("\n=== Batch complete ===")
    print(f"Samples: {N_SAMPLES}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Multiple-mask cases: {n_multiple}")
    print(f"No-feasible-mask cases: {n_infeasible}")
    print("Mask counts (single and from multiple-mask sets):")
    for m in sorted(mask_counts.keys()):
        print(f"  {m:>4s}: {mask_counts[m]}")
    if n_multiple > 0:
        print(f"Comparison tolerance for 'identical across masks': {TOL_COMPARE:g}")


if __name__ == "__main__":
    main()
