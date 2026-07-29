$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python .\audit_thue_morse_dc_formula.py

python .\export_explicit_quantum_witness.py
python .\parameterize_exactly_feasible_quantum_witness.py
python .\certify_quantum_witness_interval.py
python .\certify_classical_d2_L8_exact_rational.py `
  --max-nodes 200000 --max-seconds 600

python .\export_exact_quantum_witness_generic.py --level 4 --digits 12
python .\certify_quantum_witness_interval_generic.py `
  --level 4 --threshold 0.00069
python .\certify_classical_d2_L16_two_stage.py

python .\analyze_quantum_witness_robustness.py
python .\make_manuscript_figures.py

$env:TECTONIC_CACHE_DIR = (Resolve-Path ".\tools\tectonic-cache").Path
.\tools\tectonic\tectonic.exe -C `
  -b "https://relay.fullyjustified.net/default_bundle_v33.tar" `
  ".\manuscript\main.tex" --keep-logs --keep-intermediates

python .\verify_release.py
