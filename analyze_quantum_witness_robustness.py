"""Noise robustness and shot-power analysis for the explicit L8,d2 witness."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom


ROOT = Path(__file__).resolve().parent
WITNESS_PATH = ROOT / "outputs/thue_morse_L8_d2_explicit_quantum_witness.json"
OUTPUT_PATH = ROOT / "outputs/thue_morse_L8_d2_noise_and_shots.json"
CLASSICAL_CERTIFIED_BOUND = 0.03


def load_witness():
    data = json.loads(WITNESS_PATH.read_text(encoding="utf-8"))
    psi = np.asarray(data["initial_state_vector"], dtype=float)
    kraus = [
        np.asarray(data["K0"], dtype=float),
        np.asarray(data["K1"], dtype=float),
    ]
    word = tuple(int(bit) for bit in data["target_word"])
    return data, psi, kraus, word


def noisy_word_probability(
    eta: float, psi: np.ndarray, kraus: list[np.ndarray], word: tuple[int, ...]
) -> float:
    """Repeated noisy instrument probability.

    For outcome a:
      E_a(rho) = (1-eta) K_a rho K_a^T
                 + eta * Tr(rho) * I/4.

    The second term is a fair random output followed by a maximally mixed
    two-dimensional memory state.  Summing over both outcomes is trace
    preserving.
    """
    rho = np.outer(psi, psi)
    identity = np.eye(2)
    for outcome in word:
        trace = float(np.trace(rho))
        rho = (
            (1.0 - eta) * kraus[outcome] @ rho @ kraus[outcome].T
            + eta * trace * identity / 4.0
        )
    return float(np.trace(rho))


def minimum_shots(p0: float, p1: float, alpha: float, power: float):
    """Exact one-sided binomial-test design."""
    if p1 <= p0:
        return None
    for n in range(1, 2_000_001):
        # Smallest k with Pr_{p0}(X>=k) <= alpha.
        k = int(binom.isf(alpha, n, p0)) + 1
        achieved_alpha = float(binom.sf(k - 1, n, p0))
        achieved_power = float(binom.sf(k - 1, n, p1))
        if achieved_alpha <= alpha and achieved_power >= power:
            return {
                "shots": n,
                "reject_if_target_count_at_least": k,
                "achieved_type_I_error": achieved_alpha,
                "achieved_power_at_witness": achieved_power,
            }
    return None


def main() -> None:
    witness, psi, kraus, word = load_witness()
    ideal = noisy_word_probability(0.0, psi, kraus, word)
    threshold = brentq(
        lambda eta: noisy_word_probability(eta, psi, kraus, word)
        - CLASSICAL_CERTIFIED_BOUND,
        0.0,
        1.0,
    )

    noise_levels = sorted(
        set(
            [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10, threshold]
        )
    )
    noise_table = [
        {
            "eta": float(eta),
            "target_word_probability": noisy_word_probability(
                eta, psi, kraus, word
            ),
            "above_classical_bound": noisy_word_probability(
                eta, psi, kraus, word
            )
            > CLASSICAL_CERTIFIED_BOUND,
        }
        for eta in noise_levels
    ]

    shot_designs = {}
    for label, alpha in (
        ("alpha_0p001", 1e-3),
        ("five_sigma_one_sided", 2.866515718791933e-7),
    ):
        shot_designs[label] = {
            "ideal_90_percent_power": minimum_shots(
                CLASSICAL_CERTIFIED_BOUND, ideal, alpha, 0.90
            ),
            "eta_0p02_90_percent_power": minimum_shots(
                CLASSICAL_CERTIFIED_BOUND,
                noisy_word_probability(0.02, psi, kraus, word),
                alpha,
                0.90,
            ),
        }

    result = {
        "target_word": witness["target_word"],
        "classical_certified_upper_bound_used": CLASSICAL_CERTIFIED_BOUND,
        "ideal_quantum_probability_recomputed": ideal,
        "ideal_quantum_probability_file": witness["sequence_probability"],
        "recomputation_absolute_error": abs(ideal - witness["sequence_probability"]),
        "noise_model": (
            "Per round: with weight 1-eta apply the ideal outcome Kraus map; "
            "with weight eta output a fair random bit and reset the "
            "two-dimensional memory to the maximally mixed state."
        ),
        "critical_eta_where_probability_equals_0p03": threshold,
        "noise_table": noise_table,
        "exact_binomial_shot_designs": shot_designs,
        "claim_boundary": (
            "Robustness is conditional on the stated trusted noise model and "
            "the certified p_classical<0.03 bound. Device-independent and "
            "arbitrary-noise robustness are not claimed."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
