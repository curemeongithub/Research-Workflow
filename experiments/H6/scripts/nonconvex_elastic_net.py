"""
H6: Non-Convex Elastic Net Training.

Trains a two-layer ReLU network with elastic net regularization using
Adam optimizer with multiple random restarts.
"""
import torch
import torch.nn as nn
import numpy as np


class TwoLayerReLU(nn.Module):
    """Two-layer ReLU network: input -> Linear(d, width) -> ReLU -> Linear(width, 1)"""

    def __init__(self, d, width):
        super().__init__()
        self.layer1 = nn.Linear(d, width, bias=False)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(width, 1, bias=False)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x))).squeeze(-1)


def elastic_net_penalty(model, lambda_1, lambda_2):
    """
    Compute elastic net penalty: lambda_1 * sum|w| + lambda_2 * sum(w^2)
    Applied to ALL weights in the network (both layers).
    """
    l1_term = 0.0
    l2_term = 0.0
    for param in model.parameters():
        l1_term = l1_term + torch.sum(torch.abs(param))
        l2_term = l2_term + torch.sum(param ** 2)
    return lambda_1 * l1_term + lambda_2 * l2_term


def train_elastic_net(X, y, d, width, lambda_1, lambda_2,
                      n_restarts=50, n_epochs=3000, lr=0.001, seed_base=0):
    """
    Train two-layer ReLU with elastic net regularization.
    Multiple random restarts; return best (lowest total loss).

    Args:
        X: (n, d) numpy array
        y: (n,) numpy array
        d: input dimension
        width: hidden layer width
        lambda_1: L1 regularization strength
        lambda_2: L2-squared regularization strength
        n_restarts: number of random initializations
        n_epochs: training epochs per restart
        lr: Adam learning rate
        seed_base: base seed (restart i uses seed_base * 1000 + i)
    Returns:
        best_loss: float, best total loss (data + regularization)
        best_state_dict: model weights achieving best loss
    """
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    n = X.shape[0]

    best_loss = float('inf')
    best_state_dict = None

    for restart in range(n_restarts):
        torch.manual_seed(seed_base * 1000 + restart)
        model = TwoLayerReLU(d, width)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        for epoch in range(n_epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = elastic_net_penalty(model, lambda_1, lambda_2)
            total_loss = data_loss + reg_loss
            total_loss.backward()
            optimizer.step()

        final_loss = total_loss.item()
        if final_loss < best_loss:
            best_loss = final_loss
            best_state_dict = {k: v.clone() for k, v in model.state_dict().items()}

    return best_loss, best_state_dict


def compute_elastic_net_loss_from_state(X, y, state_dict, d, width, lambda_1, lambda_2):
    """
    Compute elastic net loss for a given state dict.
    Used to evaluate convex solution weights under the elastic net objective.
    """
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    n = X.shape[0]

    model = TwoLayerReLU(d, width)
    model.load_state_dict(state_dict)
    model.eval()

    with torch.no_grad():
        pred = model(X_t)
        data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
        reg_loss = elastic_net_penalty(model, lambda_1, lambda_2)
        total_loss = data_loss + reg_loss

    return float(total_loss.item())
