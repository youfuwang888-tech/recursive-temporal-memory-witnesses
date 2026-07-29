"""Two-stage rigorous certificate for the length-16 classical bound.

Stage 1 uses explicitly outward-rounded IEEE-754 arithmetic to construct a
cover whose every remaining box has an upper bound below 1/2000. Stage 2
converts every endpoint of that final cover to its exact binary rational value
and recomputes every upper bound using Fraction arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
import heapq
import json
from pathlib import Path
import time

import numpy as np

import certify_classical_d2_L8_interval as floating
from certify_classical_d2_generic_exact_rational import exact_interval_upper


WORD = tuple(map(int, "0110100110010110"))
TARGET = Fraction(1, 2000)
OUTPUT = Path("outputs/thue_morse_L16_d2_two_stage_exact_certificate.json")


def as_exact(values: np.ndarray) -> tuple[Fraction, ...]:
    return tuple(Fraction.from_float(float(value)) for value in values)


def main() -> None:
    floating.WORD = WORD
    started = time.time()
    lower = np.zeros(6)
    upper = np.ones(6)
    if not floating.tighten_simplex(lower, upper):
        raise RuntimeError("Root simplex unexpectedly infeasible")
    root_bound = floating.interval_upper(lower, upper)
    heap: list[floating.QueueNode] = [
        floating.QueueNode(-root_bound, 0, lower, upper, root_bound)
    ]
    serial = 0
    processed = 0
    infeasible = 0

    while heap:
        node = heapq.heappop(heap)
        if node.bound < float(TARGET):
            heapq.heappush(heap, node)
            break

        split = floating.choose_split(node.lower, node.upper)
        midpoint = 0.5 * (node.lower[split] + node.upper[split])
        for is_left in (True, False):
            child_lower = node.lower.copy()
            child_upper = node.upper.copy()
            if is_left:
                child_upper[split] = midpoint
            else:
                child_lower[split] = midpoint
            if not floating.tighten_simplex(child_lower, child_upper):
                infeasible += 1
                continue
            bound = floating.interval_upper(child_lower, child_upper)
            serial += 1
            heapq.heappush(
                heap,
                floating.QueueNode(
                    -bound,
                    serial,
                    child_lower,
                    child_upper,
                    bound,
                ),
            )
        processed += 1
        if processed % 50_000 == 0:
            print(
                f"float nodes={processed} queue={len(heap)} "
                f"upper={-heap[0].priority:.12g}",
                flush=True,
            )

    float_stage_seconds = time.time() - started
    float_global_upper = max(node.bound for node in heap)

    exact_started = time.time()
    exact_max = Fraction(0)
    exact_boxes_at_or_above_target = 0
    for index, node in enumerate(heap, start=1):
        exact_bound = exact_interval_upper(
            WORD,
            as_exact(node.lower),
            as_exact(node.upper),
        )
        exact_max = max(exact_max, exact_bound)
        exact_boxes_at_or_above_target += int(exact_bound >= TARGET)
        if index % 25_000 == 0:
            print(
                f"exact boxes={index}/{len(heap)} "
                f"max={float(exact_max):.12g}",
                flush=True,
            )

    exact_stage_seconds = time.time() - exact_started
    result = {
        "word": "".join(map(str, WORD)),
        "length": len(WORD),
        "dimension": 2,
        "method": (
            "outward-rounded floating cover followed by exact-rational "
            "verification of every box in the final cover"
        ),
        "target_exact": "1/2000",
        "processed_float_nodes": processed,
        "final_cover_boxes": len(heap),
        "infeasible_children": infeasible,
        "float_global_upper": float_global_upper,
        "float_stage_seconds": float_stage_seconds,
        "exact_verified_boxes": len(heap),
        "exact_boxes_at_or_above_target": exact_boxes_at_or_above_target,
        "exact_global_upper_numerator": exact_max.numerator,
        "exact_global_upper_denominator": exact_max.denominator,
        "exact_global_upper_decimal": float(exact_max),
        "exact_stage_seconds": exact_stage_seconds,
        "certified_below_1_over_2000": (
            exact_boxes_at_or_above_target == 0 and exact_max < TARGET
        ),
        "coverage_argument": (
            "The root is the product of two 4-outcome simplices in six "
            "independent coordinates. Every processed feasible box is replaced "
            "by its two feasible children; infeasible children have empty "
            "intersection with the domain. Hence the final queue covers the "
            "full feasible domain. Every final box is then verified exactly."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
