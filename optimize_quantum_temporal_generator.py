r"""Real-amplitude quantum-instrument lower-bound optimization.

The same binary-output instrument is repeated at every time step. A real
Stinespring isometry parameterizes Kraus operators K[a, r] and enforces

    sum_{a,r} K[a,r]^T K[a,r] = I.

Real instruments are a strict, physically valid subset of general complex
quantum instruments. Therefore any advantage found here is a valid quantum
lower bound; failure to find one is not a no-go result.

The implementation deliberately uses NumPy/SciPy only because the available
Windows machine cannot initialize the PyTorch or JAX native runtimes.
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


def parameter_count(dimension: int, kraus_rank: int) -> int:
    return 2 * kraus_rank * dimension * dimension + dimension


def unpack(
    theta: np.ndarray, dimension: int, kraus_rank: int
) -> tuple[np.ndarray, np.ndarray]:
    instrument_size = 2 * kraus_rank * dimension * dimension
    raw = theta[:instrument_size].reshape(
        2 * kraus_rank * dimension, dimension
    )
    isometry, triangular = np.linalg.qr(raw, mode="reduced")
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    isometry = isometry * signs
    kraus = isometry.reshape(2, kraus_rank, dimension, dimension)

    vector = theta[instrument_size:]
    norm = np.linalg.norm(vector)
    if norm < 1e-14:
        vector = np.ones(dimension) / np.sqrt(dimension)
    else:
        vector = vector / norm
    rho = np.outer(vector, vector)
    return kraus, rho


def negative_log_probability(
    theta: np.ndarray, word: str, dimension: int, kraus_rank: int
) -> float:
    kraus, rho = unpack(theta, dimension, kraus_rank)
    for bit in word:
        operators = kraus[int(bit)]
        rho = np.einsum("rij,jk,rnk->in", operators, rho, operators)
    probability = max(float(np.trace(rho)), np.finfo(float).tiny)
    return -np.log(probability)


def completeness_error(theta: np.ndarray, dimension: int, kraus_rank: int) -> float:
    kraus, _ = unpack(theta, dimension, kraus_rank)
    completeness = np.einsum("arji,arjk->ik", kraus, kraus)
    return float(np.linalg.norm(completeness - np.eye(dimension)))


@dataclass
class QuantumOptimizationResult:
    level: int
    length: int
    deterministic_complexity: int
    dimension: int
    kraus_rank: int
    amplitude_field: str
    best_probability: float
    best_log_probability: float
    completeness_error: float
    successful_restarts: int
    restarts: int
    maxiter: int
    seed: int


def optimize(
    word: str,
    dimension: int,
    kraus_rank: int,
    restarts: int,
    maxiter: int,
    seed: int,
) -> tuple[QuantumOptimizationResult, dict[str, list[float]]]:
    rng = np.random.default_rng(seed)
    best = None
    successful = 0
    for _ in range(restarts):
        theta0 = rng.normal(
            0.0, 0.8, size=parameter_count(dimension, kraus_rank)
        )
        result = minimize(
            negative_log_probability,
            theta0,
            args=(word, dimension, kraus_rank),
            method="L-BFGS-B",
            options={
                "maxiter": maxiter,
                "ftol": 1e-12,
                "gtol": 1e-7,
                "maxls": 35,
            },
        )
        successful += int(result.success)
        if best is None or result.fun < best.fun:
            best = result

    assert best is not None
    level = int(np.log2(len(word)))
    dc, _, _ = deterministic_complexity(word)
    result = QuantumOptimizationResult(
        level=level,
        length=len(word),
        deterministic_complexity=dc,
        dimension=dimension,
        kraus_rank=kraus_rank,
        amplitude_field="real",
        best_probability=float(np.exp(-best.fun)),
        best_log_probability=float(-best.fun),
        completeness_error=completeness_error(
            best.x, dimension, kraus_rank
        ),
        successful_restarts=successful,
        restarts=restarts,
        maxiter=maxiter,
        seed=seed,
    )
    return result, {"theta": best.x.tolist()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--levels", nargs="+", type=int, default=[2, 3, 4])
    parser.add_argument("--dimensions", nargs="+", type=int, default=[2, 3])
    parser.add_argument("--kraus-rank", type=int, default=2)
    parser.add_argument("--restarts", type=int, default=16)
    parser.add_argument("--maxiter", type=int, default=800)
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
            result, payload = optimize(
                word,
                dimension,
                args.kraus_rank,
                args.restarts,
                args.maxiter,
                args.seed + 1000 * level + dimension,
            )
            summaries.append(asdict(result))
            parameters[f"n{level}_d{dimension}_r{args.kraus_rank}"] = payload
            print(
                f"n={level} L={len(word):2d} d={dimension} "
                f"r={args.kraus_rank} P={result.best_probability:.10f} "
                f"TPerr={result.completeness_error:.2e}"
            )

    csv_path = output_dir / "thue_morse_quantum_optimization.csv"
    json_path = output_dir / "thue_morse_quantum_optimization.json"
    parameter_path = output_dir / "thue_morse_quantum_best_parameters.json"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)
    json_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    parameter_path.write_text(json.dumps(parameters), encoding="utf-8")


if __name__ == "__main__":
    main()
