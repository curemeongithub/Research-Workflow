"""
H6 Utilities: Data generation, seed management, and metric computation.
"""
import numpy as np
import torch
import random


def set_all_seeds(seed):
    """Set numpy, torch, and random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    random.seed(seed)


def generate_gaussian_data(n, d, seed, noise_std=0.1):
    """
    Generate synthetic regression data.
    X ~ N(0, I_d) in R^{n x d}
    w_true ~ N(0, I_d)
    y = X @ w_true + noise, noise ~ N(0, noise_std)
    Returns: X (n,d), y (n,), w_true (d,) as numpy arrays
    """
    set_all_seeds(seed)
    X = np.random.randn(n, d)
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = X @ w_true + noise
    return X, y, w_true


def normalized_gap(f_test, f_reference):
    """
    Compute (f_test - f_reference) / f_test.
    Positive means f_test > f_reference (reference is better under test objective).
    """
    if abs(f_test) < 1e-12:
        return 0.0
    return (f_test - f_reference) / f_test
