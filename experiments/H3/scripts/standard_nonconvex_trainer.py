"""Standard (non-parallel) 3-layer ReLU non-convex primal trainer.

Architecture: d -> width -> width -> 1, no biases, ReLU.
Objective: (1/(2n)) ||y - f(X)||^2 + beta * sum ||W||_F^2

Note: The regularisation coefficient here is `beta * ||theta||_2^2` (no 1/2
prefactor) matching the roadmap pseudocode.  The convex lower bound uses
beta_convex = 2 * sqrt(beta) accordingly.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


class ThreeLayerReLU(nn.Module):
    """
    Standard (non-parallel) 3-layer ReLU: d -> width -> width -> 1.
    No bias in any layer (matches the standard convex reformulation setup).
    """

    def __init__(self, d: int, width: int):
        super().__init__()
        self.layer1 = nn.Linear(d, width, bias=False)
        self.layer2 = nn.Linear(width, width, bias=False)
        self.layer3 = nn.Linear(width, 1, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        h1 = self.relu(self.layer1(x))
        h2 = self.relu(self.layer2(h1))
        return self.layer3(h2).squeeze(-1)


def l2_squared_penalty(model: nn.Module) -> torch.Tensor:
    """Sum of squared Frobenius norms across all weight matrices."""
    total = torch.zeros((), dtype=torch.float32)
    for p in model.parameters():
        total = total + torch.sum(p ** 2)
    return total


def train_standard_3layer(X: np.ndarray, y: np.ndarray, *, d: int, width: int,
                          beta: float, n_restarts: int = 50, n_epochs: int = 2000,
                          lr: float = 1e-3, seed_base: int = 0,
                          device: str = "cpu") -> tuple:
    """
    Train a standard 3-layer ReLU with L2-squared weight decay (beta).

    Objective:
        f(theta) = (1 / (2n)) * ||y - net(X)||^2 + beta * ||theta||_2^2

    Multi-restart Adam; return the BEST final loss across restarts.

    Args:
        X: (n, d) numpy array
        y: (n,)   numpy array
        d: input dimension
        width: hidden layer width (both hidden layers use this width)
        beta: L2-squared regularization strength
        n_restarts: number of random initializations
        n_epochs: training epochs per restart
        lr: Adam learning rate
        seed_base: base seed; restart i uses torch seed seed_base*1000 + i
        device: 'cpu' or 'mps'
    Returns:
        best_loss: float, best total (data + reg) loss across restarts
        best_state: state dict achieving best loss
    """
    torch.set_num_threads(1)
    X_t = torch.tensor(X, dtype=torch.float32, device=device)
    y_t = torch.tensor(y, dtype=torch.float32, device=device)
    n = X.shape[0]

    best_loss = float("inf")
    best_state = None

    for restart in range(n_restarts):
        torch.manual_seed(seed_base * 1000 + restart)
        model = ThreeLayerReLU(d, width).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        for _ in range(n_epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = beta * l2_squared_penalty(model)
            total_loss = data_loss + reg_loss
            total_loss.backward()
            optimizer.step()

        final = float(total_loss.item())
        if final < best_loss:
            best_loss = final
            best_state = {k: v.detach().cpu().clone()
                          for k, v in model.state_dict().items()}

        del model, optimizer

    return best_loss, best_state
