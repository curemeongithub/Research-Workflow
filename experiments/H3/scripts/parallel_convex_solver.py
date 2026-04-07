"""Parallel-architecture convex (lower-bound) solver via CVXPY.

Implements the parallel 3-layer ReLU convex reformulation from
WangErgenPilanci2021 as a two-layer-style group-l1 convex program.

Objective convention (must match standard_nonconvex_trainer.py):
  Primal:     (1/(2n))||y - f_standard(X)||^2  +  beta * ||theta||_F^2
  Convex LB:  (1/(2n))||y - sum_j D_j X (u_j - v_j)||^2
                         +  beta * sum_j (||u_j||_2 + ||v_j||_2)

Using beta_convex = beta keeps the same regularization scale on both sides,
which is necessary for the convex value to be a valid lower bound on the
primal (same objective, larger feasible set -> smaller or equal minimum).

The roadmap's "2*sqrt(beta)" rescaling is the theoretically tightest
coefficient for the weight-magnitude-balanced case (WangErgenPilanci2021
Theorem 3), but that theorem assumes (beta/2)||W||^2 normalization. When the
primal uses beta * ||theta||^2 (no 1/2 factor), the direct correspondence
is beta_convex = beta for a valid lower bound.  We use beta_convex = beta.
"""
from __future__ import annotations

from typing import List, Tuple

import cvxpy as cp
import numpy as np


def enumerate_sign_patterns(X: np.ndarray, max_patterns: int = 150,
                            rng_seed: int = 0) -> List[np.ndarray]:
    """
    Sample ReLU activation patterns by drawing random hyperplane normals.

    For each random v ~ N(0, I_d), compute the sign pattern (X @ v > 0)
    and add the corresponding 0/1 mask to the pattern list.
    Deduplicates. Caps at max_patterns.

    Returns:
        List of (n,) int8 arrays.
    """
    rng = np.random.default_rng(rng_seed)
    n, d = X.shape
    seen = set()
    out: List[np.ndarray] = []
    budget = max_patterns * 20
    for _ in range(budget):
        v = rng.standard_normal(d)
        pattern = (X @ v > 0).astype(np.int8)
        key = pattern.tobytes()
        if key not in seen:
            seen.add(key)
            out.append(pattern)
            if len(out) >= max_patterns:
                break
    # Always add all-ones pattern to ensure feasibility
    all_ones = np.ones(n, dtype=np.int8)
    if all_ones.tobytes() not in seen:
        out.append(all_ones)
        seen.add(all_ones.tobytes())
    return out


def solve_parallel_convex_3layer(X: np.ndarray, y: np.ndarray, *, beta: float,
                                 max_patterns: int = 150, solver_eps: float = 1e-8,
                                 pattern_seed: int = 0) -> Tuple[float, dict]:
    """
    Solve the parallel-architecture convex lower bound for 3-layer ReLU.

    Convex program (two-layer group-l1 form):
        min_{u_j, v_j} (1/2n) ||y - sum_j D_j X (u_j - v_j)||^2
                        + beta * sum_j (||u_j||_2 + ||v_j||_2)
        s.t. u_j >= 0, v_j >= 0

    where D_j are sampled diagonal activation patterns (0/1 masks) and
    beta_convex = beta (same regularization scale as the standard primal).

    This is a valid lower bound because:
      1. The parallel architecture has zero duality gap (WangErgenPilanci2021).
      2. The parallel architecture's feasible function class is a superset of
         the standard 3-layer ReLU's function class (at matched width).
      3. Same objective, larger feasible set => convex optimum <= primal optimum.

    Args:
        X: (n, d) numpy array
        y: (n,)   numpy array
        beta: L2-squared weight decay (same value as used in the primal)
        max_patterns: how many unique sign patterns to sample
        solver_eps: SCS epsilon tolerance
        pattern_seed: seed for sign-pattern sampling
    Returns:
        D_parallel: float, optimal objective value
        meta: dict with solver status, num_patterns, solver stats
    """
    n, d = X.shape

    # Use same regularization coefficient as the primal (valid LB condition)
    beta_convex = beta

    patterns = enumerate_sign_patterns(X, max_patterns=max_patterns,
                                       rng_seed=pattern_seed)
    P = len(patterns)

    u_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]

    # Build prediction: sum_j diag(D_j) * X * (u_j - v_j)
    pred_terms = []
    for j in range(P):
        mask = patterns[j].astype(np.float64)  # (n,)
        DX = mask[:, None] * X                  # (n, d)
        pred_terms.append(DX @ (u_vars[j] - v_vars[j]))
    pred = cp.sum(pred_terms)

    data_loss = (0.5 / n) * cp.sum_squares(y - pred)
    reg = beta_convex * cp.sum([cp.norm(u_vars[j], 2) + cp.norm(v_vars[j], 2)
                                for j in range(P)])
    prob = cp.Problem(cp.Minimize(data_loss + reg))

    # Try SCS first, fall back to CLARABEL
    prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=50000, verbose=False)

    if prob.status not in ("optimal", "optimal_inaccurate"):
        try:
            prob.solve(solver=cp.CLARABEL, verbose=False)
        except Exception:
            pass

    if prob.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"CVXPY solver failed: status={prob.status}")

    stats = prob.solver_stats
    return float(prob.value), {
        "status": prob.status,
        "num_patterns": P,
        "solver_stats": {
            "num_iters": getattr(stats, "num_iters", None),
            "solve_time": getattr(stats, "solve_time", None),
        },
    }
