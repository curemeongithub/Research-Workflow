"""H5 shared utilities: seeds, rank-controlled data, metrics, logging.

Reused by H3 via a sys.path injection.
"""
from __future__ import annotations

import logging
import os
import random
import sys
from typing import Optional

import numpy as np
import torch


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_LOGGER_CACHE: dict = {}


def get_logger(name: str = "experiment", log_file: Optional[str] = None,
               level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger that writes to stdout and (optionally) a file.

    Safe to call multiple times: handlers are only added once per (name, file).
    """
    key = (name, log_file)
    if key in _LOGGER_CACHE:
        return _LOGGER_CACHE[key]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter(
        "[%(asctime)s][%(processName)s][%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Clear any stale handlers (safe in worker re-imports)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, mode="a")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    _LOGGER_CACHE[key] = logger
    return logger


# ---------------------------------------------------------------------------
# Seeds and data
# ---------------------------------------------------------------------------


def set_all_seeds(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    random.seed(seed)


def generate_rank_controlled_data(n: int, d: int, rank: int, seed: int,
                                  noise_std: float = 0.1):
    """X = A B^T with rank r, y = X w_true + noise."""
    assert 1 <= rank <= min(n, d), f"rank {rank} out of range for n={n} d={d}"
    set_all_seeds(seed)
    A = np.random.randn(n, rank)
    B = np.random.randn(d, rank)
    X = (A @ B.T).astype(np.float64)
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = (X @ w_true + noise).astype(np.float64)
    eff = int(np.linalg.matrix_rank(X, tol=1e-8))
    assert eff == rank, f"effective rank {eff} != requested {rank} (seed={seed})"
    return X, y, w_true, eff


def normalized_gap(p_primal: float, d_lower: float) -> float:
    if abs(p_primal) < 1e-12:
        return 0.0
    return (p_primal - d_lower) / p_primal
