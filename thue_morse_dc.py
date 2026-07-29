"""Exact deterministic complexity for finite Thue-Morse prefixes.

The definition follows Vieira and Budroni, Quantum 6, 623 (2022): the stopping
time is externally specified and a deterministic finite-state generator is a
tail followed by a cycle. The deterministic complexity is the shortest
tail-plus-cycle pattern reproducing the requested finite word.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


def thue_morse_word(level: int, seed: str = "0") -> str:
    word = seed
    translation = str.maketrans({"0": "01", "1": "10"})
    for _ in range(level):
        word = "".join(ch.translate(translation) for ch in word)
    return word


def deterministic_complexity(word: str) -> tuple[int, int, int]:
    """Return (DC, tail_length, cycle_length) for a nonempty finite word."""
    if not word:
        raise ValueError("word must be nonempty")

    length = len(word)
    for pattern_length in range(1, length + 1):
        for tail_length in range(pattern_length):
            cycle_length = pattern_length - tail_length
            valid = True
            for index in range(pattern_length, length):
                source = tail_length + ((index - tail_length) % cycle_length)
                if word[index] != word[source]:
                    valid = False
                    break
            if valid:
                return pattern_length, tail_length, cycle_length
    raise AssertionError("the full word is always a valid pattern")


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    rows = []
    for level in range(0, 11):
        word = thue_morse_word(level)
        complement = thue_morse_word(level, seed="1")
        dc, tail, cycle = deterministic_complexity(word)
        dc_bar, tail_bar, cycle_bar = deterministic_complexity(complement)
        rows.append(
            {
                "level": level,
                "length": len(word),
                "word": word if len(word) <= 64 else word[:64] + "...",
                "dc": dc,
                "tail": tail,
                "cycle": cycle,
                "complement_dc": dc_bar,
                "complement_tail": tail_bar,
                "complement_cycle": cycle_bar,
            }
        )

    json_path = output_dir / "thue_morse_dc_levels_0_10.json"
    csv_path = output_dir / "thue_morse_dc_levels_0_10.csv"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(
            f"n={row['level']:2d} L={row['length']:4d} "
            f"DC={row['dc']:4d} tail={row['tail']:4d} cycle={row['cycle']:4d}"
        )


if __name__ == "__main__":
    main()
