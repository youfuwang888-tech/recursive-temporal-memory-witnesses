# Literature and Novelty Matrix v0.3

## Frozen novelty claim

The manuscript does not claim the first classical-quantum comparison of
finite-state generators. Its defensible contributions are:

1. the exact deterministic complexity of every dyadic finite Thue-Morse word;
2. machine-auditable global classical upper certificates for the
   length-eight and length-sixteen words at memory dimension two;
3. explicit two-dimensional quantum instruments above both certified bounds;
4. a concrete noise and finite-sample implementation analysis.

## Closest work

| Work | What it establishes | Overlap | Difference retained here |
|---|---|---|---|
| Vieira and Budroni, *Quantum* 6, 623 (2022), https://doi.org/10.22331/q-2022-01-18-623 | Defines deterministic complexity for one stationary repeated binary instrument; classical survey through length 10; quantum survey through length 7 | Same operational model and optimization classes | No Thue-Morse family theorem; no length-eight quantum survey; arbitrary-sequence classical results are numerical/conjectural rather than a word-specific rational global certificate |
| Budroni, Fagundes, and Kleinmann, *NJP* 21, 093018 (2019), https://doi.org/10.1088/1367-2630/ab3cb4 | Memory cost of temporal correlations in classical, quantum, and GPT models | Dimension-bounded temporal nonclassicality | Uses temporal inequalities rather than autonomous generation probability of a frozen recursive word |
| Brierley et al., *PRL* 115, 120404 (2015), https://doi.org/10.1103/PhysRevLett.115.120404 | Temporal correlations that cannot be simulated by equal-dimensional classical information | Classical-quantum temporal separation | Different sequential measurement scenario and witness; no repeated stationary binary generator or Thue-Morse theorem |
| Vieira et al., *Quantum* 8, 1224 (2024), https://doi.org/10.22331/q-2024-01-10-1224 | Environment-dimension witnesses from temporal correlations | Memory dimension from multi-time data | Probe-environment protocol and SDP hierarchy differ from autonomous target-word generation |
| Ringbauer and Chaves, *Quantum* 1, 35 (2017), https://doi.org/10.22331/q-2017-11-25-35 | Probes nonclassicality in temporal correlations | Temporal classical-quantum distinction | Uses interventions and causal modeling rather than one stationary autonomous instrument |
| Sohbi et al., *Quantum* 5, 472 (2021), https://doi.org/10.22331/q-2021-06-10-472 | Certifies Hilbert-space dimension using sequential projective measurements | Sequential dimension witnesses | Multiple projective settings and a different certification task |
| Taranto, Elliott, and Milz, *Quantum* 7, 991 (2023), https://doi.org/10.22331/q-2023-04-27-991 | Establishes hidden quantum memory in instrument-dependent multi-time processes | Quantum memory revealed by temporal data | Different process-memory question; our manuscript explicitly makes no hidden-memory ontology claim |
| Deb, Beige, and Clark, arXiv:2604.10315 (2026), https://arxiv.org/abs/2604.10315 | Compares one-bit and one-qubit stochastic finite-state generators using temporal CHSH-like scores and delays | Same broad generator classes | Different score and scenario; no target recursive word, deterministic complexity theorem, or rational word-probability certificate |
| Garner et al., *NJP* 19, 103009 (2017), https://doi.org/10.1088/1367-2630/aa82df | Unbounded quantum memory advantage in stochastic simulation | Quantum models can use less memory than classical models | Simulates stationary stochastic processes and compares memory cost, not probability of an externally stopped finite word |
| Elliott et al., *PRL* 125, 260501 (2020), https://doi.org/10.1103/PhysRevLett.125.260501 | Extreme dimensionality reduction with quantum models | Quantum memory compression | Different process-simulation objective and causal-state construction |
| Shallit and Wang, *JALC* 6, 537 (2001) | Automatic complexity of finite strings | Finite-word state complexity | Automaton accepts/generates a word under an input model different from a clock-free repeated instrument |
| Allouche and Shallit, *Automatic Sequences* (2003) | Thue-Morse is 2-automatic | Apparent two-state description | The automaton receives digits of the time index; our generator receives no clock/index input |

## Important non-equivalences

### Two-automatic does not mean two-state autonomous generation

The standard two-state Thue-Morse automaton reads the binary digits of the
index. The temporal generator studied here receives no index, position, or
clock input. Its finite memory must autonomously encode the progress needed to
emit the requested prefix. Therefore the linear deterministic complexity does
not contradict two-automaticity.

### Numerical lower estimates are not classical upper bounds

Variational optimization supplies feasible classical probabilities and hence
lower bounds on the classical optimum. The final exact-rational box
verification is what converts each comparison into a certified separation.

### The result is not device independent

The null model assumes a stationary two-state classical memory and no hidden
clock. Experimental certification must justify these assumptions or use an
independent dimension bound.

## Search outcome

Targeted searches through July 29, 2026 found no source stating

`DC(mu^n(0)) = 3*2^(n-2)`

for the Vieira-Budroni deterministic complexity, and no source giving a
certified length-eight and length-sixteen, dimension-two classical upper
bounds together with explicit quantum violations for the corresponding
Thue-Morse words.

This is a documented novelty window, not a legal or exhaustive guarantee.
