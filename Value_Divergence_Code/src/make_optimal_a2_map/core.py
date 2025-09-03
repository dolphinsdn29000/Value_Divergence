# -*- coding: utf-8 -*-
"""
Grid sweep over productivities (comparative advantage) to test the "opposites attract" pattern.

We *strictly* import the optimizer from the exact file:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/optimize_a2/optimize_a2.py

Outputs:
- summary dataframe (r1, r2, frac_match, mean_signed_gap, n_valid, n_a1), optionally raw (a1, a2*).
- PNG heatmaps for frac_match and mean_signed_gap.
"""

from __future__ import annotations
import os
import math
import csv
from typing import Dict, List, Tuple

# ---------- FIXED PATHS ----------
SRC_DIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src"
OPT_QNAME = "optimize_a2.optimize_a2"
OPT_EXPECTED_FILE = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/optimize_a2/optimize_a2.py"

DEFAULT_OUTDIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/outputs"
SUMMARY_CSV = os.path.join(DEFAULT_OUTDIR, "opposites_attract_grid_summary.csv")
RAW_CSV     = os.path.join(DEFAULT_OUTDIR, "opposites_attract_grid_raw.csv")
PNG_FRAC    = os.path.join(DEFAULT_OUTDIR, "opposites_attract_fraction_heatmap.png")
PNG_GAP     = os.path.join(DEFAULT_OUTDIR, "opposites_attract_signed_gap_heatmap.png")


def _import_optimizer_strict():
    import sys, os, importlib
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    mod = importlib.import_module(OPT_QNAME)
    mod_file = getattr(mod, "__file__", None)
    if not mod_file or not os.path.exists(mod_file) or not os.path.exists(OPT_EXPECTED_FILE):
        raise ImportError(f"Could not verify optimizer module file. Got: {mod_file!r}; expected: {OPT_EXPECTED_FILE}")
    if not os.path.samefile(mod_file, OPT_EXPECTED_FILE):
        raise ImportError(f"Imported optimizer from {mod_file}, expected {OPT_EXPECTED_FILE}")
    if not hasattr(mod, "optimize_a2_for_player1"):
        raise ImportError("optimize_a2_for_player1 not found in optimize_a2.optimize_a2")
    return mod.optimize_a2_for_player1, mod_file


def _mrs_a2(a1: float, r1: float, r2: float) -> float:
    # analytic interior benchmark: a2 = (r2 a1)/(r2 a1 + r1(1-a1))
    num = r2 * a1
    den = r2 * a1 + r1 * (1.0 - a1)
    return float(num / den)


def sweep_productivities(
    *,
    r1_min: float = 0.5, r1_max: float = 2.0, r1_steps: int = 16,
    r2_min: float = 0.5, r2_max: float = 2.0, r2_steps: int = 16,
    a1_min: float = 0.01, a1_max: float = 0.99, a1_steps: int = 101,
    # keep costs equal & fixed (per your instruction)
    c: float = 1.0,
    # absolute scales: hold p1y = p2y = 1; p1x = r1; p2x = r2  (pure comparative-advantage sweep)
    scale1: float = 1.0,
    scale2: float = 1.0,
    # optimizer tolerances
    a2_lo: float = 1e-6, a2_hi: float = 1.0 - 1e-6, tol: float = 1e-5, max_iter: int = 200,
    solver_tol: float = 1e-10, solver_verbose: bool = False,
) -> Tuple[List[Dict], List[Dict], str]:
    """
    Returns:
      summary_rows : list of dicts with per-(r1,r2) summary (frac_match, mean_signed_gap, ...)
      raw_rows     : list of dicts with per-(r1,r2,a1) triplets (a2_star, a2_mrs, etc.)
      optimizer_src: the optimizer's file path actually used (sanity check)
    """
    import numpy as np
    opt_fun, opt_src = _import_optimizer_strict()

    r1_grid = np.linspace(r1_min, r1_max, r1_steps)
    r2_grid = np.linspace(r2_min, r2_max, r2_steps)
    a1_grid = np.linspace(a1_min, a1_max, a1_steps)

    summary_rows: List[Dict] = []
    raw_rows: List[Dict] = []

    for r1 in r1_grid:
        for r2 in r2_grid:
            # productivities from (r1,r2), holding p_iy = 1
            p1x = scale1 * r1; p1y = scale1 * 1.0
            p2x = scale2 * r2; p2y = scale2 * 1.0

            sign_target = 0
            if r2 > r1:  # 2 better at X than 1
                sign_target = +1
            elif r2 < r1:
                sign_target = -1

            n_match = 0
            signed_gaps: List[float] = []
            n_valid = 0

            for a1 in a1_grid:
                try:
                    res = opt_fun(
                        a1=float(a1),
                        p1x=float(p1x), p1y=float(p1y),
                        p2x=float(p2x), p2y=float(p2y),
                        c1=float(c), c2=float(c),
                        a2_lo=float(a2_lo), a2_hi=float(a2_hi),
                        tol=float(tol), max_iter=int(max_iter),
                        solver_tol=float(solver_tol), solver_verbose=bool(solver_verbose),
                    )
                    a2_star = float(res.best_a2)
                except Exception:
                    # skip failed points
                    continue

                # classification
                diff = a2_star - a1
                if sign_target != 0:
                    if diff * sign_target > 0.0:
                        n_match += 1
                    signed_gaps.append(diff * sign_target)
                else:
                    # r2 == r1: treat as neutral; signed gap = 0 for averaging
                    signed_gaps.append(0.0)

                n_valid += 1

                raw_rows.append({
                    "r1": float(r1), "r2": float(r2),
                    "a1": float(a1), "a2_star": float(a2_star),
                    # diagnostic: analytic interior baseline
                    "a2_mrs": float(_mrs_a2(a1, r1, r2)),
                    "diff": float(diff),
                    "sign_target": int(sign_target),
                })

            frac_match = (n_match / n_valid) if (n_valid > 0 and sign_target != 0) else float("nan")
            mean_signed_gap = (sum(signed_gaps) / len(signed_gaps)) if signed_gaps else float("nan")

            summary_rows.append({
                "r1": float(r1), "r2": float(r2),
                "ratio_r2_over_r1": float(r2 / r1) if r1 != 0 else float("inf"),
                "n_valid": int(n_valid),
                "n_a1": int(len(a1_grid)),
                "frac_match_opposites": float(frac_match),
                "mean_signed_gap": float(mean_signed_gap),
            })

    return summary_rows, raw_rows, opt_src


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_summary_csv(rows: List[Dict], path: str = SUMMARY_CSV) -> str:
    _ensure_dir(os.path.dirname(path))
    if not rows:
        return path
    keys = ["r1", "r2", "ratio_r2_over_r1", "n_valid", "n_a1", "frac_match_opposites", "mean_signed_gap"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    return path


def save_raw_curves_csv(rows: List[Dict], path: str = RAW_CSV) -> str:
    _ensure_dir(os.path.dirname(path))
    if not rows:
        return path
    keys = ["r1", "r2", "a1", "a2_star", "a2_mrs", "diff", "sign_target"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    return path


def plot_fraction_heatmap(rows: List[Dict], path: str = PNG_FRAC) -> str:
    import numpy as np
    import matplotlib.pyplot as plt

    # pivot to grid by (r1,r2)
    r1_vals = sorted(set(float(r["r1"]) for r in rows))
    r2_vals = sorted(set(float(r["r2"]) for r in rows))
    m = len(r1_vals); n = len(r2_vals)
    Z = np.full((m, n), np.nan)
    for r in rows:
        i = r1_vals.index(float(r["r1"]))
        j = r2_vals.index(float(r["r2"]))
        Z[i, j] = float(r["frac_match_opposites"])

    _ensure_dir(os.path.dirname(path))
    plt.figure()
    plt.imshow(Z, origin="lower", aspect="auto",
               extent=[min(r2_vals), max(r2_vals), min(r1_vals), max(r1_vals)])
    plt.colorbar(label="Fraction matching opposites-attract")
    plt.xlabel("r2 (p2x/p2y)")
    plt.ylabel("r1 (p1x/p1y)")
    plt.title("Opposites-Attract Match Fraction over (r1, r2)")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_signed_gap_heatmap(rows: List[Dict], path: str = PNG_GAP) -> str:
    import numpy as np
    import matplotlib.pyplot as plt

    r1_vals = sorted(set(float(r["r1"]) for r in rows))
    r2_vals = sorted(set(float(r["r2"]) for r in rows))
    m = len(r1_vals); n = len(r2_vals)
    Z = np.full((m, n), np.nan)
    for r in rows:
        i = r1_vals.index(float(r["r1"]))
        j = r2_vals.index(float(r["r2"]))
        Z[i, j] = float(r["mean_signed_gap"])

    _ensure_dir(os.path.dirname(path))
    plt.figure()
    plt.imshow(Z, origin="lower", aspect="auto",
               extent=[min(r2_vals), max(r2_vals), min(r1_vals), max(r1_vals)])
    plt.colorbar(label="Mean signed gap  E[(a2*−a1)·sign(r2−r1)]")
    plt.xlabel("r2 (p2x/p2y)")
    plt.ylabel("r1 (p1x/p1y)")
    plt.title("Signed Gap over (r1, r2)")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    return path
