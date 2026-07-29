"""Outward interval verification of an exactly normalized qubit witness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mpmath import iv


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
    return [a[i][0] * v[0] + a[i][1] * v[1] for i in range(2)]


def bounds(value):
    return float(value.a), float(value.b)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--threshold", type=str, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    source_path = root / (
        f"outputs/thue_morse_L{2 ** args.level}_d2_"
        "exactly_feasible_parameterization.json"
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))

    iv.dps = 80
    theta = iv.mpf(str(source["theta_radians"]))
    phi = iv.mpf(str(source["phi_radians"]))
    k0 = [[iv.mpf(str(x)) for x in row] for row in source["K0_printed"]]

    identity = [[iv.mpf(1), iv.mpf(0)], [iv.mpf(0), iv.mpf(1)]]
    gram = mul(transpose(k0), k0)
    residual = [
        [identity[i][j] - gram[i][j] for j in range(2)]
        for i in range(2)
    ]
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
    state = [iv.cos(theta), iv.sin(theta)]
    for symbol in source["target_word"]:
        state = matvec(k0 if symbol == "0" else k1, state)
    probability = state[0] ** 2 + state[1] ** 2
    lower, upper = bounds(probability)
    threshold = float(args.threshold)

    result = {
        "target_word": source["target_word"],
        "level": args.level,
        "length": len(source["target_word"]),
        "interval_method": "mpmath.iv outward interval arithmetic, 80 decimal digits",
        "probability_lower": lower,
        "probability_upper": upper,
        "probability_interval_80d": iv.nstr(probability, 90),
        "certified_lower_threshold": threshold,
        "certified_above_threshold": lower > threshold,
        "residual_determinant_interval": bounds(determinant),
    }
    output = root / (
        f"outputs/thue_morse_L{len(source['target_word'])}_d2_"
        "quantum_interval_certificate.json"
    )
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
