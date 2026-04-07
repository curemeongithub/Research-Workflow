"""Parallel-architecture convex (lower-bound) solver via CVXPY.

Matches the primal convention in standard_primal_solver.py: the primal uses
`(beta/2) sum ||W||_F^2` and the convex program uses `beta * sum_j (||u_j||_2 + ||v_j||_2)`.
So the scalar `beta` is passed through unchanged.
"""
from __future__ import annotations

from typing import List

import cvxpy as cp
import numpy as np


def enumerate_sign_patterns(X: np.ndarray, max_patterns: int = 200,
                            oversample_factor: int = 20, rng_seed: int = 0) -> List[np.ndarray]:
    rng = np.random.default_rng(rng_seed)
    n, d = X.shape
    seen = set()
    out: List[np.ndarray] = []
    budget = max_patterns * oversample_factor
    for _ in range(budget):
        v = rng.standard_normal(d)
        pattern = (X @ v > 0).astype(np.int8)
        key = pattern.tobytes()
        if key not in seen:
            seen.add(key)
            out.append(pattern)
            if len(out) >= max_patterns:
                break
    all_ones = np.ones(n, dtype=np.int8)
    if all_ones.tobytes() not in seen:
        out.append(all_ones)
        seen.add(all_ones.tobytes())
    zeros = np.zeros(n, dtype=np.int8)  # trivial; ensures feasibility
    if zeros.tobytes() not in seen:
        out.append(zeros)
    return out


def solve_convex_parallel(X: np.ndarray, y: np.ndarray, *, beta: float,
                          max_patterns: int = 200, solver_eps: float = 1e-9,
                          max_iters: int = 40000, pattern_seed: int = 0,
                          logger=None) -> dict:
    """Two-layer-style parallel convex program (valid LB for deeper parallel net)."""
    n, d = X.shape
    patterns = enumerate_sign_patterns(X, max_patterns=max_patterns, rng_seed=pattern_seed)
    P = len(patterns)

    u_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]

    pred_terms = []
    for j in range(P):
        mask = patterns[j].astype(np.float64)
        pred_terms.append(cp.multiply(mask, X @ (u_vars[j] - v_vars[j])))
    pred = cp.sum(pred_terms)

    data_loss = (0.5 / n) * cp.sum_squares(y - pred)
    reg = beta * cp.sum([cp.norm(u_vars[j], 2) + cp.norm(v_vars[j], 2) for j in range(P)])
    prob = cp.Problem(cp.Minimize(data_loss + reg))

    try:
        prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=max_iters, verbose=False)
    except Exception as e:
        if logger is not None:
            logger.warning(f"SCS failed ({e}); retrying with CLARABEL")
        prob.solve(solver=cp.CLARABEL, verbose=False)

    if prob.status not in ("optimal", "optimal_inaccurate"):
        if logger is not None:
            logger.warning(f"Retry CLARABEL after status={prob.status}")
        prob.solve(solver=cp.CLARABEL, verbose=False)

    if prob.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"Convex solve failed with status={prob.status}")

    stats = prob.solver_stats
    return {
        "d_parallel": float(prob.value),
        "status": prob.status,
        "num_patterns": P,
        "solver": stats.solver_name if stats else "unknown",
        "solve_time": stats.solve_time if stats else None,
    }
