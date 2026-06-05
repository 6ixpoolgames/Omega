# OmegaAdapters Finite Channel Decoder Provenance v0

Status: Lean-checked decoder provenance repair
Scope: finite channel recovery, decoder registries, and anti-self-validation counterexamples

## Purpose

This pass separates channel capacity from instrument-facing decoder evidence.

The older finite-channel recovery surface remains available:

```text
ExactRecovers:
  existence-style exact recovery; some decoder works.
```

The new provenance layer adds:

```text
RegisteredExactRecovers:
  a decoder drawn from a supplied registry works.

DeclaredRegisteredExactRecovers:
  the supplied registry is marked declared and contains a working decoder.
```

This blocks the invalid compression:

```text
some decoder exists
=
the declared instrument recovered the distinction
```

## Lean Artifact

Added:

```text
formal/lean/OmegaAdapters/FiniteChannelDecoderNative.lean
```

Updated:

```text
formal/lean/OmegaAdapters/FiniteChannelNative.lean
formal/lean/OmegaAdapters/FiniteChannel.lean
formal/lean/OmegaAdapters.lean
```

## Definitions

The provenance module defines:

```text
DecoderPolicy
DecoderSpec
DecoderRegistry
SpecExactRecovers
RegisteredExactRecovers
DeclaredRegisteredExactRecovers
ExistsExactRecovers
```

`ExistsExactRecovers` is an explicit alias for the older `ExactRecovers`
surface.

## Checked Direction

The checked theorem direction is intentionally one-way:

```text
registered_exact_implies_exists_exact
declared_registered_exact_implies_exists_exact
spec_declared_exact_implies_exists_exact
```

No theorem proves that existence-style recovery implies registered or declared
recovery.

## Counterexamples

The module includes finite counterexamples:

```text
exists_exact_not_empty_registered:
  a working decoder exists, but an empty declared registry does not recover.

bad_declared_registry_but_exists_exact:
  the channel has recoverable information, but the declared registry fails.

bad_declared_good_exists:
  a good supplied decoder works, a bad supplied decoder fails, and existence
  recovery still holds.
```

These examples are the guardrail: post-hoc decoder existence cannot masquerade
as registered instrument recovery.

## Empirical Consequence

Future registry-first stochastic channel data should be generated in this
order:

```text
1. Declare carriers, distinctions, priors, and target observations.
2. Generate decoder registries from declared rules.
3. Freeze and digest the registry manifest.
4. Score channels against frozen registries.
5. Score optimized/exhaustive decoders separately as diagnostics.
```

Lean can enforce that theorem surfaces require a registry. The empirical side
must enforce historical provenance, such as whether the registry existed before
scoring.

## Validation

Validated by:

```powershell
lake build OmegaAdapters
```
