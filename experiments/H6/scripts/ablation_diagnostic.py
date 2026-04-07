"""
H6 Ablation Diagnostic Script.

Investigates why the convex L2 solver still fails even in the underparameterized
regime (width=10, n=200). Checks:
1. The actual data loss breakdown for both solvers
2. Whether data-dependent pattern sampling (using trained non-convex activation
   patterns as seeds) closes the gap
3. The correct criterion (b) via full weight reconstruction from convex (u,v) pairs
4. The formula for l2_equiv_norm

This is a diagnostic only -- the reviewer will use these numbers to adjust the fix.

Run from project root:
    .venv/bin/python experiments/H6/scripts/ablation_diagnostic.py
"""
import json
import os
import sys
import traceback

import numpy as np

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from utils import set_all_seeds, generate_gaussian_data

RESULTS_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), 'results')

N = 200
D = 10
LAMBDA_2 = 0.01
LAMBDA_1 = 0.0
WIDTH = 10
BETA_CONVEX = 2.0 * np.sqrt(LAMBDA_2)
MAX_PATTERNS = 500


def analyze_seed(seed):
    import torch
    import torch.nn as nn
    import cvxpy as cp

    set_all_seeds(seed)
    X, y, w_true = generate_gaussian_data(N, D, seed)
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)

    print(f"\n=== Seed {seed} Diagnostic ===")

    # Train a single non-convex network to convergence
    class TwoLayerReLU(nn.Module):
        def __init__(self, d, width):
            super().__init__()
            self.layer1 = nn.Linear(d, width, bias=False)
            self.relu = nn.ReLU()
            self.layer2 = nn.Linear(width, 1, bias=False)
        def forward(self, x):
            return self.layer2(self.relu(self.layer1(x))).squeeze(-1)

    torch.manual_seed(seed * 1000)
    model = TwoLayerReLU(D, WIDTH)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    for epoch in range(8000):
        if epoch == 2000:
            for pg in optimizer.param_groups:
                pg['lr'] = 0.0005
        optimizer.zero_grad()
        pred = model(X_t)
        data_loss = (1.0 / (2 * N)) * torch.sum((y_t - pred) ** 2)
        l2_reg = sum(torch.sum(p**2) for p in model.parameters())
        total = data_loss + LAMBDA_2 * l2_reg
        total.backward()
        optimizer.step()

    with torch.no_grad():
        nc_pred = model(X_t).numpy()
        nc_data_loss = float((1.0 / (2 * N)) * torch.sum((y_t - model(X_t)) ** 2))
        nc_l2_reg = float(sum(torch.sum(p**2) for p in model.parameters()))
    nc_total = nc_data_loss + LAMBDA_2 * nc_l2_reg
    print(f"  Non-convex: data_loss={nc_data_loss:.6f}, L2_reg={nc_l2_reg:.6f}, "
          f"total={nc_total:.6f}")

    # Extract activation patterns from trained non-convex model
    with torch.no_grad():
        hidden = model.layer1(X_t)
        activations = (hidden > 0).numpy().astype(float)  # (n, width)

    print(f"  Non-convex activation patterns (width={WIDTH} unique per-neuron):")
    unique_patterns = set(tuple(row) for row in activations)
    print(f"    {len(unique_patterns)} unique activation patterns across {N} samples")
    nc_activation_array = activations  # (n, width), column j = activation of neuron j

    # Build D_list from non-convex activations (data-dependent)
    D_list_datadep = []
    for j in range(WIDTH):
        diag_j = activations[:, j]  # 0/1 per sample
        D_list_datadep.append(np.diag(diag_j))
    # Also add random patterns
    rng = np.random.RandomState(seed)
    D_list_random = []
    seen = set()
    for _ in range(MAX_PATTERNS * 20):
        v = rng.randn(D)
        pattern = tuple((X @ v > 0).astype(int))
        if pattern not in seen:
            seen.add(pattern)
            D_list_random.append(np.diag(np.array(pattern, dtype=float)))
            if len(D_list_random) >= MAX_PATTERNS - WIDTH:
                break
    D_list_combined = D_list_datadep + D_list_random
    print(f"  Combined pattern set: {len(D_list_datadep)} data-dep + "
          f"{len(D_list_random)} random = {len(D_list_combined)} total")

    # Solve convex with data-dependent patterns
    for label, D_list in [('random_500', None), ('combined', D_list_combined)]:
        if D_list is None:
            # Use random patterns from convex_l2_solver
            from convex_l2_solver import enumerate_sign_patterns, solve_convex_l2
            f_cv, cv_weights = solve_convex_l2(X, y, beta=BETA_CONVEX,
                                                max_patterns=MAX_PATTERNS,
                                                solver_eps=1e-8, seed=seed)
            print(f"  Convex ({label}): f={f_cv:.6f}, data_loss={0:.6f}")
            # recompute data loss from predictions
            u_list = cv_weights['u']
            v_list = cv_weights['v']
            D_list_used = cv_weights['D_list']
            pred_cv = np.zeros(N)
            for jj, D_jj in enumerate(D_list_used):
                u_j = u_list[jj]
                v_j = v_list[jj]
                if u_j is not None and v_j is not None:
                    pred_cv += D_jj @ X @ (u_j - v_j)
            cv_data_loss = float(np.sum((y - pred_cv)**2) / (2 * N))
            group_l1_norm = sum(np.linalg.norm(u_list[jj]) + np.linalg.norm(v_list[jj])
                                for jj in range(len(D_list_used))
                                if u_list[jj] is not None and v_list[jj] is not None)
            cv_l2_equiv = LAMBDA_2 * group_l1_norm  # proxy
            print(f"  Convex ({label}): f={f_cv:.6f}, data_loss={cv_data_loss:.6f}, "
                  f"group_L1={group_l1_norm:.6f}, lambda2*proxy={cv_l2_equiv:.6f}")
            print(f"  -> f_convex_l2_only (wrong proxy)={cv_data_loss + cv_l2_equiv:.6f}")
            print(f"  -> f_convex direct (correct)={cv_data_loss + BETA_CONVEX*group_l1_norm:.6f} "
                  f"[should match f_cv={f_cv:.6f}]")
        else:
            # Solve convex with combined patterns
            P = len(D_list)
            DX_list = [D_list[j] @ X for j in range(P)]
            u = [cp.Variable(D, nonneg=True) for _ in range(P)]
            v = [cp.Variable(D, nonneg=True) for _ in range(P)]
            pred_cp = sum(DX_list[j] @ (u[j] - v[j]) for j in range(P))
            loss_cp = (1.0 / (2 * N)) * cp.sum_squares(y - pred_cp)
            reg_cp = BETA_CONVEX * sum(cp.norm(u[j], 2) + cp.norm(v[j], 2) for j in range(P))
            prob = cp.Problem(cp.Minimize(loss_cp + reg_cp))
            try:
                prob.solve(solver=cp.SCS, eps=1e-8, max_iters=100000, verbose=False)
                f_cv = float(prob.value)
                # compute data loss and L2 proxy
                pred_cv = np.zeros(N)
                group_l1_norm = 0.0
                for jj in range(P):
                    u_j = u[jj].value
                    v_j = v[jj].value
                    if u_j is not None and v_j is not None:
                        pred_cv += D_list[jj] @ X @ (u_j - v_j)
                        group_l1_norm += np.linalg.norm(u_j) + np.linalg.norm(v_j)
                cv_data_loss = float(np.sum((y - pred_cv)**2) / (2 * N))
                cv_l2_equiv = LAMBDA_2 * group_l1_norm
                print(f"  Convex ({label}): f={f_cv:.6f}, data_loss={cv_data_loss:.6f}, "
                      f"group_L1={group_l1_norm:.6f}, lambda2*proxy={cv_l2_equiv:.6f}")
                print(f"  -> f_convex_l2_only (wrong proxy)={cv_data_loss + cv_l2_equiv:.6f}")
                print(f"  -> Gap with non-convex L2 total: "
                      f"{abs(cv_data_loss + cv_l2_equiv - nc_total)/nc_total*100:.2f}%")
            except Exception as e:
                print(f"  Convex ({label}) FAILED: {e}")

    # What is the correct L2 norm of the non-convex weights?
    W1 = model.layer1.weight.data.numpy()  # (width, d)
    W2 = model.layer2.weight.data.numpy()  # (1, width)
    nc_l2_true = float(np.sum(W1**2) + np.sum(W2**2))
    print(f"\n  Non-convex true L2_sq = {nc_l2_true:.6f}")
    print(f"  lambda_2 * L2_sq = {LAMBDA_2 * nc_l2_true:.6f}")
    print(f"  Non-convex data_loss = {nc_data_loss:.6f}")
    print(f"  Non-convex total = {nc_data_loss + LAMBDA_2*nc_l2_true:.6f}")

    # Norm-balance check
    for k in range(WIDTH):
        w1k = W1[k, :]
        w2k = W2[0, k]
        print(f"  Neuron {k}: ||w1_k||={np.linalg.norm(w1k):.4f}, |w2_k|={abs(w2k):.4f}, "
              f"product={np.linalg.norm(w1k)*abs(w2k):.4f}")

    return {
        'seed': seed,
        'nc_data_loss': nc_data_loss,
        'nc_l2_reg': LAMBDA_2 * nc_l2_true,
        'nc_total': nc_data_loss + LAMBDA_2 * nc_l2_true,
    }


def main():
    print("=" * 60)
    print("H6 Ablation Diagnostic: investigating convex/non-convex gap")
    print("=" * 60)

    results = []
    for seed in [0, 1]:
        try:
            res = analyze_seed(seed)
            results.append(res)
        except Exception as e:
            print(f"Seed {seed} failed: {e}")
            traceback.print_exc()

    out_path = os.path.join(RESULTS_DIR, 'ablation_diagnostic.json')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDiagnostic saved to {out_path}")


if __name__ == '__main__':
    main()
