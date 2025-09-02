import math
from typing import Dict, Any, List

def solve_two_task_cobb_douglas_equilibrium(
    a1: float, a2: float,
    c1: float, c2: float,
    p1x: float, p1y: float, p2x: float, p2y: float,
    *, tol: float = 1e-10, verbose: bool = True
) -> Dict[str, Any]:
    """
    Two-Task Cobb–Douglas Team: case selection and closed-form equilibrium.
    Implements ONLY the formulas and inequalities in these sources (do not change paths):
      - /mnt/data/Value_Divergence (56).pdf  [Pairs P1–P4, Tables 1–3, interior selection derivation]
      - /mnt/data/Value_Divergence (57).pdf  [fully-interior proportional-split note; equivalent selection]

    Returns
    -------
    If exactly one case matches:
      {
        "multiple_matches": False,
        "mask": "<one of 'B,X'|'X,B'|'B,Y'|'Y,B'|'X,Y'|'Y,X'|'B,B'>",
        "r": float,
        "x1": float, "y1": float, "x2": float, "y2": float,
        "totals": {"s1": float, "s2": float},
        "XY": {"X": float, "Y": float, "ratio": float},
        "candidates": [...],        # all tested cases with margins
        "diagnostics": {...}        # FOCs/KKT and ratio checks
      }

    If multiple cases match (knife-edge):
      {
        "multiple_matches": True,
        "masks": ["...", "..."],
        "solutions_by_mask": { "<mask>": <solution dict as above>, ... },
        "candidates": [...],
        "note": "Knife-edge / boundary: more than one mask satisfied the PDF inequalities"
      }

    If no case matches:
      {
        "multiple_matches": False,
        "mask": None,
        "reason": "no feasible mask under PDF inequalities",
        "candidates": [...],   # shows which inequalities failed (with margins)
      }

    Notes on selection in (B,B):
      - Uses the canonical equal-fraction-to-X rule from Table 2 (56.pdf):
        lambda = (p1y*s1 + p2y*s2) / [ (p1y*s1 + p2y*s2) + r*(p1x*s1 + p2x*s2) ]
        x_i = lambda * s_i, y_i = (1-lambda)*s_i
      - This is equivalent to the proportional-split rule in (57).pdf.

    """

    # -----------------------------
    # Step 0. Validate input domains (56.pdf, p.1)
    # -----------------------------
    def _in_open_unit(x): return (x > 0.0) and (x < 1.0)
    if not (_in_open_unit(a1) and _in_open_unit(a2)):
        raise ValueError("ai must be in (0,1).")
    for name, val in [("c1", c1), ("c2", c2), ("p1x", p1x), ("p1y", p1y), ("p2x", p2x), ("p2y", p2y)]:
        if not (val > 0.0):
            raise ValueError(f"{name} must be > 0.")

    # helper comparisons with tolerance
    geq = lambda A, B: (A >= B - tol)    # A >= B (within tol)
    leq = lambda A, B: (A <= B + tol)    # A <= B (within tol)
    close = lambda A, B: (abs(A - B) <= tol)

    # -----------------------------
    # Step 1. Parameter-only primitives (56.pdf, eqs (6)-(7); P4)
    # -----------------------------
    r1 = (a1 * p1y) / ((1.0 - a1) * p1x)
    r2 = (a2 * p2y) / ((1.0 - a2) * p2x)
    KXY = (a2 * c1 * (p2y ** 2.0)) / ((1.0 - a1) * c2 * (p1x ** 2.0))
    KYX = (a1 * c2 * (p1y ** 2.0)) / ((1.0 - a2) * c1 * (p2x ** 2.0))

    # specialized r* (unique positive roots since exponents in (1,3); 56.pdf P4)
    exp_XY = 2.0 + a1 - a2
    exp_YX = 2.0 + a2 - a1
    r_star_XY = KXY ** (1.0 / exp_XY)
    r_star_YX = KYX ** (1.0 / exp_YX)

    # -----------------------------
    # Step 2. Case feasibility tests (parameter-only inequalities; 56.pdf Table 1)
    # -----------------------------
    candidates: List[Dict[str, Any]] = []

    # (B,X)
    LHS_c2 = r1 ** (1.0 + a2 - a1)
    RHS_c2 = ((1.0 - a1) * p1y * p1x * c2) / ((1.0 - a2) * (p2x ** 2.0) * c1)
    pass_BX = geq(r1, r2) and leq(LHS_c2, RHS_c2)
    candidates.append({
        "mask": "B,X",
        "passed": pass_BX,
        "margins": {
            "r1_minus_r2": r1 - r2,                          # should be >= 0
            "capacity_LHS_minus_RHS": LHS_c2 - RHS_c2        # should be <= 0
        }
    })

    # (X,B)  [flip 1↔2]
    LHS_c2_XB = r2 ** (1.0 + a1 - a2)
    RHS_c2_XB = ((1.0 - a2) * p2y * p2x * c1) / ((1.0 - a1) * (p1x ** 2.0) * c2)
    pass_XB = geq(r2, r1) and leq(LHS_c2_XB, RHS_c2_XB)
    candidates.append({
        "mask": "X,B",
        "passed": pass_XB,
        "margins": {
            "r2_minus_r1": r2 - r1,                          # should be >= 0
            "capacity_LHS_minus_RHS": LHS_c2_XB - RHS_c2_XB  # should be <= 0
        }
    })

    # (B,Y)
    LHS_c2_BY = r1 ** (2.0 + a1 - a2)
    pass_BY = leq(r1, r2) and geq(LHS_c2_BY, KXY)
    candidates.append({
        "mask": "B,Y",
        "passed": pass_BY,
        "margins": {
            "r1_minus_r2": r1 - r2,                       # should be <= 0
            "r1_power_minus_KXY": LHS_c2_BY - KXY        # should be >= 0
        }
    })

    # (Y,B)  [flip 1↔2]
    LHS_c2_YB = r2 ** (2.0 + a2 - a1)
    pass_YB = leq(r2, r1) and geq(LHS_c2_YB, KYX)
    candidates.append({
        "mask": "Y,B",
        "passed": pass_YB,
        "margins": {
            "r2_minus_r1": r2 - r1,                       # should be <= 0
            "r2_power_minus_KYX": LHS_c2_YB - KYX        # should be >= 0
        }
    })

    # (X,Y) specialization (56.pdf P4)
    pass_XY = geq(r_star_XY, r1) and leq(r_star_XY, r2)
    candidates.append({
        "mask": "X,Y",
        "passed": pass_XY,
        "margins": {
            "r_star_minus_r1": r_star_XY - r1,            # should be >= 0
            "r2_minus_r_star": r2 - r_star_XY,            # should be >= 0
            "equation_LHS_minus_RHS": (r_star_XY ** exp_XY) - KXY  # should be ~ 0
        }
    })

    # (Y,X) specialization [flip]
    pass_YX = geq(r_star_YX, r2) and leq(r_star_YX, r1)
    candidates.append({
        "mask": "Y,X",
        "passed": pass_YX,
        "margins": {
            "r_star_minus_r2": r_star_YX - r2,            # should be >= 0
            "r1_minus_r_star": r1 - r_star_YX,            # should be >= 0
            "equation_LHS_minus_RHS": (r_star_YX ** exp_YX) - KYX  # should be ~ 0
        }
    })

    # (B,B) fully interior (knife-edge r1=r2); selection via equal fraction to X (56.pdf pp.14–15, Table 2)
    pass_BB = close(r1, r2)
    candidates.append({
        "mask": "B,B",
        "passed": pass_BB,
        "margins": {"r1_minus_r2": r1 - r2}               # should be ~ 0
    })

    passing = [c["mask"] for c in candidates if c["passed"]]

    # -----------------------------
    # Step 3. If zero / multiple matches, handle per request
    # -----------------------------
    if len(passing) == 0:
        if verbose:
            print("No feasible mask under the PDF inequalities. See candidate margins for diagnostics.")
        return {
            "multiple_matches": False,
            "mask": None,
            "reason": "no feasible mask under PDF inequalities",
            "candidates": candidates
        }

    # helper: compute equilibrium for a given mask
    def _solve_for_mask(mask: str) -> Dict[str, Any]:
        # local aliases
        _a1, _a2, _c1, _c2 = a1, a2, c1, c2
        _p1x, _p1y, _p2x, _p2y = p1x, p1y, p2x, p2y

        if mask == "B,X":
            r = r1
            s1 = ((1.0 - _a1) * _p1x / _c1) * (r ** _a1)
            s2 = ((1.0 - _a2) * _p2x / _c2) * (r ** _a2)
            y1 = (r * (_p1x * s1 + _p2x * s2)) / (_p1y + r * _p1x)
            x1 = s1 - y1
            x2 = s2
            y2 = 0.0

        elif mask == "X,B":
            r = r2
            s2 = ((1.0 - _a2) * _p2x / _c2) * (r ** _a2)
            s1 = ((1.0 - _a1) * _p1x / _c1) * (r ** _a1)
            y2 = (r * (_p1x * s1 + _p2x * s2)) / (_p2y + r * _p2x)
            x2 = s2 - y2
            x1 = s1
            y1 = 0.0

        elif mask == "B,Y":
            r = r1
            s1 = ((1.0 - _a1) * _p1x / _c1) * (r ** _a1)
            s2 = (_a2 * _p2y / _c2) * (r ** (_a2 - 1.0))
            y1 = (r * _p1x * s1 - _p2y * s2) / (_p1y + r * _p1x)
            x1 = s1 - y1
            x2 = 0.0
            y2 = s2

        elif mask == "Y,B":
            r = r2
            s2 = ((1.0 - _a2) * _p2x / _c2) * (r ** _a2)     # also equals (a2*p2y/_c2)*r^{-(1-a2)}
            s1 = (_a1 * _p1y / _c1) * (r ** (_a1 - 1.0))
            y2 = (r * _p2x * s2 - _p1y * s1) / (_p2y + r * _p2x)
            x2 = s2 - y2
            x1 = 0.0
            y1 = s1

        elif mask == "X,Y":
            r = r_star_XY
            x1 = ((1.0 - _a1) * _p1x / _c1) * (r ** _a1)
            y1 = 0.0
            x2 = 0.0
            y2 = (_a2 * _p2y / _c2) * (r ** (_a2 - 1.0))

        elif mask == "Y,X":
            r = r_star_YX
            x1 = 0.0
            y1 = (_a1 * _p1y / _c1) * (r ** (_a1 - 1.0))
            x2 = ((1.0 - _a2) * _p2x / _c2) * (r ** _a2)
            y2 = 0.0

        elif mask == "B,B":
            # Knife-edge: r1 == r2; set r and use canonical equal-fraction-to-X λ (56.pdf, pp.14–15, Table 2)
            r = r1  # == r2 within tol
            s1 = ((1.0 - _a1) * _p1x / _c1) * (r ** _a1)
            s2 = ((1.0 - _a2) * _p2x / _c2) * (r ** _a2)
            SX = _p1x * s1 + _p2x * s2
            SY = _p1y * s1 + _p2y * s2
            lam = SY / (SY + r * SX)  # equal fraction to X
            x1, y1 = lam * s1, (1.0 - lam) * s1
            x2, y2 = lam * s2, (1.0 - lam) * s2
        else:
            raise ValueError(f"Unknown mask '{mask}'")

        # Build totals and outputs; compute ratio and diagnostics
        s1_calc = x1 + y1
        s2_calc = x2 + y2
        X = p1x * x1 + p2x * x2
        Y = p1y * y1 + p2y * y2
        ratio = (Y / X) if X > 0 else float('inf')

        # FOC / KKT residuals using r (all feasible cases use r > 0)
        # Active/inactive sets by mask:
        active = {
            "x1": x1 > tol, "y1": y1 > tol,
            "x2": x2 > tol, "y2": y2 > tol
        }
        s1_here, s2_here = s1_calc, s2_calc

        def foc_x(ai, pix, ci, s, rr): return (1.0 - ai) * pix * (rr ** ai) - ci * s
        def foc_y(ai, piy, ci, s, rr): return ai * piy * (rr ** (ai - 1.0)) - ci * s

        diagnostics = {
            "checks": {
                "ratio_identity_abs_error": abs(ratio - r) if math.isfinite(ratio) else float('inf'),
                "s_totals_residuals": {"s1_minus_x1_plus_y1": s1_here - s1_calc, "s2_minus_x2_plus_y2": s2_here - s2_calc},
                "active_foc_residuals": {},
                "inactive_kkt_margins": {}
            }
        }

        # Player 1
        if active["x1"]:
            diagnostics["checks"]["active_foc_residuals"]["x1"] = foc_x(a1, p1x, c1, s1_here, r)
        else:
            diagnostics["checks"]["inactive_kkt_margins"]["x1"] = foc_x(a1, p1x, c1, s1_here, r)  # should be <= 0
        if active["y1"]:
            diagnostics["checks"]["active_foc_residuals"]["y1"] = foc_y(a1, p1y, c1, s1_here, r)
        else:
            diagnostics["checks"]["inactive_kkt_margins"]["y1"] = foc_y(a1, p1y, c1, s1_here, r)  # should be <= 0

        # Player 2
        if active["x2"]:
            diagnostics["checks"]["active_foc_residuals"]["x2"] = foc_x(a2, p2x, c2, s2_here, r)
        else:
            diagnostics["checks"]["inactive_kkt_margins"]["x2"] = foc_x(a2, p2x, c2, s2_here, r)  # should be <= 0
        if active["y2"]:
            diagnostics["checks"]["active_foc_residuals"]["y2"] = foc_y(a2, p2y, c2, s2_here, r)
        else:
            diagnostics["checks"]["inactive_kkt_margins"]["y2"] = foc_y(a2, p2y, c2, s2_here, r)  # should be <= 0

        # Assemble solution dict
        sol = {
            "multiple_matches": False,
            "mask": mask,
            "r": r,
            "x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2),
            "totals": {"s1": float(s1_calc), "s2": float(s2_calc)},
            "XY": {"X": float(X), "Y": float(Y), "ratio": float(ratio)},
            "diagnostics": diagnostics
        }
        return sol

    if len(passing) > 1:
        # Edge / knife-edge: compute and return solutions for all passing cases
        if verbose:
            print(f"Edge case: multiple masks matched ({len(passing)}). Masks = {passing}")
            print("Returning solutions for each passing case to aid debugging.")
        sols = {mask: _solve_for_mask(mask) for mask in passing}
        return {
            "multiple_matches": True,
            "masks": passing,
            "solutions_by_mask": sols,
            "candidates": candidates,
            "note": "Knife-edge / boundary: more than one mask satisfied the PDF inequalities"
        }

    # Exactly one match
    mask = passing[0]
    if verbose:
        print(f"Matched mask: {mask}")
    sol = _solve_for_mask(mask)
    sol["candidates"] = candidates
    return sol
