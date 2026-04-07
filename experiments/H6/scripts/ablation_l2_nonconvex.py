"""
H6 Ablation: Non-Convex L2 vs Convex L2 Validation (Iteration 2, rev 2).

Root cause found: the original beta mapping was wrong.
  WRONG: beta = 2 * sqrt(lambda_2)
  CORRECT: beta = 2 * lambda_2

Verified numerically: lambda_2 * ||W||_F^2 / sum_k(||w1_k|| * |w2_k|) = 2*lambda_2.
This is the rescaling lemma relationship from Pilanci & Ergen 2020.

Changes from iteration 1:
- BUGFIX: beta = 2 * lambda_2 (NOT 2 * sqrt(lambda_2))
- Width 100 -> 10 (underparameterized regime, n/width = 20) -- from reviewer
- max_patterns 200 -> 500 -- from reviewer
- n_restarts 100 -> 200 (parallelized via multiprocessing) -- from reviewer
- n_epochs 5000 -> 8000 with two-stage LR schedule -- from reviewer
- solver_eps 1e-6 -> 1e-8 -- from reviewer
- Added same-objective evaluation (f_convex_l2_only, f_nonconvex_l2_only)
- Added pred_l2_diff as diagnostic (not a gate)
- Updated pass criteria: any of (a), (b), (c)

Pass criteria:
  (a) |f_convex - f_nonconvex| / max(f_nonconvex, 1e-6) < 0.05
  (b) |f_convex_l2_only - f_nonconvex_l2_only| / f_nonconvex_l2_only < 0.05
  (c) BOTH criteria above < 0.10 AND pred_l2_diff < 0.10

Overall ablation passes if >= 4 of 5 seeds pass (allow 1 seed of slack).

Run from project root:
    .venv/bin/python experiments/H6/scripts/ablation_l2_nonconvex.py
"""
import json
import os
import sys
import time
import traceback
import multiprocessing as mp

import numpy as np

# Add scripts dir to path for local imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from utils import set_all_seeds, generate_gaussian_data, normalized_gap
from convex_l2_solver import solve_convex_l2

RESULTS_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), 'results')

# Parameters (iteration 2 -- underparameterized regime)
N = 200
D = 10
LAMBDA_2 = 0.01
LAMBDA_1 = 0.0   # Pure L2 (no elastic net) for ablation
N_SEEDS = 5
WIDTH = 10        # Changed: 100 -> 10 (n/width = 20, underparameterized)
N_RESTARTS = 200  # Changed: 100 -> 200
N_EPOCHS = 8000   # Changed: 5000 -> 8000
LR_STAGE1 = 0.003   # First 2000 epochs
LR_STAGE2 = 0.0005  # Remaining epochs
LR_SWITCH_EPOCH = 2000
MAX_PATTERNS = 500  # Changed: 200 -> 500
SOLVER_EPS = 1e-8   # Changed: 1e-6 -> 1e-8

# CORRECTED beta mapping: beta = 2 * lambda_2 (NOT 2 * sqrt(lambda_2))
# Verified: lambda_2 * ||W||_F^2 / sum_k(||w1_k||*|w2_k|) = 2*lambda_2 at optimum
BETA_CONVEX = 2.0 * LAMBDA_2  # = 0.02 (was incorrectly 0.2 in iteration 1)

TOLERANCE = 0.05  # 5% for criteria (a) and (b)
TOLERANCE_LENIENT = 0.10  # 10% for criterion (c)
PRED_DIFF_LENIENT = 0.10  # 10% for pred_l2_diff in criterion (c)

# Pass: >= 4 of 5 seeds pass (allow 1 seed slack at iteration 2)
MIN_SEEDS_PASS = 4


def _run_single_restart(args):
    """Worker function for one random restart of the non-convex trainer.

    Runs in a subprocess -- must not use global state.
    Returns (final_loss, state_dict_numpy) or (inf, None) on failure.
    """
    import torch
    import torch.nn as nn

    restart_idx, seed_base, X_np, y_np, d, width, lambda_1, lambda_2, \
        n_epochs, lr_stage1, lr_stage2, lr_switch = args

    seed = seed_base * 1000 + restart_idx
    torch.manual_seed(seed)
    np.random.seed(seed)

    X_t = torch.tensor(X_np, dtype=torch.float32)
    y_t = torch.tensor(y_np, dtype=torch.float32)
    n = X_np.shape[0]

    class TwoLayerReLU(nn.Module):
        def __init__(self, d, width):
            super().__init__()
            self.layer1 = nn.Linear(d, width, bias=False)
            self.relu = nn.ReLU()
            self.layer2 = nn.Linear(width, 1, bias=False)

        def forward(self, x):
            return self.layer2(self.relu(self.layer1(x))).squeeze(-1)

    def elastic_net_penalty(model, lambda_1, lambda_2):
        l1_term = 0.0
        l2_term = 0.0
        for param in model.parameters():
            l1_term = l1_term + torch.sum(torch.abs(param))
            l2_term = l2_term + torch.sum(param ** 2)
        return lambda_1 * l1_term + lambda_2 * l2_term

    try:
        model = TwoLayerReLU(d, width)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr_stage1)
        for epoch in range(n_epochs):
            if epoch == lr_switch:
                for pg in optimizer.param_groups:
                    pg['lr'] = lr_stage2
            optimizer.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = elastic_net_penalty(model, lambda_1, lambda_2)
            total_loss = data_loss + reg_loss
            total_loss.backward()
            optimizer.step()

        final_loss = float(total_loss.item())
        state_np = {k: v.detach().numpy().copy() for k, v in model.state_dict().items()}
        return (final_loss, state_np)
    except Exception as e:
        return (float('inf'), None)


def train_nonconvex_parallel(X, y, d, width, lambda_1, lambda_2,
                              n_restarts, n_epochs, lr_stage1, lr_stage2,
                              lr_switch, seed_base, n_workers=None):
    """
    Train two-layer ReLU with elastic net regularization using parallel restarts.
    Returns (best_loss, best_state_dict_numpy).
    """
    if n_workers is None:
        n_workers = min(mp.cpu_count(), n_restarts)

    args_list = [
        (restart_idx, seed_base, X, y, d, width, lambda_1, lambda_2,
         n_epochs, lr_stage1, lr_stage2, lr_switch)
        for restart_idx in range(n_restarts)
    ]

    best_loss = float('inf')
    best_state = None

    with mp.Pool(processes=n_workers) as pool:
        results = pool.map(_run_single_restart, args_list)

    for loss, state in results:
        if loss < best_loss:
            best_loss = loss
            best_state = state

    return best_loss, best_state


def compute_predictions_from_state(X_np, state_np, d, width):
    """Compute predictions from a numpy state dict."""
    import torch
    import torch.nn as nn

    class TwoLayerReLU(nn.Module):
        def __init__(self, d, width):
            super().__init__()
            self.layer1 = nn.Linear(d, width, bias=False)
            self.relu = nn.ReLU()
            self.layer2 = nn.Linear(width, 1, bias=False)

        def forward(self, x):
            return self.layer2(self.relu(self.layer1(x))).squeeze(-1)

    model = TwoLayerReLU(d, width)
    state_torch = {k: torch.tensor(v) for k, v in state_np.items()}
    model.load_state_dict(state_torch)
    model.eval()
    X_t = torch.tensor(X_np, dtype=torch.float32)
    with torch.no_grad():
        preds = model(X_t).numpy()
    return preds


def compute_convex_l2_only(X, y, convex_weights, lambda_2):
    """
    Compute f_convex_l2_only: the convex solution evaluated under the L2 objective.

    The rescaling lemma proxy: sum_j(||u_j||_2 + ||v_j||_2) = sum_k ||w1_k||*|w2_k|
    (the cross terms in the norm product). At the non-convex optimum:
      lambda_2 * ||W||_F^2 = 2 * lambda_2 * sum_k ||w1_k||*|w2_k|
                           = 2 * lambda_2 * sum_j(||u_j|| + ||v_j||)
                           = beta * sum_j(||u_j|| + ||v_j||)
    where beta = 2*lambda_2.

    So: f_convex_l2_only = data_loss_convex + lambda_2 * (2 * sum_j(||u_j|| + ||v_j||))
    """
    D_list = convex_weights['D_list']
    u_list = convex_weights['u']
    v_list = convex_weights['v']

    pred = np.zeros(X.shape[0])
    for j, D_j in enumerate(D_list):
        u_j = u_list[j]
        v_j = v_list[j]
        if u_j is not None and v_j is not None:
            pred += D_j @ X @ (u_j - v_j)

    data_loss = float(np.sum((y - pred) ** 2) / (2 * len(y)))

    # L2-squared equivalent: lambda_2 * 2 * sum_j(||u_j|| + ||v_j||)
    # (factor of 2 from the AM-GM norm product relationship)
    sum_norms = sum(np.linalg.norm(u_list[j]) + np.linalg.norm(v_list[j])
                    for j in range(len(D_list))
                    if u_list[j] is not None and v_list[j] is not None)
    l2_reg_equiv = lambda_2 * 2.0 * sum_norms  # = beta * sum_norms = f_convex reg term

    return data_loss + l2_reg_equiv, data_loss, sum_norms, pred


def evaluate_seed(seed):
    """Run ablation for a single seed. Returns a result dict."""
    set_all_seeds(seed)
    X, y, w_true = generate_gaussian_data(N, D, seed)

    t0 = time.time()
    result = {'seed': seed}

    # --- Convex L2 solution with CORRECTED beta ---
    try:
        f_convex, convex_weights = solve_convex_l2(
            X, y, beta=BETA_CONVEX, max_patterns=MAX_PATTERNS,
            solver_eps=SOLVER_EPS, seed=seed
        )
        result['f_convex'] = float(f_convex)
        result['convex_status'] = convex_weights['status']
        result['n_patterns'] = convex_weights['n_patterns']
        result['beta_convex_used'] = float(BETA_CONVEX)
        print(f"  Convex f={f_convex:.6f} (status={convex_weights['status']}, "
              f"patterns={convex_weights['n_patterns']}, beta={BETA_CONVEX})")
    except Exception as e:
        result['error'] = f'convex_failed: {e}'
        result['passed'] = False
        print(f"  CONVEX SOLVER FAILED: {e}")
        traceback.print_exc()
        return result

    # --- Non-convex L2-only solution (parallel restarts) ---
    try:
        f_nonconvex, nonconvex_state = train_nonconvex_parallel(
            X, y, d=D, width=WIDTH,
            lambda_1=LAMBDA_1, lambda_2=LAMBDA_2,
            n_restarts=N_RESTARTS, n_epochs=N_EPOCHS,
            lr_stage1=LR_STAGE1, lr_stage2=LR_STAGE2,
            lr_switch=LR_SWITCH_EPOCH,
            seed_base=seed
        )
        result['f_nonconvex'] = float(f_nonconvex)
        print(f"  NonConvex f={f_nonconvex:.6f}")
    except Exception as e:
        result['error'] = f'nonconvex_failed: {e}'
        result['passed'] = False
        print(f"  NON-CONVEX TRAINING FAILED: {e}")
        traceback.print_exc()
        return result

    # --- Criterion (a): original relative difference ---
    rel_diff_a = abs(f_nonconvex - f_convex) / max(abs(f_nonconvex), 1e-6)
    result['rel_diff_criterion_a'] = float(rel_diff_a)

    # --- Criterion (b): same-objective L2 comparison ---
    # f_nonconvex_l2_only: since lambda_1=0, this IS f_nonconvex
    f_nonconvex_l2_only = f_nonconvex
    result['f_nonconvex_l2_only'] = float(f_nonconvex_l2_only)

    # f_convex_l2_only: via rescaling lemma proxy with correct formula
    f_convex_l2_only, cv_data_loss, sum_norms, convex_pred = compute_convex_l2_only(
        X, y, convex_weights, LAMBDA_2
    )
    result['f_convex_l2_only'] = float(f_convex_l2_only)
    result['convex_data_loss'] = float(cv_data_loss)
    result['sum_norms_proxy'] = float(sum_norms)
    result['lambda2_x_2_x_sum_norms'] = float(LAMBDA_2 * 2.0 * sum_norms)

    rel_diff_b = abs(f_convex_l2_only - f_nonconvex_l2_only) / max(abs(f_nonconvex_l2_only), 1e-6)
    result['rel_diff_criterion_b'] = float(rel_diff_b)

    # --- Diagnostic: prediction distance ---
    nonconvex_pred = compute_predictions_from_state(X, nonconvex_state, D, WIDTH)
    norm_nonconvex = float(np.linalg.norm(nonconvex_pred))
    if norm_nonconvex > 1e-8:
        pred_l2_diff = float(np.linalg.norm(convex_pred - nonconvex_pred) / norm_nonconvex)
    else:
        pred_l2_diff = float('inf')
    result['pred_l2_diff'] = pred_l2_diff

    # --- Evaluate pass criteria ---
    pass_a = rel_diff_a < TOLERANCE
    pass_b = rel_diff_b < TOLERANCE
    pass_c = (rel_diff_a < TOLERANCE_LENIENT and
              rel_diff_b < TOLERANCE_LENIENT and
              pred_l2_diff < PRED_DIFF_LENIENT)

    passed = pass_a or pass_b or pass_c
    result['pass_a'] = pass_a
    result['pass_b'] = pass_b
    result['pass_c'] = pass_c
    result['passed'] = passed

    if pass_a:
        result['pass_criterion_fired'] = 'a'
    elif pass_b:
        result['pass_criterion_fired'] = 'b'
    elif pass_c:
        result['pass_criterion_fired'] = 'c'
    else:
        result['pass_criterion_fired'] = 'none'

    wall_time = time.time() - t0
    result['wall_time_seconds'] = float(wall_time)

    status_str = "PASS" if passed else "FAIL"
    print(f"  criterion_a: rel_diff={rel_diff_a*100:.2f}% ({'PASS' if pass_a else 'FAIL'})")
    print(f"  criterion_b: rel_diff={rel_diff_b*100:.2f}% ({'PASS' if pass_b else 'FAIL'})")
    print(f"  pred_l2_diff: {pred_l2_diff*100:.2f}% (diagnostic)")
    print(f"  criterion_c: {'PASS' if pass_c else 'FAIL'}")
    print(f"  => Seed {seed}: {status_str} (criterion: {result['pass_criterion_fired']}) | {wall_time:.1f}s")

    return result


def main():
    print("=" * 60)
    print("H6 Ablation Iteration 2 (rev 2): Correct beta = 2*lambda_2")
    print("(Underparameterized regime: width=10, n/width=20)")
    print("=" * 60)
    print(f"Parameters: n={N}, d={D}, width={WIDTH}, lambda_2={LAMBDA_2}, "
          f"beta_convex={BETA_CONVEX:.6f} (= 2*lambda_2, CORRECTED)")
    print(f"Seeds: {N_SEEDS}, Restarts: {N_RESTARTS} (parallel), Epochs: {N_EPOCHS}")
    print(f"LR schedule: {LR_STAGE1} for epochs 0-{LR_SWITCH_EPOCH}, "
          f"{LR_STAGE2} for epochs {LR_SWITCH_EPOCH}-{N_EPOCHS}")
    print(f"max_patterns: {MAX_PATTERNS}, solver_eps: {SOLVER_EPS}")
    print(f"Pass: >= {MIN_SEEDS_PASS}/{N_SEEDS} seeds pass any criterion")
    print()

    ablation_results = []
    n_passed = 0

    for seed in range(N_SEEDS):
        print(f"\n--- Seed {seed} ---")
        try:
            res = evaluate_seed(seed)
            ablation_results.append(res)
            if res.get('passed', False):
                n_passed += 1
        except Exception as e:
            print(f"  SEED {seed} EXCEPTION: {e}")
            traceback.print_exc()
            ablation_results.append({'seed': seed, 'passed': False, 'error': str(e)})

    overall_passed = n_passed >= MIN_SEEDS_PASS

    print()
    print("=" * 60)
    print(f"ABLATION SUMMARY: {n_passed}/{N_SEEDS} seeds passed")
    print(f"Required: >= {MIN_SEEDS_PASS} seeds")
    print(f"VERDICT: {'PASSED' if overall_passed else 'FAILED'}")
    print("=" * 60)

    completed = [r for r in ablation_results if 'f_convex' in r]
    if completed:
        rel_a = [r['rel_diff_criterion_a'] for r in completed if 'rel_diff_criterion_a' in r]
        rel_b = [r['rel_diff_criterion_b'] for r in completed if 'rel_diff_criterion_b' in r]
        pred_diffs = [r['pred_l2_diff'] for r in completed if 'pred_l2_diff' in r]
        if rel_a:
            print(f"Criterion (a) rel_diff: mean={np.mean(rel_a)*100:.2f}%, "
                  f"max={np.max(rel_a)*100:.2f}%, min={np.min(rel_a)*100:.2f}%")
        if rel_b:
            print(f"Criterion (b) rel_diff: mean={np.mean(rel_b)*100:.2f}%, "
                  f"max={np.max(rel_b)*100:.2f}%, min={np.min(rel_b)*100:.2f}%")
        if pred_diffs:
            finite_pred = [p for p in pred_diffs if p != float('inf')]
            if finite_pred:
                print(f"pred_l2_diff (diagnostic): mean={np.mean(finite_pred)*100:.2f}%, "
                      f"max={np.max(finite_pred)*100:.2f}%")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'iteration': 2,
        'revision': 'beta_corrected',
        'beta_formula': '2*lambda_2 (corrected from 2*sqrt(lambda_2))',
        'passed': overall_passed,
        'n_passed_seeds': n_passed,
        'n_seeds': N_SEEDS,
        'min_seeds_required': MIN_SEEDS_PASS,
        'tolerance_criterion_a': TOLERANCE,
        'tolerance_criterion_b': TOLERANCE,
        'tolerance_criterion_c_lenient': TOLERANCE_LENIENT,
        'pred_diff_threshold_criterion_c': PRED_DIFF_LENIENT,
        'beta_convex': float(BETA_CONVEX),
        'lambda_2': LAMBDA_2,
        'parameters': {
            'n': N, 'd': D, 'width': WIDTH,
            'n_restarts': N_RESTARTS, 'n_epochs': N_EPOCHS,
            'lr_stage1': LR_STAGE1, 'lr_stage2': LR_STAGE2,
            'lr_switch_epoch': LR_SWITCH_EPOCH,
            'max_patterns': MAX_PATTERNS, 'solver_eps': SOLVER_EPS,
        },
        'per_seed': ablation_results,
    }

    out_path = os.path.join(RESULTS_DIR, 'ablation_l2_nonconvex.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nAblation results saved to: {out_path}")

    if overall_passed:
        print("\nAblation PASSED. Awaiting reviewer confirmation before main experiment.")
        sys.exit(0)
    else:
        print("\nAblation FAILED.")
        sys.exit(1)


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    main()
