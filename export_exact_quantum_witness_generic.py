"""Export an exactly normalized rank-one real qubit witness for T_n."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from optimize_quantum_temporal_generator import unpack
from thue_morse_dc import thue_morse_word


def positive_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if values.min() <= 0:
        raise ValueError(f"Matrix is not positive definite: {values}")
    return (vectors * np.sqrt(values)) @ vectors.T


def sequence_probability(
    word: str,
    psi: np.ndarray,
    k0: np.ndarray,
    k1: np.ndarray,
) -> float:
    state = psi.copy()
    for symbol in word:
        state = (k0 if symbol == "0" else k1) @ state
    return float(state @ state)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--digits", type=int, default=14)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    parameters = json.loads(
        (root / "outputs/thue_morse_quantum_rank1_parameters.json").read_text(
            encoding="utf-8"
        )
    )
    theta_raw = np.asarray(
        parameters[f"n{args.level}_d2_r1"]["theta"], dtype=float
    )
    kraus, rho = unpack(theta_raw, dimension=2, kraus_rank=1)
    k0_source = kraus[0, 0]
    k1_source = kraus[1, 0]

    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    psi_source = eigenvectors[:, np.argmax(eigenvalues)]
    if psi_source[0] < 0:
        psi_source = -psi_source

    theta = float(np.arctan2(psi_source[1], psi_source[0]))
    k0 = np.round(k0_source, args.digits)
    residual = np.eye(2) - k0.T @ k0
    sqrt_residual = positive_sqrt(residual)
    raw_rotation = k1_source @ np.linalg.inv(sqrt_residual)
    u, _, vt = np.linalg.svd(raw_rotation)
    rotation = u @ vt
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vt
    phi = float(np.arctan2(rotation[1, 0], rotation[0, 0]))
    rotation_from_phi = np.array(
        [[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]]
    )
    k1 = rotation_from_phi @ sqrt_residual
    psi = np.array([np.cos(theta), np.sin(theta)])
    word = thue_morse_word(args.level)
    probability = sequence_probability(word, psi, k0, k1)

    payload = {
        "target_word": word,
        "level": args.level,
        "length": len(word),
        "definition": "K1=R(phi)sqrt(I-K0^T K0); psi=(cos(theta),sin(theta))",
        "theta_radians": theta,
        "phi_radians": phi,
        "K0_printed": k0.tolist(),
        "residual_eigenvalues": np.linalg.eigvalsh(residual).tolist(),
        "derived_K1": k1.tolist(),
        "completeness_frobenius_error": float(
            np.linalg.norm(k0.T @ k0 + k1.T @ k1 - np.eye(2))
        ),
        "target_word_probability": probability,
    }
    output = root / (
        f"outputs/thue_morse_L{len(word)}_d2_"
        "exactly_feasible_parameterization.json"
    )
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
