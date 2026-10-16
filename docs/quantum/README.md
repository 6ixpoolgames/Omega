# Quantum continuation foundation

Working platform, 2026-10-09. This is the entry point for the quantum formalism
supporting the [v4 full draft](../cosmology/v4/README.md) and subsequent research.
It does not supply a completed definition of quantum lushness.

## Read in this order

1. [Formalism](FORMALISM.md): physical object, frames, conventions, composition,
   classical boundary and candidate breadth requirements.
2. [Claims and evidence](CLAIMS_AND_EVIDENCE.md): what each probe established,
   what it did not establish, and the source/test links.
3. [Compatibility audit specification](COMPATIBILITY_AUDIT.md): the next bounded
   mathematical task, before another measure or larger field simulation.

## Scope and current decisions

The research object is the native quantum development of a sufficient present,
with its physical law, local structure and constraints. The block-Everett picture
is the adopted interpretive setting; the probes do not validate that cosmology.

Characterizing possibility structure has independent scientific value: access,
obstruction, composition, propagation, memory, recovery and emergence remain
research targets even without a universal scalar. Lushness asks about effective
weighted breadth. Ethics and cosmological interpretation are further applications,
not prerequisites for the physical work to count as progress.

Two adopted pivots govern this platform:

- [Effective breadth](../research_notes/omega_v2/effective_breadth_pivot_2026-10-09.md):
  a literal geometric volume/base measure is optional.
- [QFT foundation](../research_notes/omega_v2/qft_foundation_pivot_2026-10-09.md):
  native local field dynamics is the preferred physical foundation; existing
  circuits remain exact fixtures. The larger field adapter follows the audit.

## What v4 carries forward

- The native physical carrier and distinctions between its representations.
- Classical complete-history perplexity as a declared calibration.
- Explicit conditional quantum bounds as hypotheses to test.
- Finite record/extension certificates and the observed failures of candidate
  readouts as evidence, with their declared model scope.
- The open mathematical question: an invariant effective breadth, profile or
  comparison on physically justified continuation structure.

Do not carry forward a chosen entropy as universal lushness, a compulsory trace
or volume element, purity as a branch count, or a failed record certificate as
evidence of no possibility. No published result here derives value from breadth.

## Implementation status

The prototype implementation is in `omega_v2/finite`; exact probe runners are in
`omega_v2/validation`. History projectors are separate analytical inputs from the
unitaries. The current tuple-based API does not enforce physical provenance of
every projector family. Calling a quantity `record_breadth` in legacy code is not
a proof that an actual record exists; see the formalism's implementation notes.

The cleanup preserves existing experiment code and reports. It does not refactor
the physics, introduce new experiments, or silently redefine old result columns.
Raw outputs stay in ignored `results/local_runs/` and are not publication inputs.

This folder supplies the working formulation. Earlier notes remain historical
proposals and reports. The [October 9 consolidation](../research_notes/omega_v2/field_first_consolidation_v1.md)
is retained as context; this entry point states the present research interface.

For the broader synthesis, read [Omega Cosmology v4](../cosmology/v4/README.md).
The [foundation review](../cosmology/v4-preparation/FOUNDATION_REVIEW.md)
remains the earlier drafting brief. The v4 publication adds the synthesis without
promoting the compatibility audit specification into a completed result.
