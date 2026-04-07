"""
Quick verification of the beta mapping formula for the convex reformulation.
Tests both beta=2*lambda_2 and beta=2*sqrt(lambda_2) on a tiny problem.
"""
import numpy as np
import cvxpy as cp
import torch
import torch.nn as nn

np.random.seed(42)
torch.manual_seed(42)

# Tiny problem: n=20, d=2, width=3
n, d, width = 20, 2, 3
lambda_2 = 0.1

X = np.random.randn(n, d)
w_true = np.random.randn(d)
y = X @ w_true + 0.01 * np.random.randn(n)

X_t = torch.tensor(X, dtype=torch.float32)
y_t = torch.tensor(y, dtype=torch.float32)

class Net(nn.Module):
    def __init__(self, d, w):
        super().__init__()
        self.l1 = nn.Linear(d, w, bias=False)
        self.l2 = nn.Linear(w, 1, bias=False)
    def forward(self, x):
        return self.l2(torch.relu(self.l1(x))).squeeze(-1)

best_loss = float('inf')
best_data_loss = None
best_l2_sq = None
best_sum_products = None

for restart in range(200):
    torch.manual_seed(restart * 7 + 42)
    model = Net(d, width)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    for ep in range(3000):
        opt.zero_grad()
        pred = model(X_t)
        dl = (1/(2*n)) * torch.sum((y_t - pred)**2)
        l2 = sum(torch.sum(p**2) for p in model.parameters())
        loss = dl + lambda_2 * l2
        loss.backward()
        opt.step()
    with torch.no_grad():
        pred = model(X_t)
        dl = float((1/(2*n)) * torch.sum((y_t - pred)**2))
        l2 = float(sum(torch.sum(p**2) for p in model.parameters()))
        total = dl + lambda_2 * l2
        W1 = model.l1.weight.data.numpy()
        W2 = model.l2.weight.data.numpy()
        sum_prod = sum(np.linalg.norm(W1[k,:]) * abs(W2[0,k]) for k in range(width))
    if total < best_loss:
        best_loss = total
        best_data_loss = dl
        best_l2_sq = l2
        best_sum_products = sum_prod

print("Non-convex optimum:")
print(f"  data_loss = {best_data_loss:.6f}")
print(f"  L2_sq_norm = {best_l2_sq:.6f}")
print(f"  lambda_2 * L2_sq = {lambda_2 * best_l2_sq:.6f}")
print(f"  sum_k ||w1_k|| * |w2_k| = {best_sum_products:.6f}")
ratio = lambda_2 * best_l2_sq / (best_sum_products + 1e-12)
print(f"  lambda_2 * L2_sq / sum_products = {ratio:.6f}")
print(f"  2*lambda_2 = {2*lambda_2:.6f}")
print(f"  2*sqrt(lambda_2) = {2*np.sqrt(lambda_2):.6f}")
print(f"  sqrt(lambda_2) = {np.sqrt(lambda_2):.6f}")
print()

# Enumerate ALL activation patterns for n=20, d=2
all_patterns = set()
for _ in range(100000):
    v = np.random.randn(d)
    p = tuple((X @ v > 0).astype(int))
    all_patterns.add(p)
D_list = [np.diag(np.array(p, dtype=float)) for p in all_patterns]
P = len(D_list)
print(f"Total unique activation patterns: {P}")
print()

# Test both beta values
for beta_name, beta in [('2*lambda_2', 2*lambda_2), ('2*sqrt(lambda_2)', 2*np.sqrt(lambda_2)), ('sqrt(lambda_2)', np.sqrt(lambda_2))]:
    DX = [D @ X for D in D_list]
    u = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v = [cp.Variable(d, nonneg=True) for _ in range(P)]
    pred_cv = sum(DX[j] @ (u[j] - v[j]) for j in range(P))
    loss_cv = (1/(2*n)) * cp.sum_squares(y - pred_cv)
    reg_cv = beta * sum(cp.norm(u[j],2) + cp.norm(v[j],2) for j in range(P))
    prob = cp.Problem(cp.Minimize(loss_cv + reg_cv))
    prob.solve(solver=cp.SCS, eps=1e-9, max_iters=500000, verbose=False)

    u_vals = [u[j].value for j in range(P)]
    v_vals = [v[j].value for j in range(P)]
    pred_cv_val = np.zeros(n)
    for j in range(P):
        if u_vals[j] is not None and v_vals[j] is not None:
            pred_cv_val += D_list[j] @ X @ (u_vals[j] - v_vals[j])
    cv_data_loss = float(np.sum((y - pred_cv_val)**2) / (2*n))
    group_l1 = sum(np.linalg.norm(u_vals[j]) + np.linalg.norm(v_vals[j])
                   for j in range(P) if u_vals[j] is not None and v_vals[j] is not None)

    print(f"Convex (beta={beta_name}={beta:.4f}, P={P}, status={prob.status}):")
    print(f"  f_convex = {float(prob.value):.6f}")
    print(f"  data_loss = {cv_data_loss:.6f}")
    print(f"  group_L1_norm = {group_l1:.6f}")
    print(f"  beta * group_L1 = {beta*group_l1:.6f}")
    print(f"  rel_diff with nc: {abs(float(prob.value) - best_loss)/max(best_loss,1e-12)*100:.2f}%")
    print()
