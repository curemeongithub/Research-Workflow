"""Standard (non-parallel) 3-layer ReLU primal solver.

Architecture: d -> width -> width -> 1, no biases, ReLU.
Objective: (1/(2n)) ||y - f(X)||^2 + (beta/2) sum ||W||_F^2
(the `(1/2)` prefactor lives HERE, matching the convex-reformulation convention.)
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import torch
import torch.nn as nn


class StandardThreeLayerReLU(nn.Module):
    def __init__(self, d: int, width: int):
        super().__init__()
        self.fc1 = nn.Linear(d, width, bias=False)
        self.fc2 = nn.Linear(width, width, bias=False)
        self.fc3 = nn.Linear(width, 1, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        h1 = self.relu(self.fc1(x))
        h2 = self.relu(self.fc2(h1))
        return self.fc3(h2).squeeze(-1)


class StandardTwoLayerReLU(nn.Module):
    def __init__(self, d: int, width: int):
        super().__init__()
        self.fc1 = nn.Linear(d, width, bias=False)
        self.fc2 = nn.Linear(width, 1, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x))).squeeze(-1)


def _weight_decay(model: nn.Module, beta: float) -> torch.Tensor:
    total = torch.zeros((), dtype=torch.float32)
    for p in model.parameters():
        total = total + torch.sum(p ** 2)
    return 0.5 * beta * total


def train_standard_primal(X: np.ndarray, y: np.ndarray, *, d: int, width: int,
                          beta: float, n_restarts: int = 100, n_epochs: int = 3000,
                          lr: float = 1e-3, seed_base: int = 0,
                          arch: str = "three_layer", device: str = "cpu",
                          logger=None) -> dict:
    """Multi-restart Adam; return the restart with lowest final total loss."""
    torch.set_num_threads(1)  # critical when used inside multiprocessing.Pool
    X_t = torch.tensor(X, dtype=torch.float32, device=device)
    y_t = torch.tensor(y, dtype=torch.float32, device=device)
    n = X.shape[0]

    best_total = float("inf")
    best_data = None
    best_reg = None
    best_restart = -1
    best_state = None
    per_restart = []

    Model = StandardThreeLayerReLU if arch == "three_layer" else StandardTwoLayerReLU

    for r in range(n_restarts):
        torch.manual_seed(seed_base * 10000 + r + 1)
        model = Model(d, width).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=lr)

        for _ in range(n_epochs):
            opt.zero_grad()
            pred = model(X_t)
            data_loss = (0.5 / n) * torch.sum((y_t - pred) ** 2)
            reg_loss = _weight_decay(model, beta)
            total = data_loss + reg_loss
            total.backward()
            opt.step()

        ft = float(total.item())
        per_restart.append(ft)
        if ft < best_total:
            best_total = ft
            best_data = float(data_loss.item())
            best_reg = float(reg_loss.item())
            best_restart = r
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        del model, opt

    if logger is not None:
        logger.debug(
            f"train_standard_primal arch={arch} width={width} beta={beta} "
            f"restarts={n_restarts} best_restart={best_restart} best_total={best_total:.6e}"
        )

    return {
        "p_standard": best_total,
        "data_loss": best_data,
        "reg_loss": best_reg,
        "best_restart": best_restart,
        "per_restart_final_loss": per_restart,
        "best_state_dict": best_state,
    }
