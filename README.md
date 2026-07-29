# Recursive Binary Words as Temporal Memory Witnesses

This repository contains the manuscript, source code, exact certificates, and
reproduction workflow for:

> **Recursive Binary Words as Dimension-Bounded Temporal Memory Witnesses**

Public repository:
<https://github.com/youfuwang888-tech/recursive-temporal-memory-witnesses>

The operational model repeats one stationary binary-output instrument on a
memory of fixed dimension. The stopping length is external; no clock, index,
position, or round label enters the device.

## Certified results

1. For the dyadic finite Thue-Morse words
   `T_n = mu^n(0)`, `mu(0)=01`, `mu(1)=10`,

   `DC(T_n) = 3*2^(n-2) = 3|T_n|/4` for every `n >= 2`.

2. For `T_3 = 01101001` and memory dimension two,

   `sup P_classical(T_3) < 3/100 < 0.0414 < P_qubit(T_3)`.

3. For `T_4 = 0110100110010110` and memory dimension two,

   `sup P_classical(T_4) < 1/2000 < 0.00069 < P_qubit(T_4)`.

The length-eight classical certificate is exact-rational throughout. The
length-sixteen certificate constructs an outward-rounded cover and then
recomputes every final box bound with exact binary rational arithmetic. The
qubit lower bounds use exactly normalized instruments and 80-digit outward
interval evaluation.

These are trusted-dimension temporal-memory witnesses. They are not
device-independent statements, do not establish hidden quantum states, and do
not modify standard finite-dimensional quantum theory.

## Quick verification

The existing machine-readable outputs can be checked in seconds:

```powershell
python .\verify_release.py
```

## Full reproduction

The full certificate build takes several minutes on a typical desktop:

```powershell
powershell -ExecutionPolicy Bypass -File .\reproduce_all.ps1
```

The workflow regenerates the deterministic audit, both classical
certificates, both quantum interval certificates, the registered noise
analysis, all figures, the manuscript PDF, and the final verification report.

## Main files

- `manuscript/main.tex`: journal manuscript source.
- `manuscript/main.pdf`: compiled manuscript.
- `manuscript/quantumarticle.cls`: journal class used for compilation.
- `thue_morse_dc_theorem_v0_1.md`: detailed theorem notes.
- `certify_classical_d2_L8_exact_rational.py`: length-eight global bound.
- `certify_classical_d2_L16_two_stage.py`: length-sixteen global bound.
- `certify_quantum_witness_interval.py`: length-eight qubit certificate.
- `certify_quantum_witness_interval_generic.py`: length-sixteen qubit
  certificate.
- `outputs/`: machine-readable certificate and analysis outputs.

Earlier structural exploration files are retained for research provenance but
are not premises of the paper's operational claims.

## Environment

The release was tested with Python 3.12.8. Exact package versions are listed
in `requirements.txt`. The manuscript uses the official `quantumarticle`
class and is built locally with Tectonic.

## License and citation

Code is released under the MIT License. Manuscript text and figures are
released under CC BY 4.0. Citation metadata are in `CITATION.cff`.
