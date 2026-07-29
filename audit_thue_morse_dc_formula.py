"""Structural audit for the deterministic complexity of Thue-Morse words.

The script does more than re-run the brute-force DC calculation. It records
the two combinatorics-on-words quantities needed for a proof:

1. the longest proper border;
2. the longest suffix that occurs at an earlier position.

For an overlap-free word, any valid tail-cycle representation whose generated
suffix is longer than its cycle would create an overlap. The remaining case
reduces DC to the longest earlier occurrence of a suffix.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from thue_morse_dc import deterministic_complexity, thue_morse_word


def complement(word: str) -> str:
    return word.translate(str.maketrans({"0": "1", "1": "0"}))


def longest_proper_border(word: str) -> tuple[int, list[int]]:
    """Return the longest proper border length and all matching shifts."""
    length = len(word)
    best = 0
    shifts: list[int] = []
    for border in range(1, length):
        if word[:border] == word[length - border :]:
            if border > best:
                best = border
                shifts = [length - border]
            elif border == best:
                shifts.append(length - border)
    return best, shifts


def longest_repeated_suffix(word: str) -> tuple[int, list[int]]:
    """Return longest suffix occurring strictly before its terminal occurrence."""
    length = len(word)
    for suffix_length in range(length - 1, 0, -1):
        suffix_start = length - suffix_length
        target = word[suffix_start:]
        positions = []
        start = word.find(target, 0, suffix_start)
        while start != -1 and start < suffix_start:
            positions.append(start)
            start = word.find(target, start + 1, suffix_start)
        if positions:
            return suffix_length, positions
    return 0, []


def is_overlap_free(word: str) -> bool:
    """Check absence of factors axaxa, with x possibly empty."""
    length = len(word)
    for start in range(length):
        for period in range(1, (length - start) // 2 + 1):
            end = start + 2 * period + 1
            if end <= length and word[start : start + period + 1] == word[
                start + period : end
            ]:
                return False
    return True


def maximum_shift_match(word: str) -> tuple[int, list[dict[str, int]]]:
    """Return the longest run equal to a nonzero shift of itself."""
    length = len(word)
    best = 0
    witnesses: list[dict[str, int]] = []
    for shift in range(1, length):
        run = 0
        for index in range(length - shift):
            if word[index] == word[index + shift]:
                run += 1
                start = index - run + 1
                if run > best:
                    best = run
                    witnesses = [{"shift": shift, "start": start}]
                elif run == best:
                    witnesses.append({"shift": shift, "start": start})
            else:
                run = 0
    return best, witnesses


def valid_patterns_at_length(word: str, pattern_length: int) -> list[dict[str, int]]:
    """Enumerate all valid tail-cycle splits for a fixed pattern length."""
    length = len(word)
    valid = []
    for tail in range(pattern_length):
        cycle = pattern_length - tail
        generated = (word[tail:pattern_length] * ((length // cycle) + 2))[
            : length - pattern_length
        ]
        if word[pattern_length:] == generated:
            valid.append(
                {
                    "tail": tail,
                    "cycle": cycle,
                    "generated_suffix": length - pattern_length,
                }
            )
    return valid


def audit(max_level: int = 12) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for level in range(max_level + 1):
        word = thue_morse_word(level)
        length = len(word)
        dc, tail, cycle = deterministic_complexity(word)
        border, border_shifts = longest_proper_border(word)
        suffix, suffix_positions = longest_repeated_suffix(word)
        maximum_match, match_witnesses = maximum_shift_match(word)
        predicted = length if level < 2 else 3 * length // 4
        quarter = length // 4 if level >= 2 else None
        four_block_identity = (
            word
            == thue_morse_word(level - 2)
            + complement(thue_morse_word(level - 2))
            + complement(thue_morse_word(level - 2))
            + thue_morse_word(level - 2)
            if level >= 2
            else None
        )
        rows.append(
            {
                "level": level,
                "length": length,
                "dc": dc,
                "predicted_dc": predicted,
                "formula_match": dc == predicted,
                "minimal_tail": tail,
                "minimal_cycle": cycle,
                "minimal_valid_splits": valid_patterns_at_length(word, dc),
                "longest_border": border,
                "border_shifts": border_shifts,
                "longest_repeated_suffix": suffix,
                "suffix_positions": suffix_positions,
                "maximum_shift_match": maximum_match,
                "maximum_shift_match_witnesses": match_witnesses,
                "quarter": quarter,
                "quarter_suffix_match": suffix == quarter if level >= 2 else None,
                "quarter_shift_match": maximum_match == quarter if level >= 2 else None,
                "four_block_identity": four_block_identity,
                "overlap_free": is_overlap_free(word) if level <= 8 else "not_rechecked",
            }
        )
    return rows


def main() -> None:
    root = Path(__file__).resolve().parent
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    rows = audit()

    json_path = output_dir / "thue_morse_dc_formula_audit.json"
    csv_path = output_dir / "thue_morse_dc_formula_audit.csv"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    flat_rows = []
    for row in rows:
        flat_rows.append(
            {
                key: json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value
                for key, value in row.items()
            }
        )
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=flat_rows[0].keys())
        writer.writeheader()
        writer.writerows(flat_rows)

    for row in rows:
        print(
            f"n={row['level']:2d} N={row['length']:5d} "
            f"DC={row['dc']:5d} suffix={row['longest_repeated_suffix']:5d} "
            f"shift_match={row['maximum_shift_match']:5d} "
            f"formula={row['formula_match']}"
        )


if __name__ == "__main__":
    main()
