"""
H6: Convex L2 Reformulation Solver.

Implements the Pilanci-Ergen (2020) convex reformulation of two-layer
ReLU network training with L2-squared regularization.
"""
import numpy as np
import cvxpy as cp


def enumerate_sign_patterns(X, max_patterns=200, seed=None):
    """
    Enumerate hyperplane arrangements for ReLU activation patterns.
    Samples random hyperplanes and deduplicates by activation pattern.

    Args:
        X: (n, d) data matrix
        max_patterns: maximum number of patterns to sample
        seed: random seed for reproducibility
    Returns:
        D_list: list of (n, n) diagonal matrices (as 2D numpy arrays)
                each representing a ReLU activation pattern
    """
    rng = np.random.RandomState(seed if seed is not None else 42)
    n, d = X.shape
    D_list = []
    seen = set()

    # Oversample to get max_patterns unique patterns
    for _ in range(max_patterns * 20):
        v = rng.randn(d)
        pattern = tuple((X @ v > 0).astype(int))
        if pattern not in seen:
            seen.add(pattern)
            D_list.append(np.diag(np.array(pattern, dtype=float)))
            if len(D_list) >= max_patterns:
                break

    return D_list


def solve_convex_l2(X, y, beta, max_patterns=200, solver_eps=1e-6, seed=None):
    """
    Solve the convex reformulation of two-layer ReLU network training
    with L2-squared (weight decay) regularization.

    The convex program (from Pilanci-Ergen 2020):
        min_{u_j, v_j} (1/2n) ||y - sum_j D_j X (u_j - v_j)||^2
                        + beta * sum_j (||u_j||_2 + ||v_j||_2)
        s.t. u_j >= 0, v_j >= 0 for all j

    where D_j are diagonal matrices encoding ReLU activation patterns,
    and beta is the group-L1 regularization (equivalent to L2-squared
    weight decay via the rescaling lemma: beta_convex = 2 * sqrt(lambda_2)).

    Args:
        X: (n, d) data matrix
        y: (n,) target vector
        beta: group-L1 regularization strength (= 2 * sqrt(lambda_2))
        max_patterns: number of hyperplane patterns to sample
        solver_eps: SCS solver tolerance
        seed: random seed for activation pattern sampling
    Returns:
        f_convex: optimal objective value (training loss + regularization)
        weights: dict with optimal u, v arrays and convex predictions
    """
    n, d = X.shape

    # Enumerate activation patterns
    D_list = enumerate_sign_patterns(X, max_patterns=max_patterns, seed=seed)
    P = len(D_list)

    if P == 0:
        raise RuntimeError("No activation patterns enumerated.")

    # Precompute DX matrices to speed up CVXPY construction
    DX_list = [D_list[j] @ X for j in range(P)]  # each is (n, d)

    # Decision variables: u_j, v_j in R^d for each pattern j (nonneg)
    u = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v = [cp.Variable(d, nonneg=True) for _ in range(P)]

    # Prediction: sum_j D_j X (u_j - v_j)
    pred = sum(DX_list[j] @ (u[j] - v[j]) for j in range(P))

    # Objective: (1/2n)||y - pred||^2 + beta * sum_j (||u_j||_2 + ||v_j||_2)
    loss = (1.0 / (2 * n)) * cp.sum_squares(y - pred)
    reg = beta * sum(cp.norm(u[j], 2) + cp.norm(v[j], 2) for j in range(P))

    objective = cp.Minimize(loss + reg)
    prob = cp.Problem(objective)

    # Try SCS first, fall back to ECOS if needed
    try:
        prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=100000, verbose=False)
    except Exception as e:
        print(f"  SCS failed ({e}), trying ECOS...")
        prob.solve(solver=cp.ECOS, verbose=False)

    if prob.status not in ['optimal', 'optimal_inaccurate']:
        raise RuntimeError(f"CVXPY solver failed with status: {prob.status}")

    if prob.value is None:
        raise RuntimeError("CVXPY returned None value despite optimal status")

    f_convex = float(prob.value)
    weights = {
        'u': [u_j.value for u_j in u],
        'v': [v_j.value for v_j in v],
        'n_patterns': P,
        'status': prob.status,
    }

    return f_convex, weights


def evaluate_convex_weights_under_elastic_net(X, y, weights, lambda_1, lambda_2,
                                               beta_convex):
    """
    Evaluate the convex solution's weights under the elastic net objective.

    The convex solution has weights (u_j, v_j). We reconstruct the effective
    first-layer weights w1_j = u_j - v_j and compute the elastic net loss.

    Note: this is an approximation since the convex solution lives in a
    different parameterization than the non-convex network.
    We evaluate the total elastic net loss on the convex prediction.

    Returns:
        f_convex_elastic: elastic net objective value at convex solution
    """
    n, d = X.shape
    u_list = weights['u']
    v_list = weights['v']

    # Compute predictions using the pattern-based weights
    # We need to re-enumerate patterns consistently -- use the stored ones
    # But since we don't store D_list, we compute prediction from y and f_convex
    # Instead, compute L2 norm of all weights for penalty terms
    all_params = []
    for u_j, v_j in zip(u_list, v_list):
        if u_j is not None and v_j is not None:
            all_params.extend(u_j.tolist())
            all_params.extend(v_j.tolist())
    all_params = np.array(all_params)

    l1_penalty = lambda_1 * np.sum(np.abs(all_params))
    l2_penalty = lambda_2 * np.sum(all_params ** 2)

    return None  # Placeholder -- actual implementation in run_experiment.py
