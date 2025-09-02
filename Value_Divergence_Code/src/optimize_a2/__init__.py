"""
value_divergence_tools

Exports:
- optimize_a2_for_player1: maximize player 1's utility over a2 in (0,1),
  repeatedly calling your standard solver in Finding_Equilibrium_1.py.
- OptimizationResult: container with best a2, U1, chosen mask, and the equilibrium dict.
"""

from .optimize_a2 import optimize_a2_for_player1, OptimizationResult

__all__ = ["optimize_a2_for_player1", "OptimizationResult"]
