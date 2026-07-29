"""Export and independently verify an explicit L=8, d=2 quantum witness."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from optimize_quantum_temporal_generator import unpack
from thue_morse_dc import thue_morse_word


def main() -> None:
    root = Path(__file__).resolve().parent
    parameters = json.loads(
        (root / "outputs" / "thue_morse_quantum_rank1_parameters.json").read_text(
            encoding="utf-8"
        )
    )
    theta = np.asarray(parameters["n3_d2_r1"]["theta"], dtype=float)
    kraus, rho = unpack(theta, dimension=2, kraus_rank=1)
    matrix0 = kraus[0, 0]
    matrix1 = kraus[1, 0]
    completeness = matrix0.T @ matrix0 + matrix1.T @ matrix1

    evolved = rho.copy()
    for bit in thue_morse_word(3):
        operator = matrix0 if bit == "0" else matrix1
        evolved = operator @ evolved @ operator.T
    probability = float(np.trace(evolved))

    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    state = eigenvectors[:, np.argmax(eigenvalues)]
    if state[0] < 0:
        state = -state

    payload = {
        "target_word": thue_morse_word(3),
        "memory_dimension": 2,
        "kraus_rank_per_outcome": 1,
        "amplitudes": "real",
        "initial_state_vector": state.tolist(),
        "K0": matrix0.tolist(),
        "K1": matrix1.tolist(),
        "completeness_matrix": completeness.tolist(),
        "completeness_frobenius_error": float(
            np.linalg.norm(completeness - np.eye(2))
        ),
        "sequence_probability": probability,
        "classical_best_found": 0.016434148019480888,
        "ratio_to_classical_best_found": probability / 0.016434148019480888,
        "claim_boundary": (
            "Explicit quantum lower bound. The classical comparison remains "
            "numerical until a global upper certificate is completed."
        ),
    }
    output = root / "outputs" / "thue_morse_L8_d2_explicit_quantum_witness.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
