"""Fast machine checks for every claim displayed in the manuscript."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs"


def load(name: str):
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def main() -> None:
    dc = load("thue_morse_dc_formula_audit.json")
    assert all(row["formula_match"] for row in dc)
    assert all(
        row["dc"] == 3 * row["length"] // 4
        for row in dc
        if row["level"] >= 2
    )

    c8 = load("thue_morse_L8_d2_exact_rational_certificate.json")
    c8_exact = Fraction(
        c8["exact_global_upper_numerator"],
        c8["exact_global_upper_denominator"],
    )
    assert c8["separation_certified"]
    assert c8_exact < Fraction(3, 100)

    q8 = load("thue_morse_L8_d2_quantum_interval_certificate.json")
    assert q8["certified_above_0p0414"]
    assert q8["probability_lower"] > 0.0414

    c16 = load("thue_morse_L16_d2_two_stage_exact_certificate.json")
    c16_exact = Fraction(
        c16["exact_global_upper_numerator"],
        c16["exact_global_upper_denominator"],
    )
    assert c16["certified_below_1_over_2000"]
    assert c16["exact_boxes_at_or_above_target"] == 0
    assert c16_exact < Fraction(1, 2000)

    q16 = load("thue_morse_L16_d2_quantum_interval_certificate.json")
    assert q16["certified_above_threshold"]
    assert q16["probability_lower"] > 0.00069

    noise = load("thue_morse_L8_d2_noise_and_shots.json")
    assert noise["ideal_quantum_probability_recomputed"] > 0.0414
    assert 0.08 < noise["critical_eta_where_probability_equals_0p03"] < 0.09

    manuscript = (ROOT / "manuscript/main.tex").read_text(encoding="utf-8")
    for text in (
        r"\DC(T_n)=3\,2^{n-2}",
        r"\frac{3}{100}",
        r"\frac{1}{2000}",
        "0.0414",
        "0.00069",
    ):
        assert text in manuscript
    assert (ROOT / "manuscript/main.pdf").is_file()

    report = {
        "status": "PASS",
        "deterministic_levels_checked": len(dc),
        "L8_classical_exact_upper": float(c8_exact),
        "L8_quantum_interval_lower": q8["probability_lower"],
        "L16_classical_exact_upper": float(c16_exact),
        "L16_quantum_interval_lower": q16["probability_lower"],
        "manuscript_pdf_bytes": (ROOT / "manuscript/main.pdf").stat().st_size,
    }
    path = OUTPUT / "release_verification.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
