"""
make_optimal_a2_graph

Utilities to compute and plot the curve a1 ↦ argmax_{a2∈(0,1)} U1(a1,a2; params),
repeatedly calling Tony's optimizer (which calls the canonical equilibrium solver).
"""

from .core import (
    A1A2Point,
    make_a1_grid,
    compute_a1_vs_opt_a2,
    plot_and_save,
    run_and_save,
)

__all__ = [
    "A1A2Point",
    "make_a1_grid",
    "compute_a1_vs_opt_a2",
    "plot_and_save",
    "run_and_save",
]
