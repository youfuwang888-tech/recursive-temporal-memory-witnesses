# Exact Deterministic Complexity of Finite Thue-Morse Words

## Status

Proof draft v0.1. The finite computations are independent checks, not the
logical basis of the theorem.

## Definitions

Let \(\mu(0)=01\), \(\mu(1)=10\), and

\[
T_n=\mu^n(0), \qquad |T_n|=N=2^n.
\]

For a finite binary word \(w=w_0\ldots w_{N-1}\), its deterministic
complexity \(DC(w)\) is the minimum \(d=a+q\) for which a deterministic
generator consisting of a tail of length \(a\geq 0\) and a cycle of length
\(q\geq 1\) reproduces all \(N\) symbols. The stopping length \(N\) is
external.

Define the maximum self-match length

\[
M(w)=\max_{\substack{q\geq 1,\;s\geq0\\s+q<N}}
\left\{\ell:\;s+q+\ell\leq N,\;
w_{s+j}=w_{s+q+j}\text{ for }0\leq j<\ell\right\}.
\]

## Theorem

For every \(n\geq2\),

\[
\boxed{DC(T_n)=3\cdot2^{n-2}=\frac{3N}{4}.}
\]

The same formula holds for the bitwise complement \(\overline{T_n}\).

## Lemma 1: odd shifts match at most three consecutive symbols

Every length-four factor of the infinite Thue-Morse word starting at an even
position belongs to

\[
\{0101,0110,1001,1010\},
\]

whereas every length-four factor starting at an odd position belongs to

\[
\{0010,0011,0100,1011,1100,1101\}.
\]

The two sets are disjoint. Therefore two factors separated by an odd shift
cannot agree on four consecutive symbols.

This enumeration is exhaustive because an even-start length-four factor is
the image under \(\mu\) of a length-two factor, while an odd-start factor is
determined by a length-three factor and the offset inside its image.

## Lemma 2: even shifts desubstitute

The identities

\[
t_{2i}=t_i,\qquad t_{2i+1}=1-t_i
\]

imply that, for an even shift \(2r\), the equality indicator is duplicated:

\[
[t_{2i}=t_{2i+2r}]
=[t_{2i+1}=t_{2i+1+2r}]
=[t_i=t_{i+r}].
\]

Consequently, if \(q=2^s u\) with \(u\) odd, any matching run at shift \(q\)
is contained in at most \(2^s\) copies of each equality indicator generated
at the desubstituted scale. Its length is therefore at most \(2^s\) times
the longest odd-shift matching run in \(T_{n-s}\), up to truncation at the
two finite-word boundaries. Truncation can only shorten a run.

For \(n-s\geq4\), Lemma 1 gives

\[
3\cdot2^s < 2^{n-2}.
\]

The remaining terminal cases are checked directly:

- in \(T_3\), an odd shift matches at most \(2\) symbols;
- in \(T_2\), an odd shift matches at most \(1\) symbol;
- in \(T_1\), an odd shift matches no symbols.

Thus

\[
M(T_n)\leq 2^{n-2}=\frac N4.
\]

## Lemma 3: the bound is attained

Writing \(A=T_{n-2}\) and \(\bar A\) for its complement,

\[
T_n=A\,\bar A\,\bar A\,A.
\]

The prefix and suffix blocks \(A\) agree and have length \(N/4\), so a shift
of \(3N/4\) gives a matching run of length \(N/4\). Hence

\[
M(T_n)=\frac N4.
\]

## Proof of the theorem

Suppose a tail-cycle generator of total length \(d=a+q\) reproduces \(T_n\).
For every generated position \(i\geq d\), periodicity implies

\[
(T_n)_i=(T_n)_{i-q}.
\]

Therefore the word contains a self-match at shift \(q\) of length \(N-d\).
By Lemmas 1-3,

\[
N-d\leq M(T_n)=\frac N4,
\]

and hence \(d\geq3N/4\).

Conversely, the four-block identity in Lemma 3 means that a cycle containing
the first \(3N/4\) symbols, with cycle length \(q=3N/4\) and no tail,
reproduces the final \(N/4\) symbols before the external stopping event.
Thus a valid generator with \(d=3N/4\) exists. The lower and upper bounds
coincide.

Bitwise complementation preserves all equality relations, so the result also
holds for \(\overline{T_n}\).

## Independent computational checks

`audit_thue_morse_dc_formula.py` exhaustively checks the tail-cycle definition
through \(n=12\), length \(4096\), and separately computes the maximum
self-match. Every tested level satisfies

\[
DC(T_n)=3N/4,\qquad M(T_n)=N/4.
\]

## Scientific boundary

This is a finite-word/finite-memory theorem. It does not certify hidden
quantum states, QEM-8, or nonstandard physics. Its physical value depends on
a second result: a dimension-limited quantum generator must outperform the
optimal classical generator for this same sequence family under one frozen
operational protocol.
