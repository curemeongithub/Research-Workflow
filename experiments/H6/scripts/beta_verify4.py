"""
Beta formula verification: lambda_2=0.1 (so 2*lambda_2=0.2, 2*sqrt=0.632, differ significantly).
n=30, d=2, width=2 -- tiny problem to enumerate all patterns.
"""
import numpy as np
import cvxpy as cp
import torch
import torch.nn as nn
import sys

np.random.seed(1)
torch.manual_seed(1)

n, d, width = 30, 2, 2
lambda_2 = 0.1

X = np.random.randn(n, d)
w_true = np.random.randn(d)
y = X @ w_true  # no noise -> ground truth is linear

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
best_l2_sq = None
best_sum_products = None

for restart in range(300):
    torch.manual_seed(restart * 13)
    model = Net(d, width)
    opt = torch.optim.Adam(model.parameters(), lr=0.003)
    for ep in range(15000):
        if ep == 5000:
            for pg in opt.param_groups: pg['lr'] = 0.0005
        if ep == 10000:
            for pg in opt.param_groups: pg['lr'] = 0.0001
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
        W1 = model.l1.weight.data.numpy().copy()
        W2 = model.l2.weight.data.numpy().copy()
        sum_prod = sum(np.linalg.norm(W1[k,:]) * abs(W2[0,k]) for k in range(width))
    if total < best_loss:
        best_loss = total
        best_l2_sq = l2
        best_sum_products = sum_prod
        best_dl = dl

print("Non-convex optimum (300 restarts x 15000 epochs):")
print(f"  data_loss = {best_dl:.8f}")
print(f"  L2_sq_norm = {best_l2_sq:.8f}")
print(f"  lambda_2 * L2_sq = {lambda_2 * best_l2_sq:.8f}")
print(f"  sum_k ||w1_k|| * |w2_k| = {best_sum_products:.8f}")
ratio = lambda_2 * best_l2_sq / (best_sum_products + 1e-12)
print(f"  ratio (lambda_2 * L2_sq / sum_products) = {ratio:.8f}")
print(f"  2*lambda_2 = {2*lambda_2:.6f}")
print(f"  2*sqrt(lambda_2) = {2*np.sqrt(lambda_2):.6f}")
print(f"  nc total = {best_loss:.8f}")
sys.stdout.flush()

# Enumerate all patterns
all_patterns = set()
for _ in range(100000):
    v = np.random.randn(d)
    p = tuple((X @ v > 0).astype(int))
    all_patterns.add(p)
D_list = [np.diag(np.array(p, dtype=float)) for p in all_patterns]
P = len(D_list)
print(f"\nTotal unique activation patterns: {P}")
sys.stdout.flush()

for beta_name, beta in [
    ('2*lambda_2', 2*lambda_2),
    ('2*sqrt(lambda_2)', 2*np.sqrt(lambda_2)),
]:
    DX = [D @ X for D in D_list]
    u = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v_var = [cp.Variable(d, nonneg=True) for _ in range(P)]
    pred_cv = sum(DX[j] @ (u[j] - v_var[j]) for j in range(P))
    loss_cv = (1/(2*n)) * cp.sum_squares(y - pred_cv)
    reg_cv = beta * sum(cp.norm(u[j],2) + cp.norm(v_var[j],2) for j in range(P))
    prob = cp.Problem(cp.Minimize(loss_cv + reg_cv))
    prob.solve(solver=cp.SCS, eps=1e-10, max_iters=1000000, verbose=False)

    u_vals = [u[j].value for j in range(P)]
    v_vals = [v_var[j].value for j in range(P)]
    pred_cv_val = np.zeros(n)
    for j in range(P):
        if u_vals[j] is not None and v_vals[j] is not None:
            pred_cv_val += D_list[j] @ X @ (u_vals[j] - v_vals[j])
    cv_dl = float(np.sum((y - pred_cv_val)**2) / (2*n))
    group_l1 = sum(np.linalg.norm(u_vals[j]) + np.linalg.norm(v_vals[j])
                   for j in range(P) if u_vals[j] is not None and v_vals[j] is not None)

    print(f"\nConvex (beta={beta_name}={beta:.4f}, P={P}, status={prob.status}):")
    print(f"  f_convex = {float(prob.value):.8f}")
    print(f"  data_loss = {cv_dl:.8f}")
    print(f"  group_L1_norm = {group_l1:.8f}")
    print(f"  beta*gL1 = {beta*group_l1:.8f}")
    print(f"  rel_diff with nc total: {abs(float(prob.value) - best_loss)/max(best_loss,1e-12)*100:.4f}%")
    sys.stdout.flush()

print("\nDone.")
