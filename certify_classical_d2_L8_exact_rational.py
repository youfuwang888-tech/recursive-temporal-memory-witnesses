"""Exact-rational branch-and-bound certificate for the L8,d=2 classical bound.

This implementation is deliberately independent of NumPy and floating-point
interval arithmetic. All box endpoints and propagated probability bounds are
fractions. Floating-point values are used only to order the priority queue;
termination checks the exact maximum over every queued node.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import heapq
import json
from pathlib import Path
import time


WORD = (0, 1, 1, 0, 1, 0, 0, 1)
TARGET = Fraction(3, 100)
QUANTUM = Fraction("0.041469816596040404")


def tighten(lower: tuple[Fraction, ...], upper: tuple[Fraction, ...]):
    lo = list(lower)
    hi = list(upper)
    for start in (0, 3):
        if sum(lo[start : start + 3], Fraction(0)) > 1:
            return None
        for k in range(start, start + 3):
            others = sum(
                (lo[j] for j in range(start, start + 3) if j != k),
                Fraction(0),
            )
            hi[k] = min(hi[k], 1 - others)
            if hi[k] < lo[k]:
                return None
    return tuple(lo), tuple(hi)


def row_upper(lower: tuple[Fraction, ...], upper: tuple[Fraction, ...], start: int):
    return (
        upper[start],
        upper[start + 1],
        upper[start + 2],
        1 - sum(lower[start : start + 3], Fraction(0)),
    )


def exact_interval_upper(
    lower: tuple[Fraction, ...], upper: tuple[Fraction, ...]
) -> Fraction:
    r0 = row_upper(lower, upper, 0)
    r1 = row_upper(lower, upper, 3)
    matrices = (
        ((r0[0], r0[1]), (r1[0], r1[1])),
        ((r0[2], r0[3]), (r1[2], r1[3])),
    )
    v0, v1 = Fraction(1), Fraction(0)
    total = Fraction(1)
    for symbol in WORD:
        matrix = matrices[symbol]
        n0 = v0 * matrix[0][0] + v1 * matrix[1][0]
        n1 = v0 * matrix[0][1] + v1 * matrix[1][1]
        total = min(total, n0 + n1)
        v0, v1 = min(n0, total), min(n1, total)
    return min(total, v0 + v1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-nodes", type=int, default=500_000)
    parser.add_argument("--max-seconds", type=float, default=900.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "outputs/thue_morse_L8_d2_exact_rational_certificate.json"
        ),
    )
    args = parser.parse_args()

    zero = Fraction(0)
    one = Fraction(1)
    root_lo = (zero,) * 6
    root_hi = (one,) * 6
    root_bound = exact_interval_upper(root_lo, root_hi)
    # Heap entries: conservative float ordering key, serial, exact bound, box.
    heap = [(-float(root_bound), 0, root_bound, root_lo, root_hi)]
    serial = 0
    processed = 0
    started = time.time()
    certified = False

    while heap and processed < args.max_nodes:
        if time.time() - started > args.max_seconds:
            break

        # A float key is sufficient for search order, but not certification.
        _, _, bound, lower, upper = heapq.heappop(heap)
        widths = [upper[i] - lower[i] for i in range(6)]
        split = max(range(6), key=widths.__getitem__)
        midpoint = (lower[split] + upper[split]) / 2

        for is_left in (True, False):
            child_lo = list(lower)
            child_hi = list(upper)
            if is_left:
                child_hi[split] = midpoint
            else:
                child_lo[split] = midpoint
            tightened = tighten(tuple(child_lo), tuple(child_hi))
            if tightened is None:
                continue
            child_lo_t, child_hi_t = tightened
            child_bound = exact_interval_upper(child_lo_t, child_hi_t)
            serial += 1
            heapq.heappush(
                heap,
                (
                    -float(child_bound),
                    serial,
                    child_bound,
                    child_lo_t,
                    child_hi_t,
                ),
            )
        processed += 1

        if processed % 10_000 == 0:
            exact_max = max(entry[2] for entry in heap)
            print(
                f"nodes={processed} queue={len(heap)} "
                f"exact_upper={float(exact_max):.12g}"
            )
            if exact_max < TARGET:
                certified = True
                break

    exact_max = max((entry[2] for entry in heap), default=Fraction(0))
    certified = certified or exact_max < TARGET
    elapsed = time.time() - started
    result = {
        "word": "".join(map(str, WORD)),
        "dimension": 2,
        "method": "exact-rational best-first interval branch-and-bound",
        "processed_nodes": processed,
        "queued_nodes": len(heap),
        "elapsed_seconds": elapsed,
        "exact_global_upper_numerator": exact_max.numerator,
        "exact_global_upper_denominator": exact_max.denominator,
        "global_upper_decimal": float(exact_max),
        "target_exact": "3/100",
        "explicit_quantum_witness": float(QUANTUM),
        "separation_certified": certified and TARGET < QUANTUM,
        "claim": (
            "Every stationary two-state classical generator has target-word "
            "probability below 3/100."
            if certified
            else "Resource limit reached before the 3/100 certificate."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
