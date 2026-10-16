# Quantum continuation: working formalism

Version: foundation v1, 2026-10-09. This document separates adopted interpretation,
standard finite quantum mechanics, experimental evidence, and open hypotheses.
It specifies a platform for inquiry; it does not claim a new physical law.

## 1. The physical object

**Working interpretation.** Omega is the complete native physical development.
The universal evolving-state/block-Everett picture identifies the object we mean;
failure of a proposed breadth readout does not require inventing a different
physical substance. Characterizing its structure is valuable independently of
whether a unique size or ethical application is found.

**Finite physical specification.** Declare

\[
\mathsf P=(\mathcal H,\{\mathcal A(R)\},\mathscr G,H(t)),
\qquad i\hbar\partial_tU(t,s)=H(t)U(t,s).
\]

Here the region algebras/local tensor structure and constraints or physical
identifications \(\mathscr G\) are adapter inputs. The present is a positive,
trace-one \(\rho_\Sigma\), including the environment/correlations required for
sufficient evolution. Its evolution is

\[
\rho_t=U(t,0)\rho_\Sigma U(t,0)^\dagger.
\]

Preserve the complete time-ordered propagator family, local interactions and
state, not only \(\rho_T\) or the net endpoint channel. Symbolically,

\[
\Omega_{\Sigma,T}=[\mathsf P,\rho_\Sigma,\{U(t,s):0\le s\le t\le T\}]_{\rm physical\ equivalence}.
\]

The equivalence subscript is a specification obligation, not a solved universal
quotient. Any imposed pulse schedule or external work source must be declared.
Present sufficiency does not mean a subsystem's reduced density matrix alone
determines its future. Rerooting uses the full sufficient evolved present and
remaining law, without importing an extra historical narrative.

## 2. Frames, descriptions and physical changes

A frame resolves a declared part/aspect of the same physical development: region,
duration, physical resolution and relevant observable relations. It is not a
uniform prior over imagined experiments or a task menu for a chooser.

| Operation | Required treatment |
|---|---|
| Passive coordinate change | Transform state, law, local structure and readout together; invariant physical answer |
| Identity checkpoint or numerical subdivision | Contract/recompose coherently; no new physical event |
| Different physical resolution or X/Z question | A different declared view; equality of all readouts is not required |
| Actual interaction, measurement apparatus or controller | Include it in the dynamics and sufficient state |
| Physical excursion followed by reversal | Retain the intervening development; endpoint equality alone does not erase it |
| Re-root at a later present | A new residual continuation query |

A change of physical resolution must never be presented as a mere coordinate
change. Conversely, arbitrary analytical cuts cannot count as additional native
branching in a purported intrinsic readout. Local descriptions must retain enough
joint/environmental information for their intended queries; local marginals do
not by themselves reconstruct the global state.

## 3. History descriptions and exact conventions

For an exhaustive orthogonal projector family at each declared cut, define

\[
C_\alpha=P^{(n)}_{a_n}U_{n,n-1}\cdots P^{(1)}_{a_1}U_{1,0},
\quad D_{\alpha\beta}=\operatorname{Tr}(C_\alpha\rho_\Sigma C_\beta^\dagger).
\]

For a pure root, \(v_\alpha=C_\alpha\psi_\Sigma\) and our code convention is
\(D_{\alpha\beta}=\langle v_\beta|v_\alpha\rangle\). With branch vectors stored
as rows, this is `rows @ rows.conj().T`. Other index conventions may transpose
or conjugate the matrix; do not mix conventions within a calculation.

For these exhaustive projective families,

\[
\sum_\alpha C_\alpha=U(T,0),\qquad
\sum_{\alpha\beta}D_{\alpha\beta}=1,\qquad
\operatorname{Tr}D=1.
\]

The final identity is specific to this class of history expansions; it is not
the general normalization axiom for every quantum-measure representation.
Do not divide a general kernel by its trace merely to make an entropy callable.
Zero-weight branches need no new physical alternatives; tolerances must remain
numerical error handling rather than data-dependent probability repairs.

For disjoint coarse classes \(A,B\),

\[
C_A=\sum_{\alpha\in A}C_\alpha,
\quad D(A,B)=\sum_{\alpha\in A,\beta\in B}D_{\alpha\beta},
\quad \mu(A)=D(A,A).
\]

Coarse-grain amplitudes before evaluating weights. Off-diagonal terms are part
of the carrier. Although \(D\) is positive semidefinite, \(\mu\) need not be
additive or monotone under inclusion. It is therefore not already a classical
volume. Intermediate projectors do not imply physical collapse unless the
corresponding interaction is part of the model.

Medium decoherence, \(D_{\alpha\beta}=0\) for distinct alternatives, is a
sufficient condition for a classical history law \(p_\alpha=D_{\alpha\alpha}\)
on that family. It does not select the family. In the idle \(|0\rangle\) example,
one-cut Z and X families are both decoherent and give perplexities one and two.
That rules out one family-independent scalar agreeing with every such family.

## 4. Records and their extension

In the pure-state exact fixtures, orthogonal exhaustive record projections
\(R_h\) satisfy an algebraic certificate when

\[
R_h\psi_T=C_h\psi_\Sigma.
\]

This certifies correlations between a proposed record and a history family.
Native locality, actual couplings and preparation supply the additional physical
provenance. An arbitrary branch-projector construction can also pass the algebraic
equation, so the equation alone is not a selection theorem.

For stable records, later descendant projections refine the transported parent:

\[
\sum_eR_{h,e}(t')=U(t',t)R_h(t)U(t',t)^\dagger
\]

on the relevant subspace. This is a sufficient idealized regime for classical
history extension. Approximate records require explicit error, physical scale
and stability-horizon declarations; no universal threshold is adopted.

Coherent uncomputation can invalidate a particular permanent local-record
description. It does not erase the native intervening evolution. A common
global unitary preserves conditional-vector inner products; conditional eraser
readout is not global merging of orthogonal alternatives. Keep leaked records
in the sufficient environment rather than discarding them to produce erasure.

## 5. The established classical calibration

For complete lawful developments \(h\) at a declared classical resolution,

\[
L_{\rm cl}(n)=\exp H(p_n),\quad
p_{n+1}(h,e)=p_n(h)q(e|h),\quad
\log L_{\rm cl}(n+1)-\log L_{\rm cl}(n)=\sum_hp_n(h)H(q(\cdot|h)).
\]

These are standard identities once the physical history cells and their law are
specified. Using this effective number as a lushness calibration is a programme
choice; its ethical adequacy is not a theorem.

Normalization preserves probability mass, not breadth. Fair successive binary
alternatives give \(2^n\). A deterministic continuation gives one. A terminal
outcome keeps its probability and can be extended by an absorbing symbol.
Removing it and renormalizing survivors changes the conditional question.

Original-root histories keep distinct prefixes after reconvergence. Their
cumulative classical breadth cannot decrease under ordinary extension; damage
can reduce future growth relative to another preparation. This is distinct from
the residual breadth at a newly chosen root.

Independent laws multiply breadth. Coupled systems require their full joint law;
one cannot reconstruct composition from marginal breadths. Gas/noise is allowed
to win. No bonus is assigned to catalysis, complexity, organisms or repair.

## 6. Open quantum breadth requirements

Lushness remains the intended effective weighted breadth/extent. A literal volume
element, manifold, trace or positive base measure is optional. A direct functional,
profile or partial comparison is an admissible research outcome, provided its
scope and remaining incomparabilities are explicit.

For a nonempty normalized finite-resolution query, unit single-continuation
calibration motivates a minimum one. Global purity does not force that minimum.
For a fixed physically justified alternative family, weights and calibration,
investigate

\[
1\le L_{\rm Q}\le \exp H(p).
\]

This is a candidate constraint with a domain, not a theorem about all quantum
processes. Its upper comparison is the fully distinguishable classical version
of those fixed alternatives. Changed dynamics, weights, horizon or frame require
a new comparison. No universal entropy ceiling for the universe follows.

Likewise, a proposed lower bound from physically certified records applies only
through a compatible restriction. It cannot be combined with an upper bound from
an unrelated, incompatible history family. A coherent region lacking records
is not thereby assigned extent one or zero.

The Holevo readout satisfies the displayed bounds for a declared ensemble; it
still fails checkpoint invariance when fed an invented history ensemble. None
of the tested readouts is promoted to a universal quantum breadth rule.

## 7. QFT and broader physical structure

Local field dynamics is the preferred future physical adapter. Observable nets,
Schwinger-Keldysh descriptions and process tensors supply relevant tools, while
the native process remains primary. Operational slots for hypothetical
interventions are not extra worlds to count.

Typical continuum local QFT algebras are type III; the finite trace proposals do
not transfer automatically. A lattice/occupation regulator and a fixed-background
field model are not proofs of a continuum limit, Lorentz covariance, quantum
gravity or block-Everett cosmology. Thermal gas is not the QFT vacuum.

Comparative calibration remains necessary even without a base measure: use the
same physical law, resource/conserved-sector constraints, boundary conditions,
resolution and duration when asserting a matched advantage. Physical structure
also supports questions about coupling, propagation, access and emergence without
first solving scalar breadth or the ethical application.

## 8. Implementation vocabulary and claim boundaries

Existing prototypes are evidence instruments, not a completed framework API:

- `expand_history`: analytical class-operator expansion; not a physical branching
  oracle and not proof that intermediate measurements occurred.
- `decoherence_matrix`: full complex kernel in the convention above.
- `grouped_matrix`: coherent sum over a partition, not diagonal marginalization.
- `record_weights`: medium-decoherence check for a supplied mathematical family;
  it does not verify native record formation.
- `evaluate` / `record_breadth`: legacy name for the Born breadth of specified
  final alternatives. Actual records require apparatus/model provenance.
- `record_certificate`: algebraic projector/correlation check, not native-family
  discovery.
- Spectral, reference and Holevo functions: explicitly scoped diagnostics; never
  expose their numeric outputs as generic `lushness` without a new argument.

No behaviour or historical result columns are changed by this documentation.
The [claims ledger](CLAIMS_AND_EVIDENCE.md) carries numerical evidence and
limitations. The [audit specification](COMPATIBILITY_AUDIT.md) defines the next
question; this document does not declare that audit completed.

## References

- [Hartle, histories and decoherence](https://arxiv.org/abs/gr-qc/9304006).
- [Gell-Mann and Hartle, strong decoherence](https://arxiv.org/abs/gr-qc/9509054).
- [Pollock et al., multitime quantum processes](https://arxiv.org/abs/1512.00589).
- [Witten, local QFT algebras and entanglement](https://arxiv.org/abs/1803.04993).
- [Kamenev and Levchenko, real-time field methods](https://arxiv.org/abs/0901.3586).

These ground the mathematical machinery, not an identification of a known
quantity with Omega lushness.
