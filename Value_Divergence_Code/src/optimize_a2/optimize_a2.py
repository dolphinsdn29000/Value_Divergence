# -*- coding: utf-8 -*-
"""
Maximize Player 1's utility over a2 ∈ (0,1) by *calling Tony's standard solver*:
    solve_two_task_cobb_douglas_equilibrium(...) in Finding_Equilibrium_1.py

This re-solves the equilibrium for every trial a2 using your canonical code.

Primary import target:
  /Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/Scripts/Finding Equilibrium/Finding_Equilibrium_1.py
Fallback:
  /mnt/data/Finding_Equilibrium_1.py

Return object includes the chosen mask and full equilibrium dict at the optimum.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from importlib import import_module, util as importlib_util
from types import ModuleType
from typing import Callable, Dict, List, Optional, Tuple


# ---- Exact file paths (no blanks). Update here if you move the file. ----
_CANDIDATE_FILES = [
    # Primary local project path (preferred)
    "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src/Equil_finder/Finding_Equilibrium_1.py",
    # Session upload path (fallback)
    "/mnt/data/Finding_Equilibrium_1.py",
]


def _load_solver_from_path(pyfile: str) -> Optional[Tuple[Callable, str]]:
    """Try to load solve_two_task_cobb_douglas_equilibrium from a specific .py file path."""
    try:
        spec = importlib_util.spec_from_file_location("Finding_Equilibrium_1", pyfile)
        if spec is None or spec.loader is None:
            return None
        mod = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        if hasattr(mod, "solve_two_task_cobb_douglas_equilibrium"):
            return getattr(mod, "solve_two_task_cobb_douglas_equilibrium"), pyfile
    except Exception:
        return None
    return None


def _import_solver() -> Tuple[Callable, str]:
    """
    Import the canonical equilibrium solver:
      solve_two_task_cobb_douglas_equilibrium(a1, a2, c1, c2, p1x, p1y, p2x, p2y, *, tol=..., verbose=...)
    Resolution order:
      1) Standard import by module name (if it's already on sys.path)
      2) Load directly from known absolute file paths in _CANDIDATE_FILES
    """
    # 1) If user has already put it on sys.path
    try:
        mod = import_module("Finding_Equilibrium_1")
        fn = getattr(mod, "solve_two_task_cobb_douglas_equilibrium", None)
        if callable(fn):
            # Best we can do for provenance is module __file__ if present:
            src = getattr(mod, "__file__", "Finding_Equilibrium_1 (module on sys.path)")
            return fn, str(src)
    except Exception:
        pass

    # 2) Try explicit files (preferred order)
    for fp in _CANDIDATE_FILES:
        found = _load_solver_from_path(fp)
        if found is not None:
            return found

    raise ImportError(
        "Could not import solve_two_task_cobb_douglas_equilibrium from Finding_Equilibrium_1.py. "
        "Checked sys.path and: " + " | ".join(_CANDIDATE_FILES)
    )


def _u1_from_solution(sol: Dict, a1: float, c1: float) -> Optional[Tuple[float, str]]:
    """
    Compute U1 = X^(1-a1) * Y^a1 - 0.5*c1*(x1+y1)^2 from a solver return dict.
    Returns (U1, mask) or None if invalid.
    Handles both single- and multi-mask (knife-edge) solutions by picking the mask with max U1.
    """
    def _one(sol1: Dict) -> Optional[Tuple[float, str]]:
        try:
            x1 = float(sol1["x1"]); y1 = float(sol1["y1"])
            X  = float(sol1["XY"]["X"]); Y = float(sol1["XY"]["Y"])
            if X <= 0.0 or Y <= 0.0:
                return None
            benefit = (X ** (1.0 - a1)) * (Y ** a1)
            cost    = 0.5 * c1 * (x1 + y1) ** 2
            u1 = benefit - cost
            if not math.isfinite(u1):
                return None
            return u1, str(sol1.get("mask", ""))
        except Exception:
            return None

    # Multi-mask case
    if sol.get("multiple_matches", False):
        best_pair: Optional[Tuple[float, str]] = None
        for m, sdict in sol.get("solutions_by_mask", {}).items():
            got = _one(sdict)
            if got is None:
                continue
            if (best_pair is None) or (got[0] > best_pair[0]):
                best_pair = got
        return best_pair

    # Single solution
    return _one(sol)


@dataclass
class OptimizationResult:
    best_a2: float
    u1_at_best: float
    chosen_mask: str
    eqm_at_best: Dict
    samples: List[Tuple[float, float, str]]  # (a2, U1, mask_or_note)
    solver_source: str

def optimize_a2_for_player1(
    *,
    a1: float,
    p1x: float, p1y: float,
    p2x: float, p2y: float,
    c1: float, c2: float,
    a2_lo: float = 1e-6,         # open interval (0,1): the solver requires a2 in (0,1)
    a2_hi: float = 1.0 - 1e-6,
    tol: float = 1e-5,
    max_iter: int = 200,
    solver_tol: float = 1e-10,
    solver_verbose: bool = False,
) -> OptimizationResult:
    """
    Robust maximization of Player 1's utility over a2 ∈ (a2_lo, a2_hi).

    Strategy:
      (1) Uniform coarse scan across the *entire* interval (no assumptions).
      (2) Golden-section refinement in a small bracket around the best coarse point.
      (3) ALWAYS include the true global endpoints as candidates.
      (4) Return the best among all candidates.

    This fixes failures when U1(a2) is piecewise / has jumps at mask switches.
    """
    if not (0.0 < a2_lo < a2_hi < 1.0):
        raise ValueError("Require 0.0 < a2_lo < a2_hi < 1.0 (open interval).")

    # --- canonical solver ---
    eq_solver, solver_src = _import_solver()

    def trial(a2_val: float) -> Tuple[float, Dict, str]:
        """Evaluate U1 at a2_val by solving equilibrium via your standard solver."""
        try:
            sol = eq_solver(
                a1=a1, a2=float(a2_val),
                c1=c1, c2=c2,
                p1x=p1x, p1y=p1y, p2x=p2x, p2y=p2y,
                tol=solver_tol, verbose=solver_verbose
            )
        except Exception as e:
            return float("-inf"), {"error": f"{type(e).__name__}: {e}"}, "ERR"

        u1_mask = _u1_from_solution(sol, a1, c1)
        if u1_mask is None:
            return float("-inf"), sol, sol.get("mask") or "NOFEAS"
        u1, mask = u1_mask
        return float(u1), sol, str(mask)

    samples: List[Tuple[float, float, str]] = []
    eps = max(1e-9, 1e-12 * (a2_hi - a2_lo))

    # ---------- (1) UNIFORM COARSE SCAN over the full interval ----------
    COARSE_N = 2001  # increase if you want even denser brute force
    span = (a2_hi - a2_lo)
    step = span / (COARSE_N + 1)  # so first/last interior to (a2_lo, a2_hi)

    coarse_best_u = float("-inf")
    coarse_best_a2 = None
    coarse_best_sol: Dict = {}
    coarse_best_mask = "INIT"

    for i in range(1, COARSE_N + 1):
        a2v = a2_lo + i * step
        if i == 1:
            a2v = a2_lo + eps
        elif i == COARSE_N:
            a2v = a2_hi - eps
        u, st, m = trial(a2v)
        samples.append((a2v, u, m))
        if u > coarse_best_u:
            coarse_best_u, coarse_best_a2, coarse_best_sol, coarse_best_mask = u, a2v, st, m

    # If everything infeasible, fallback to midpoint
    if coarse_best_a2 is None:
        mid = a2_lo + 0.5 * span
        u_mid, st_mid, m_mid = trial(mid)
        samples.append((mid, u_mid, m_mid))
        return OptimizationResult(
            best_a2=float(mid),
            u1_at_best=float(u_mid),
            chosen_mask=str(m_mid),
            eqm_at_best=st_mid,
            samples=[(float(a2), float(u1), str(msk)) for (a2, u1, msk) in samples],
            solver_source=solver_src,
        )

    # ---------- (2) GOLDEN REFINEMENT around the coarse best ----------
    # Small local bracket centered at coarse_best_a2 (use one coarse step on each side)
    a = max(a2_lo + eps, coarse_best_a2 - step)
    b = min(a2_hi - eps, coarse_best_a2 + step)
    if b - a < 10 * eps:
        a, b = a2_lo + eps, a2_hi - eps

    phi = (math.sqrt(5.0) - 1.0) / 2.0
    c_pt = b - phi * (b - a)
    d_pt = a + phi * (b - a)

    u_c, sol_c, m_c = trial(c_pt)
    u_d, sol_d, m_d = trial(d_pt)
    samples.extend([(c_pt, u_c, m_c), (d_pt, u_d, m_d)])

    it = 0
    while (b - a) > tol and it < max_iter:
        it += 1
        if u_c < u_d:
            a = c_pt
            c_pt, u_c, sol_c, m_c = d_pt, u_d, sol_d, m_d
            d_pt = a + phi * (b - a)
            u_d, sol_d, m_d = trial(d_pt)
            samples.append((d_pt, u_d, m_d))
        else:
            b = d_pt
            d_pt, u_d, sol_d, m_d = c_pt, u_c, sol_c, m_c
            c_pt = b - phi * (b - a)
            u_c, sol_c, m_c = trial(c_pt)
            samples.append((c_pt, u_c, m_c))

    # Include the local bracket ends
    u_a, sol_a, m_a = trial(a)
    u_b, sol_b, m_b = trial(b)
    samples.extend([(a, u_a, m_a), (b, u_b, m_b)])

    # ---------- (3) ALWAYS include the TRUE GLOBAL ENDPOINTS ----------
    u_lo, sol_lo, m_lo = trial(a2_lo + eps)
    u_hi, sol_hi, m_hi = trial(a2_hi - eps)
    samples.extend([(a2_lo + eps, u_lo, m_lo), (a2_hi - eps, u_hi, m_hi)])

    # Also include the best coarse point
    u_seed, a2_seed, sol_seed, m_seed = coarse_best_u, coarse_best_a2, coarse_best_sol, coarse_best_mask

    # ---------- (4) Pick the best among all candidates ----------
    candidates = [
        (c_pt, u_c, sol_c, m_c),
        (d_pt, u_d, sol_d, m_d),
        (a,    u_a, sol_a, m_a),
        (b,    u_b, sol_b, m_b),
        (a2_lo + eps, u_lo, sol_lo, m_lo),
        (a2_hi - eps, u_hi, sol_hi, m_hi),
        (a2_seed, u_seed, sol_seed, m_seed),
    ]
    best = max(candidates, key=lambda t: t[1])

    return OptimizationResult(
        best_a2=float(best[0]),
        u1_at_best=float(best[1]),
        chosen_mask=str(best[3]),
        eqm_at_best=best[2],
        samples=[(float(a2), float(u1), str(msk)) for (a2, u1, msk) in samples],
        solver_source=solver_src,
    )
