"""Outward interval verification of the exactly normalized qubit witness."""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs/thue_morse_L8_d2_quantum_interval_certificate.json"
WORD = (0, 1, 1, 0, 1, 0, 0, 1)


def add(a, b):
    return [[a[i][j] + b[i][j] for j in range(2)] for i in range(2)]


def mul(a, b):
    return [
        [
            sum((a[i][k] * b[k][j] for k in range(2)), iv.mpf(0))
            for j in range(2)
        ]
        for i in range(2)
    ]


def transpose(a):
    return [[a[j][i] for j in range(2)] for i in range(2)]


def matvec(a, v):
    return [
        a[i][0] * v[0] + a[i][1] * v[1]
        for i in range(2)
    ]


def interval_bounds(value):
    return float(value.a), float(value.b)


def main() -> None:
    iv.dps = 80
    theta = iv.mpf("-0.2880903478104165")
    phi = iv.mpf("2.1351675998196673")
    k0 = [
        [iv.mpf("-0.261100885994"), iv.mpf("-0.263277264622")],
        [iv.mpf("0.894987283427"), iv.mpf("-0.279312440034")],
    ]

    identity = [[iv.mpf(1), iv.mpf(0)], [iv.mpf(0), iv.mpf(1)]]
    gram = mul(transpose(k0), k0)
    residual = [
        [identity[i][j] - gram[i][j] for j in range(2)]
        for i in range(2)
    ]

    # Positive square root of a symmetric positive-definite 2x2 matrix:
    # sqrt(A) = (A + sqrt(det(A)) I) / sqrt(tr(A)+2 sqrt(det(A))).
    determinant = residual[0][0] * residual[1][1] - residual[0][1] ** 2
    root_det = iv.sqrt(determinant)
    denominator = iv.sqrt(
        residual[0][0] + residual[1][1] + 2 * root_det
    )
    sqrt_residual = [
        [
            (residual[i][j] + (root_det if i == j else 0)) / denominator
            for j in range(2)
        ]
        for i in range(2)
    ]
    rotation = [
        [iv.cos(phi), -iv.sin(phi)],
        [iv.sin(phi), iv.cos(phi)],
    ]
    k1 = mul(rotation, sqrt_residual)
    psi = [iv.cos(theta), iv.sin(theta)]

    state = psi
    for symbol in WORD:
        state = matvec(k0 if symbol == 0 else k1, state)
    probability = state[0] ** 2 + state[1] ** 2

    completeness = add(gram, mul(transpose(k1), k1))
    errors = [
        completeness[i][j] - identity[i][j]
        for i in range(2)
        for j in range(2)
    ]
    probability_lower, probability_upper = interval_bounds(probability)
    result = {
        "target_word": "".join(map(str, WORD)),
        "interval_method": "mpmath.iv outward interval arithmetic, 80 decimal digits",
        "parameter_definition": (
            "K1=R(phi)sqrt(I-K0^T K0), "
            "psi=(cos(theta),sin(theta))"
        ),
        "probability_lower": probability_lower,
        "probability_upper": probability_upper,
        "probability_interval_80d": iv.nstr(probability, 90),
        "certified_lower_threshold": 0.0414,
        "certified_above_0p0414": probability_lower > 0.0414,
        "certified_above_classical_0p03": probability_lower > 0.03,
        "completeness_error_intervals": [
            interval_bounds(value) for value in errors
        ],
        "residual_determinant_interval": interval_bounds(determinant),
        "residual_determinant_interval_80d": iv.nstr(determinant, 90),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
