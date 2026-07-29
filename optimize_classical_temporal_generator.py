"""Optimize classical finite-memory generators for Thue-Morse words.

Model
-----
At every step the same binary-output instrument is applied. For memory
dimension d, S[i, a, j] is the probability of emitting a in state i and
transitioning to state j. Each row is normalized over (a, j). The initial
memory distribution is optimized as well.

The objective is the probability of one complete externally stopped word.
This is the classical model used in the repeated-instrument temporal
correlation scenario of Vieira and Budroni (Quantum 6, 623, 2022).
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from thue_morse_dc import deterministic_complexity, thue_morse_word


def softmax_rows(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=-1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=-1, keepdims=True)


def unpack(theta: np.ndarray, dimension: int) -> tuple[np.ndarray, np.ndarray]:
    initial_logits = theta[:dimension]
    edge_logits = theta[dimension:].reshape(dimension, 2 * dimension)
    initial = softmax_rows(initial_logits[None, :])[0]
    edges = softmax_rows(edge_logits).reshape(dimension, 2, dimension)
    return initial, edges


def objective_and_gradient(
    theta: np.ndarray, word: str, dimension: int
) -> tuple[float, np.ndarray]:
    initial, edges = unpack(theta, dimension)
    symbols = np.fromiter((int(bit) for bit in word), dtype=np.int8)
    length = len(symbols)

    forward = np.empty((length + 1, dimension))
    backward = np.empty((length + 1, dimension))
    forward[0] = initial
    for step, symbol in enumerate(symbols):
        forward[step + 1] = forward[step] @ edges[:, symbol, :]

    backward[length] = 1.0
    for step in range(length - 1, -1, -1):
        backward[step] = edges[:, symbols[step], :] @ backward[step + 1]

    probability = float(forward[length].sum())
    safe_probability = max(probability, np.finfo(float).tiny)

    edge_derivative = np.zeros_like(edges)
    for step, symbol in enumerate(symbols):
        edge_derivative[:, symbol, :] += np.outer(
            forward[step], backward[step + 1]
        )

    edge_flat = edges.reshape(dimension, 2 * dimension)
    derivative_flat = edge_derivative.reshape(dimension, 2 * dimension)
    weighted = (edge_flat * derivative_flat).sum(axis=1, keepdims=True)
    edge_logit_gradient = edge_flat * (derivative_flat - weighted)

    initial_derivative = backward[0]
    initial_logit_gradient = initial * (
        initial_derivative - float(initial @ initial_derivative)
    )

    gradient_probability = np.concatenate(
        [initial_logit_gradient, edge_logit_gradient.ravel()]
    )
    return -np.log(safe_probability), -gradient_probability / safe_probability


@dataclass
class OptimizationResult:
    level: int
    length: int
    deterministic_complexity: int
    dimension: int
    best_probability: float
    best_log_probability: float
    successful_restarts: int
    restarts: int
    iterations_best: int
    seed: int


def optimize(
    word: str,
    dimension: int,
    restarts: int,
    maxiter: int,
    seed: int,
) -> tuple[OptimizationResult, np.ndarray]:
    rng = np.random.default_rng(seed)
    parameter_count = dimension + dimension * 2 * dimension
    best = None
    successful = 0

    for restart in range(restarts):
        theta0 = rng.normal(0.0, 0.8, size=parameter_count)
        result = minimize(
            objective_and_gradient,
            theta0,
            args=(word, dimension),
            method="L-BFGS-B",
            jac=True,
            options={"maxiter": maxiter, "ftol": 1e-13, "gtol": 1e-9},
        )
        successful += int(result.success)
        if best is None or result.fun < best.fun:
            best = result

    assert best is not None
    probability = float(np.exp(-best.fun))
    level = int(np.log2(len(word)))
    dc, _, _ = deterministic_complexity(word)
    summary = OptimizationResult(
        level=level,
        length=len(word),
        deterministic_complexity=dc,
        dimension=dimension,
        best_probability=probability,
        best_log_probability=float(-best.fun),
        successful_restarts=successful,
        restarts=restarts,
        iterations_best=int(best.nit),
        seed=seed,
    )
    return summary, best.x


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--levels", nargs="+", type=int, default=[2, 3, 4, 5])
    parser.add_argument("--dimensions", nargs="+", type=int, default=[2, 3, 4])
    parser.add_argument("--restarts", type=int, default=24)
    parser.add_argument("--maxiter", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=20260729)
    args = parser.parse_args()

    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    summaries = []
    parameters = {}

    for level in args.levels:
        word = thue_morse_word(level)
        dc, _, _ = deterministic_complexity(word)
        for dimension in args.dimensions:
            if dimension >= dc:
                continue
            summary, theta = optimize(
                word,
                dimension,
                args.restarts,
                args.maxiter,
                args.seed + 1000 * level + dimension,
            )
            summaries.append(asdict(summary))
            parameters[f"n{level}_d{dimension}"] = theta.tolist()
            print(
                f"n={level} L={len(word):2d} d={dimension:2d} "
                f"P={summary.best_probability:.10f}"
            )

    csv_path = output_dir / "thue_morse_classical_optimization.csv"
    json_path = output_dir / "thue_morse_classical_optimization.json"
    parameter_path = output_dir / "thue_morse_classical_best_parameters.json"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)
    json_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    parameter_path.write_text(json.dumps(parameters, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
