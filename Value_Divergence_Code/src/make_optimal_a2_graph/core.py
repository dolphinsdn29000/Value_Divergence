# -*- coding: utf-8 -*-
"""
Core functions for computing and plotting a1 vs optimal a2.

This package *strictly* imports the optimizer from:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/optimize_a2/optimize_a2.py
and verifies that the imported module file matches that exact path.
"""

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


# ---------- ABSOLUTE PATHS (as requested) ----------
_OPTIMIZER_EXPECTED_FILE = (
    "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/"
    "Value_Divergence_Code/src/optimize_a2/optimize_a2.py"
)
_DEFAULT_OUTPUT_DIR = (
    "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/"
    "Value_Divergence_Code/outputs"
)


def _import_optimizer_strict():
    """
    Import optimize_a2_for_player1 from the optimize_a2 package and assert that the
    module file is exactly _OPTIMIZER_EXPECTED_FILE.

    This uses a normal import (no manual exec) so decorators (e.g., @dataclass) are safe.
    """
    import sys
    import importlib
    import os

    # Ensure /src is on sys.path so sibling package imports resolve
    SRC_DIR = "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src"
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)

    mod = importlib.import_module("optimize_a2.optimize_a2")
    mod_file = getattr(mod, "__file__", None)
    if not mod_file or not os.path.exists(mod_file) or not os.path.exists(_OPTIMIZER_EXPECTED_FILE):
        raise ImportError(
            f"Could not verify optimizer module file. Got: {mod_file!r}; expected: {_OPTIMIZER_EXPECTED_FILE}"
        )

    # Strong check: exact file identity
    if not os.path.samefile(mod_file, _OPTIMIZER_EXPECTED_FILE):
        raise ImportError(f"Imported optimizer from {mod_file}, expected {_OPTIMIZER_EXPECTED_FILE}")

    if not hasattr(mod, "optimize_a2_for_player1"):
        raise ImportError("optimize_a2_for_player1 not found in optimize_a2.optimize_a2")

    return mod.optimize_a2_for_player1, mod_file


# ---------- DATA CONTAINER ----------
@dataclass
class A1A2Point:
    a1: float
    a2_star: float
    u1_at_best: float


# ---------- HELPERS ----------
def make_a1_grid(min_a1: float, max_a1: float, n: int) -> List[float]:
    """
    Build an open-interval grid of a1 values in (min_a1, max_a1).
    No numpy required.

    Preconditions:
      0.0 < min_a1 < max_a1 < 1.0
      n >= 2
    """
    if not (0.0 < min_a1 < max_a1 < 1.0):
        raise ValueError("Require 0.0 < min_a1 < max_a1 < 1.0.")
    if n < 2:
        raise ValueError("Require n >= 2.")
    step = (max_a1 - min_a1) / (n - 1)
    return [min_a1 + i * step for i in range(n)]


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _save_csv(points: Sequence[A1A2Point], csv_path: str) -> None:
    _ensure_dir(os.path.dirname(csv_path))
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["a1", "a2_star", "U1_at_best"])
        for pt in points:
            w.writerow([f"{pt.a1:.10f}", f"{pt.a2_star:.10f}", f"{pt.u1_at_best:.10f}"])


def _fmt_val(v: float) -> str:
    """Compact float formatting for filenames/titles (e.g., 0.333333 -> '0.333333')."""
    return f"{float(v):.6g}"


def _param_tag(p1x: float, p1y: float, p2x: float, p2y: float) -> str:
    """
    Build a safe, compact tag for filenames.
    Example: 'p1x-1_p1y-1_p2x-2_p2y-1' (with up to 6 significant digits).
    """
    return (
        f"p1x-{_fmt_val(p1x)}_"
        f"p1y-{_fmt_val(p1y)}_"
        f"p2x-{_fmt_val(p2x)}_"
        f"p2y-{_fmt_val(p2y)}"
    )


def _title_suffix(p1x: float, p1y: float, p2x: float, p2y: float) -> str:
    """
    Human-readable parameter suffix for the plot title.
    Example: 'p1x=1, p1y=1, p2x=2, p2y=1'
    """
    return (
        f"p1x={_fmt_val(p1x)}, p1y={_fmt_val(p1y)}, "
        f"p2x={_fmt_val(p2x)}, p2y={_fmt_val(p2y)}"
    )


# ---------- CORE ----------
def compute_a1_vs_opt_a2(
    *,
    p1x: float,
    p1y: float,
    p2x: float,
    p2y: float,
    c1: float,
    c2: float,
    a1_values: Iterable[float],
    a2_lo: float = 1e-6,
    a2_hi: float = 1.0 - 1e-6,
    tol: float = 1e-5,
    max_iter: int = 200,
    solver_tol: float = 1e-10,
    solver_verbose: bool = False,
) -> Tuple[List[A1A2Point], str]:
    """
    For each a1 in the provided grid (strictly inside (0,1)), call optimize_a2_for_player1(...)
    and record a2* and U1(best).

    Returns (points, optimizer_source_file)
    """
    # Import the optimizer (and verify its source file)
    optimize_a2_for_player1, optimizer_src = _import_optimizer_strict()

    points: List[A1A2Point] = []
    for a1 in a1_values:
        a1f = float(a1)
        if not (0.0 < a1f < 1.0):
            # Skip any endpoints or invalid a1
            continue

        res = optimize_a2_for_player1(
            a1=a1f,
            p1x=float(p1x), p1y=float(p1y),
            p2x=float(p2x), p2y=float(p2y),
            c1=float(c1), c2=float(c2),
            a2_lo=float(a2_lo), a2_hi=float(a2_hi),
            tol=float(tol), max_iter=int(max_iter),
            solver_tol=float(solver_tol), solver_verbose=bool(solver_verbose),
        )
        points.append(A1A2Point(a1=a1f, a2_star=float(res.best_a2), u1_at_best=float(res.u1_at_best)))

    return points, optimizer_src


def plot_and_save(
    points: Sequence[A1A2Point],
    png_path: str,
    *,
    p1x: float,
    p1y: float,
    p2x: float,
    p2y: float,
) -> None:
    """
    One matplotlib figure; no seaborn; no explicit colors; no subplots.
    The plot *title* includes the p-parameters, and the *filename* is handled upstream.
    """
    import matplotlib.pyplot as plt

    _ensure_dir(os.path.dirname(png_path))
    xs = [pt.a1 for pt in points]
    ys = [pt.a2_star for pt in points]

    plt.figure()
    plt.plot(xs, ys, marker="o", linestyle="-")
    plt.xlabel("a1")
    plt.ylabel("optimal a2 (a2*)")
    plt.title(f"a1 vs optimal a2  |  {_title_suffix(p1x, p1y, p2x, p2y)}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(png_path, dpi=200)
    plt.close()


def run_and_save(
    *,
    p1x: float,
    p1y: float,
    p2x: float,
    p2y: float,
    c1: float,
    c2: float,
    min_a1: float = 0.001,
    max_a1: float = 0.999,
    n_points: int = 999,
    a2_lo: float = 1e-6,
    a2_hi: float = 1.0 - 1e-6,
    tol: float = 1e-5,
    max_iter: int = 200,
    solver_tol: float = 1e-10,
    solver_verbose: bool = False,
    output_dir: str = _DEFAULT_OUTPUT_DIR,
    csv_name: str = "a1_vs_opt_a2.csv",
    png_name: str = "a1_vs_opt_a2.png",
) -> Tuple[str, str, str]:
    """
    Convenience wrapper:
      1) builds a1 grid,
      2) computes points,
      3) writes CSV + PNG.

    The PNG filename is automatically suffixed with the p-parameters:
      a1_vs_opt_a2__p1x-<..>_p1y-<..>_p2x-<..>_p2y-<..>.png

    Returns (optimizer_source_file, csv_path, png_path).
    """
    grid = make_a1_grid(min_a1=min_a1, max_a1=max_a1, n=n_points)
    points, optimizer_src = compute_a1_vs_opt_a2(
        p1x=p1x, p1y=p1y, p2x=p2x, p2y=p2y, c1=c1, c2=c2,
        a1_values=grid,
        a2_lo=a2_lo, a2_hi=a2_hi,
        tol=tol, max_iter=max_iter,
        solver_tol=solver_tol, solver_verbose=solver_verbose,
    )

    # CSV path (unchanged naming)
    csv_path = os.path.join(output_dir, csv_name)

    # PNG path with parameter tag appended to the *filename*
    param_suffix = _param_tag(p1x, p1y, p2x, p2y)  # e.g., p1x-1_p1y-1_p2x-2_p2y-1
    base_png, ext_png = os.path.splitext(png_name)
    if not ext_png:
        ext_png = ".png"
    png_name_tagged = f"{base_png}__{param_suffix}{ext_png}"
    png_path = os.path.join(output_dir, png_name_tagged)

    _save_csv(points, csv_path)
    plot_and_save(points, png_path, p1x=p1x, p1y=p1y, p2x=p2x, p2y=p2y)

    return optimizer_src, csv_path, png_path
