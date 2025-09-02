#!/usr/bin/env python3
"""
Local Best Response Checker for a 2‑Player Continuous‑Action Game

- Player 1's actions are x1, x2, ..., xN
- Player 2's actions are y1, y2, ..., yM
- You provide U1(x, y) and U2(x, y) as expressions.
- The script checks, for each player separately, whether the given action vector
  is a local best response (no small +/- delta move in any combination of own actions
  increases that player's utility, holding the opponent fixed).

Examples you can paste when prompted:å
  U1: (x1*y1) - 2(x1 + 2)
  U2: (x1 * 2(y1)) - 3(y1)

Notes:
- Implicit multiplication like 2(x1+2) is supported.
- You can use ^ for exponentiation (e.g., x1^2).
- Common functions available: sin, cos, exp, log, sqrt, Abs, Min, Max.
"""

from __future__ import annotations

import itertools
import math
import sys
from typing import Dict, List, Tuple

# --- Optional dependencies guard (Sympy is required) ---
try:
    import numpy as np
    from sympy import (
        symbols, lambdify, sin, cos, exp, log, sqrt, Abs, Min, Max, pi, E
    )
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
    )
except ImportError as e:
    print("This script requires 'sympy' and 'numpy'. Install them with:")
    print("    pip install sympy numpy")
    sys.exit(1)

# ----------------- Configuration -----------------
# Leave this as False to be prompted interactively.
# Set to True and fill the USER INPUT SECTION at the bottom instead.
SKIP_PROMPTS = False

# Parsing transformations: support implicit multiplication and ^ for powers.
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)

# Allowed functions and constants for safe parsing:
ALLOWED_FUNCS = {
    "sin": sin, "cos": cos, "exp": exp, "log": log, "sqrt": sqrt, "Abs": Abs,
    "Min": Min, "Max": Max, "pi": pi, "E": E
}


# ----------------- Helper functions -----------------
def clean_expr(expr_str: str) -> str:
    """
    Take a user string that might include 'u1 =' or 'U2 =', and return the RHS only.
    """
    s = expr_str.strip()
    if "=" in s:
        # Take the last '=' to be robust if someone writes 'u1 = U1 = ...'
        s = s.split("=")[-1]
    return s.strip()


def build_symbol_map(x_count: int, y_count: int) -> Tuple[List[str], List[str], Dict[str, object]]:
    """
    Create symbol names and Sympy Symbol objects for x1..xN and y1..yM.
    Returns:
        x_names, y_names, sym_map
    """
    x_names = [f"x{i+1}" for i in range(x_count)]
    y_names = [f"y{i+1}" for i in range(y_count)]
    sym_map = {name: symbols(name) for name in (x_names + y_names)}
    return x_names, y_names, sym_map


def make_utility(expr_str: str, x_names: List[str], y_names: List[str], sym_map: Dict[str, object]):
    """
    Turn a string expression into a fast numeric function u(vals) -> float,
    where 'vals' maps variable names to numbers.
    """
    local_dict = {}
    local_dict.update(ALLOWED_FUNCS)
    local_dict.update(sym_map)

    expr = parse_expr(clean_expr(expr_str), transformations=TRANSFORMS, local_dict=local_dict, evaluate=True)

    # Order arguments as [x1..xN, y1..yM] for lambdify
    ordered_symbols = [sym_map[n] for n in (x_names + y_names)]
    f = lambdify(ordered_symbols, expr, "numpy")

    def u(vals: Dict[str, float]) -> float:
        args = [float(vals[name]) for name in (x_names + y_names)]
        out = f(*args)
        # Convert numpy scalar/array to plain float
        return float(np.asarray(out).astype(float))

    return u


def all_step_combinations(n: int):
    """
    Yield all non-zero vectors in {-1, 0, +1}^n (exclude the all-zero vector).
    """
    for steps in itertools.product((-1, 0, 1), repeat=n):
        if any(s != 0 for s in steps):
            yield steps


def apply_steps(base: Dict[str, float], var_names: List[str], steps: Tuple[int, ...], delta: float) -> Dict[str, float]:
    """
    Return a new dict where 'var_names' have been shifted by steps * delta.
    """
    new_vals = dict(base)
    for name, s in zip(var_names, steps):
        new_vals[name] = base[name] + delta * s
    return new_vals


def format_steps(var_names: List[str], steps: Tuple[int, ...], delta: float) -> str:
    """
    e.g., for var_names=['x1','x2'], steps=(+1, -1), delta=0.01
    -> 'x1:+δ, x2:-δ'  (δ shown literally)
    """
    parts = []
    for name, s in zip(var_names, steps):
        if s == 0:
            parts.append(f"{name}:0")
        elif s > 0:
            parts.append(f"{name}:+δ")
        else:
            parts.append(f"{name}:-δ")
    return ", ".join(parts)


def safe_eval(u_func, vals: Dict[str, float]):
    """
    Evaluate u_func(vals) and catch math domain errors, etc.
    Returns (ok: bool, value_or_msg: float|str)
    """
    try:
        return True, u_func(vals)
    except Exception as ex:
        return False, f"Error: {type(ex).__name__}: {ex}"


def check_local_best_response(
    player_name: str,
    u_func,
    base_vals: Dict[str, float],
    own_vars: List[str],
    opp_vars: List[str],
    delta: float,
    tol: float
) -> Tuple[bool, List[Dict]]:
    """
    For a given player, iterate all combinations in {-1,0,+1}^{n_own} \ {0} on OWN variables only,
    hold opponent variables fixed, and report ΔU for each move.

    Returns:
        (is_local_best_response, records)
        where records is a list of dicts with keys:
        'steps', 'step_label', 'U_new', 'dU', 'status', 'ok'
    """
    # Baseline utility:
    ok0, U0 = safe_eval(u_func, base_vals)
    if not ok0:
        raise ValueError(f"Cannot evaluate baseline {player_name} utility: {U0}")

    records = []
    improved = False

    for steps in all_step_combinations(len(own_vars)):
        moved_vals = apply_steps(base_vals, own_vars, steps, delta)
        ok, U_new = safe_eval(u_func, moved_vals)

        if not ok:
            rec = {
                "steps": steps,
                "step_label": format_steps(own_vars, steps, delta),
                "ok": False,
                "U_new": None,
                "dU": None,
                "status": U_new,  # error message
            }
            records.append(rec)
            # An unevaluable neighbor does not constitute a profitable deviation; ignore for "improvement"
            continue

        dU = U_new - U0
        # Classify the effect of the move
        if dU > tol:
            status = "improves"
            improved = True
        elif dU < -tol:
            status = "worsens"
        else:
            status = "no change"

        rec = {
            "steps": steps,
            "step_label": format_steps(own_vars, steps, delta),
            "ok": True,
            "U_new": U_new,
            "dU": dU,
            "status": status,
        }
        records.append(rec)

    is_local_br = not improved  # no profitable local deviation
    return is_local_br, records


def print_report(player_name: str, U0: float, is_br: bool, records: List[Dict]):
    print(f"\n=== {player_name}: Local Best Response Check ===")
    print(f"Baseline utility {player_name}: {U0:.12g}")
    print(f"Neighbor checks: {sum(1 for _ in records)} moves\n")
    print("Move (own-variables only) | U_new              | ΔU = U_new - U_base | Effect")
    print("-" * 85)
    for r in records:
        if not r["ok"]:
            print(f"{r['step_label']:<26} | {'(n/a)':<18} | {'(n/a)':<20} | {r['status']}")
        else:
            print(f"{r['step_label']:<26} | {r['U_new']:<18.12g} | {r['dU']:<20.12g} | {r['status']}")
    print("-" * 85)
    verdict = "YES" if is_br else "NO"
    print(f"Is the provided action a LOCAL best response for {player_name}? {verdict}\n")


def main():
    # ----------------- Gather inputs -----------------
    if not SKIP_PROMPTS:
        # Number of actions per player
        while True:
            try:
                x_count = int(input("How many actions for Player 1 (x-variables)? e.g., 1 or 2: ").strip())
                y_count = int(input("How many actions for Player 2 (y-variables)? e.g., 1 or 2: ").strip())
                if x_count <= 0 or y_count <= 0:
                    raise ValueError
                break
            except Exception:
                print("Please enter positive integers (e.g., 1 or 2).")

        # Build variable names and sympy symbols
        x_names, y_names, sym_map = build_symbol_map(x_count, y_count)

        # Utility expressions
        print("\nEnter Player 1's utility U1(x,y). Example: (x1*y1) - 2(x1 + 2)")
        u1_expr = input("U1 = ").strip()

        print("\nEnter Player 2's utility U2(x,y). Example: (x1 * 2(y1)) - 3(y1)")
        u2_expr = input("U2 = ").strip()

        # Step and tolerance
        def read_float(prompt, default):
            raw = input(f"{prompt} [default {default}]: ").strip()
            return float(raw) if raw else default

        delta = read_float("\nStep size δ for local check", 0.01)
        tol = read_float("Numerical tolerance for 'improvement' (treat |ΔU| ≤ tol as 'no change')", 1e-12)

        # Action values
        print("\nEnter action values.")
        base_vals: Dict[str, float] = {}
        for name in x_names:
            base_vals[name] = float(input(f"  {name} = ").strip())
        for name in y_names:
            base_vals[name] = float(input(f"  {name} = ").strip())

    else:
        # ----------------- USER INPUT SECTION (fill when SKIP_PROMPTS=True) -----------------
        # How many actions each player has:
        x_count = 1
        y_count = 1

        # Build names/symbols
        x_names, y_names, sym_map = build_symbol_map(x_count, y_count)

        # Utility expressions (strings). You can include 'u1 =' or 'U2 =' or just the RHS.
        u1_expr = " (x1*y1) - 2(x1 + 2) "
        u2_expr = " (x1 * 2(y1)) - 3(y1) "

        # Step size and tolerance:
        delta = 0.01
        tol = 1e-12

        # Action values:
        base_vals = {
            "x1": 2.0,
            "y1": 3.0,
        }
        # ----------------- END USER INPUT SECTION -----------------

    # ----------------- Build utility callables -----------------
    U1 = make_utility(u1_expr, x_names, y_names, sym_map)
    U2 = make_utility(u2_expr, x_names, y_names, sym_map)

    # Baseline utilities:
    ok1, U1_base = safe_eval(U1, base_vals)
    ok2, U2_base = safe_eval(U2, base_vals)
    if not ok1:
        raise ValueError(f"Failed to evaluate baseline U1: {U1_base}")
    if not ok2:
        raise ValueError(f"Failed to evaluate baseline U2: {U2_base}")

    # ----------------- Check local best responses -----------------
    # Player 1: vary x's, hold y fixed
    is_br1, rec1 = check_local_best_response(
        "Player 1", U1, base_vals, own_vars=x_names, opp_vars=y_names, delta=delta, tol=tol
    )

    # Player 2: vary y's, hold x fixed
    is_br2, rec2 = check_local_best_response(
        "Player 2", U2, base_vals, own_vars=y_names, opp_vars=x_names, delta=delta, tol=tol
    )

    # ----------------- Print detailed report -----------------
    print("\n" + "=" * 90)
    print("INPUT SUMMARY")
    print("=" * 90)
    print("Variables:")
    print("  Player 1 (x):", ", ".join(x_names))
    print("  Player 2 (y):", ", ".join(y_names))
    print("Values:")
    for name in x_names + y_names:
        print(f"  {name} = {base_vals[name]}")
    print("\nUtilities (interpreted):")
    print("  U1(x,y) =", clean_expr(u1_expr))
    print("  U2(x,y) =", clean_expr(u2_expr))
    print(f"\nStep size δ = {delta}, tolerance = {tol}")
    print(f"Baseline utilities:  U1 = {U1_base:.12g},  U2 = {U2_base:.12g}")
    print("=" * 90)

    # Detailed tables
    print_report("Player 1", U1_base, is_br1, rec1)
    print_report("Player 2", U2_base, is_br2, rec2)

    # Overall verdict (local Nash condition = both are local BRs)
    both_local_br = is_br1 and is_br2
    print("=" * 90)
    print(f"Do the provided actions form a (simultaneous) LOCAL Nash equilibrium?")
    print(f"Answer: {'YES' if both_local_br else 'NO'}")
    print("=" * 90)


if __name__ == "__main__":
    main()
