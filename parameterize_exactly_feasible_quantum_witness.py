"""Convert the numerical qubit witness into an exactly normalized form.

We retain a printed real K0 and define

    K1 = R(phi) sqrt(I - K0.T K0),
    |psi> = (cos(theta), sin(theta)).

Completeness then holds by construction for the stated real parameters.
The script finds theta and the nearest rotation R(phi) to the numerical
witness, and recomputes the target-word probability.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "outputs/thue_morse_L8_d2_explicit_quantum_witness.json"
OUTPUT = ROOT / "outputs/thue_morse_L8_d2_exactly_feasible_parameterization.json"
WORD = (0, 1, 1, 0, 1, 0, 0, 1)


def positive_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if values.min() <= 0:
        raise ValueError(f"Matrix is not positive definite: {values}")
    return (vectors * np.sqrt(values)) @ vectors.T


def sequence_probability(
    psi: np.ndarray, k0: np.ndarray, k1: np.ndarray
) -> float:
    state = psi.copy()
    for symbol in WORD:
        state = (k0 if symbol == 0 else k1) @ state
    return float(state @ state)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    psi_source = np.array(source["initial_state_vector"], dtype=float)
    k0 = np.round(np.array(source["K0"], dtype=float), 12)
    k1_source = np.array(source["K1"], dtype=float)

    theta = float(np.arctan2(psi_source[1], psi_source[0]))
    psi = np.array([np.cos(theta), np.sin(theta)])

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

    completeness = k0.T @ k0 + k1.T @ k1
    probability = sequence_probability(psi, k0, k1)
    result = {
        "target_word": "".join(map(str, WORD)),
        "definition": "K1 = R(phi) sqrt(I - K0^T K0); psi=(cos(theta),sin(theta))",
        "theta_radians": theta,
        "phi_radians": phi,
        "K0_printed": k0.tolist(),
        "residual_eigenvalues": np.linalg.eigvalsh(residual).tolist(),
        "derived_K1": k1.tolist(),
        "completeness_frobenius_error": float(
            np.linalg.norm(completeness - np.eye(2), ord="fro")
        ),
        "state_norm_error": float(abs(psi @ psi - 1.0)),
        "target_word_probability": probability,
        "above_certified_classical_threshold_0p03": probability > 0.03,
        "margin_above_0p03": probability - 0.03,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
