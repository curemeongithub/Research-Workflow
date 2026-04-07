"""H3 shared utilities: seeds, rank-controlled data generation, metrics."""
from __future__ import annotations

import random

import numpy as np
import torch


def set_all_seeds(seed: int) -> None:
    """Set numpy, torch, and random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    random.seed(seed)


def generate_rank_controlled_data(n: int, d: int, r: int, seed: int,
                                  noise_std: float = 0.1):
    """
    Generate synthetic regression data with EXACT rank r.

    Construction:
        A ~ N(0, I) in R^{n x r}
        B ~ N(0, I) in R^{d x r}
        X = A @ B.T   (shape (n, d), rank min(r, min(n, d)))

    Targets:
        w_true ~ N(0, I_d)
        noise  ~ N(0, noise_std^2 I_n)
        y = X @ w_true + noise

    Args:
        n: number of samples
        d: ambient dimension
        r: target rank (must satisfy 1 <= r <= min(n, d))
        seed: RNG seed
        noise_std: Gaussian noise std for targets
    Returns:
        X: (n, d) float64 numpy array, np.linalg.matrix_rank(X) == r
        y: (n,)  float64 numpy array
        w_true: (d,) float64 numpy array
    """
    assert 1 <= r <= min(n, d), f"rank r={r} out of range for (n={n}, d={d})"
    set_all_seeds(seed)
    A = np.random.randn(n, r)
    B = np.random.randn(d, r)
    X = (A @ B.T).astype(np.float64)
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = (X @ w_true + noise).astype(np.float64)
    # Sanity check: numerically verify rank
    true_rank = int(np.linalg.matrix_rank(X, tol=1e-8))
    assert true_rank == r, f"Constructed rank {true_rank} != requested {r}"
    return X, y, w_true


def normalized_gap(P: float, D: float) -> float:
    """
    Normalized gap between primal P and dual lower bound D:
        gap = (P - D) / P

    Positive means primal > dual (expected: primal is always >= dual).
    Clamped at 0 if |P| < 1e-12 to avoid division by near-zero.
    """
    if abs(P) < 1e-12:
        return 0.0
    return (P - D) / P
