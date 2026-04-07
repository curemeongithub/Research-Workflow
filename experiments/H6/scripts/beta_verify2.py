"""
Careful beta verification with larger lambda_2 to force heavier regularization.
Also verify with n=100, d=2, width=3 (clearly underparameterized: 23 params / 100 points).
Key question: is beta = 2*lambda_2 correct?

Reference: Pilanci & Ergen (2020) Lemma 2 / Theorem 1:
The non-convex problem:
    min_{W1, W2} (1/2n)||y - W2 ReLU(W1 X)||^2 + lambda * (||W1||_F^2 + ||W2||^2)
is equivalent to the convex problem:
    min_{u_j, v_j >= 0} (1/2n)||y - sum_j D_j X (u_j - v_j)||^2 + 2*lambda * sum_j (||u_j||_2 + ||v_j||_2) / 2
Wait -- let me check the exact scaling in the paper...

Actually the variational representation is:
    ||W1||_F^2 + ||W2||^2 = min_{W1,W2: W2 ReLU(W1 x) = f(x)} sum_k ||w1_k||^2 + |w2_k|^2
by AM-GM: ||w1_k||^2 + |w2_k|^2 >= 2 * ||w1_k|| * |w2_k|, equality when ||w1_k|| = |w2_k|.

So the regularizer becomes:
    lambda * sum_k (||w1_k||^2 + |w2_k|^2) >= lambda * 2 * sum_k ||w1_k|| * |w2_k|
    = 2*lambda * sum_k ||w1_k|| * |w2_k|

And the group-L1 in the convex program is: beta * sum_j (||u_j|| + ||v_j||)
where each (u_j, v_j) corresponds to virtual neurons from the lifting.

From Pilanci-Ergen Lemma 2: the lifting gives u_j = alpha_j * D_j^{1/2} w_1, etc.
where alpha_j = sqrt(||w2_k||) and the constraint pattern matches D_j.

After the lifting, the L2-squared regularizer of the non-convex parameters equals:
    sum_j (||u_j||_2 + ||v_j||_2) (the group-L1 norm in the convex variables)

So: lambda * ||W||^2 = lambda * sum_j (||u_j||_2 + ||v_j||_2)
=> beta = lambda (NOT 2*lambda)

Wait, this contradicts my earlier calculation. Let me verify numerically very carefully.
"""
import numpy as np
import cvxpy as cp
import torch
import torch.nn as nn

np.random.seed(0)
torch.manual_seed(0)

# n=100, d=2, width=2 (only 6 params vs 100 points -- very underparameterized)
n, d, width = 100, 2, 2
lambda_2 = 0.5  # large regularization to avoid near-zero loss

X = np.random.randn(n, d)
w_true = np.random.randn(d)
y = X @ w_true  # no noise to make ground truth cleaner

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
best_W1 = None
best_W2 = None

for restart in range(1000):
    torch.manual_seed(restart)
    model = Net(d, width)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    for ep in range(10000):
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
        best_data_loss = dl
        best_l2_sq = l2
        best_sum_products = sum_prod
        best_W1 = W1.copy()
        best_W2 = W2.copy()

print("Non-convex optimum:")
print(f"  data_loss = {best_data_loss:.8f}")
print(f"  L2_sq_norm = {best_l2_sq:.8f}")
print(f"  lambda_2 * L2_sq = {lambda_2 * best_l2_sq:.8f}")
print(f"  sum_k ||w1_k|| * |w2_k| = {best_sum_products:.8f}")
ratio = lambda_2 * best_l2_sq / (best_sum_products + 1e-12)
print(f"  lambda_2 * L2_sq / sum_products = {ratio:.8f}")
print(f"  => beta should be: {ratio:.8f}")
print(f"  lambda_2 = {lambda_2:.6f}")
print(f"  2*lambda_2 = {2*lambda_2:.6f}")
print(f"  2*sqrt(lambda_2) = {2*np.sqrt(lambda_2):.6f}")
print()
for k in range(width):
    print(f"  Neuron {k}: ||w1_k||={np.linalg.norm(best_W1[k,:]):.6f}, |w2_k|={abs(best_W2[0,k]):.6f}")
print()

# Enumerate all patterns for n=100, d=2
all_patterns = set()
for _ in range(100000):
    v = np.random.randn(d)
    p = tuple((X @ v > 0).astype(int))
    all_patterns.add(p)
D_list = [np.diag(np.array(p, dtype=float)) for p in all_patterns]
P = len(D_list)
print(f"Total unique activation patterns: {P}")
print()

# Test multiple beta values
for beta_name, beta in [
    ('lambda_2', lambda_2),
    ('2*lambda_2', 2*lambda_2),
    ('2*sqrt(lambda_2)', 2*np.sqrt(lambda_2)),
    ('sqrt(lambda_2)', np.sqrt(lambda_2)),
    ('ratio_found', ratio),
]:
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

    print(f"Convex (beta={beta_name}={beta:.4f}, status={prob.status}):")
    print(f"  f_convex = {float(prob.value):.8f}, nc_total = {best_loss:.8f}")
    print(f"  data_loss = {cv_data_loss:.8f}")
    print(f"  group_L1_norm = {group_l1:.8f}, beta*gL1 = {beta*group_l1:.8f}")
    print(f"  rel_diff with nc: {abs(float(prob.value) - best_loss)/max(best_loss,1e-12)*100:.4f}%")
    print()
