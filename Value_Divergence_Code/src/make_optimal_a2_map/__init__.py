"""
make_optimal_a2_map

Grid-sweeps productivities to study the relationship between Player 1's taste a1
and the optimal a2 for Player 1. Uses Tony's optimizer (which calls the canonical equilibrium solver).
"""

from .core import (
    sweep_productivities,
    save_summary_csv,
    save_raw_curves_csv,
    plot_fraction_heatmap,
    plot_signed_gap_heatmap,
)
__all__ = [
    "sweep_productivities",
    "save_summary_csv",
    "save_raw_curves_csv",
    "plot_fraction_heatmap",
    "plot_signed_gap_heatmap",
]
