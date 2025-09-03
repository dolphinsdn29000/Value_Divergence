#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run a grid-sweep over productivities (r1, r2) to study the "opposites attract" phenomenon.

This script calls the package:
  make_optimal_a2_map
which imports the optimizer from:
  src/optimize_a2/optimize_a2.py

Outputs:
  - CSV summary
  - CSV raw curves
  - Heatmap PNGs
All saved under /outputs in your project.
"""

import sys
from pathlib import Path

# --- Ensure /src is on path ---
SRC_DIR = Path("/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from make_optimal_a2_map import (
    sweep_productivities,
    save_summary_csv,
    save_raw_curves_csv,
    plot_fraction_heatmap,
    plot_signed_gap_heatmap,
)


def main():
    # --- Choose grid parameters ---
    summary_rows, raw_rows, src = sweep_productivities(
        r1_min=0.5, r1_max=2.0, r1_steps=16,
        r2_min=0.5, r2_max=2.0, r2_steps=16,
        a1_min=0.01, a1_max=0.99, a1_steps=101,
        c=1.0,  # keep costs equal
    )

    print("Optimizer source file used:", src)
    print("Total (r1,r2) pairs:", len(summary_rows))

    # Save results
    sum_path = save_summary_csv(summary_rows)
    raw_path = save_raw_curves_csv(raw_rows)
    frac_png = plot_fraction_heatmap(summary_rows)
    gap_png = plot_signed_gap_heatmap(summary_rows)

    print("Summary CSV:", sum_path)
    print("Raw curves CSV:", raw_path)
    print("Fraction heatmap:", frac_png)
    print("Signed gap heatmap:", gap_png)


if __name__ == "__main__":
    main()
