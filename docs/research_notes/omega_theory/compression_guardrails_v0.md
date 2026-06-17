# Compression Guardrails v0

Status: claims-hygiene note
Scope: current Layer A compression pass
Claim boundary: not a new theorem layer; not Omega validation

## Purpose

The current formal stack is being compressed into standard patterns:

```text
presentation soundness = forbidden-merge kernel avoidance
deformation/proxy failure = non-factorization
profile abstraction = sound/complete approximation
carrier validity = denotation plus certificate
```

That compression is useful. It makes repeated proof shapes visible and makes
the project easier to audit from standard mathematical language.

It is also dangerous if used too aggressively.

The rule is:

```text
Compress the proof pattern.
Do not erase the domain meaning.
```

## Over-Compression Risks

### 1. Hiding supplied structure

Bad compression:

```text
Alpha derives consequence, dynamics, safety, and recurrence.
```

Better:

```text
Alpha supplies primitive apartness and path candidates.
Adapters supply consequence exposure, dynamics realization, safety, and
recurrence.
```

The compression should not make adapter-supplied structure look derived.

### 2. Collapsing different forbidden relations

Many soundness checks have the same generic form:

```text
present x = present y -> not Forbidden x y
```

But the forbidden relation matters:

```text
PrimitiveApart
ConsequenceMergeSeparated
TargetSeparatedBy
certified carrier endpoint distinction
```

These are not interchangeable. The generic theorem should live underneath the
domain theorem, not replace it in public-facing claims.

### 3. Treating non-factorization as all deformation

Non-factorization is the right finite shape for many proxy failures:

```text
same summary, different declared fact
```

But not every future deformation has already been reduced to a summary/target
pair. Richer adapter work may need dynamics, probability, perturbation,
control, recurrence, or trajectory-language structure.

### 4. Treating sound approximation as truth

Sound approximation says:

```text
abstract claim -> declared exact claim
```

It does not say the declared exact claim is the right measurement of the real
substrate. That remains an adapter/provenance question.

### 5. Turning sufficient contracts into necessary laws

Transfer contracts are often sufficient conditions:

```text
if these preservation obligations hold, carrying transfers
```

That does not mean the obligations are necessary, natural, or exhaustive.
Path-level transfer, relation simulation, support extension, and lineage
handoff already exist because earlier same-support and edge-preservation
contracts were too strict.

### 6. Reintroducing identity through carrier language

Carrier candidates, generated carriers, and carrier certificates are useful.
They should not be read as object identity, selfhood, or boundary realism.

The current safe statement is:

```text
this declared carrier presentation has a certificate for carrying this
consequence distinction under these dynamics and safety assumptions
```

not:

```text
this is the same object through time
```

## Names Worth Keeping

Some names should remain local even when their proof shapes compress:

```text
PrimitiveApart
ConsequenceMergeSeparated
TargetSeparatedBy
ConsequenceExposesPrimitiveApartness
DynamicsRealizesPrimitiveRel
CarrierCertificate
GeneratedCarrier
CarrierSemantics
RecurrentSupportCarries
```

These names tell readers what kind of structure is being checked. Replacing
all of them with generic words like `Forbidden`, `Fact`, or `SoundApprox`
would make the mathematics shorter but the theory less legible.

## Recommended Pattern

Use a two-level presentation:

```text
Generic theorem:
  the small standard proof pattern.

Domain theorem:
  the same pattern specialized to primitive apartness, consequence separation,
  target preservation, carrier certification, profile abstraction, or
  recurrent carrying.
```

This gives outside reviewers the standard mathematics while preserving the
reason each contract matters for the larger project.

## Compression Status

Good current compression:

```text
SoundQuotient:
  kernel containment in consequence-identifiability.

PresentationSoundness:
  generic forbidden-merge kernel avoidance.

ContinuationDeformation:
  finite deformation/proxy failure as non-factorization.

ApproximationContract:
  sound/complete approximation.

CarrierSemantics:
  raw supports, generated carriers, and trajectory-language views as carrier
  presentations.
```

Places not to compress further yet:

```text
Alpha exposure into consequence;
Alpha realization into dynamics;
carrier certificate semantics;
simulation transfer;
recurrent carrying versus endpoint viability;
joint recurrent support;
adapter provenance.
```

Those distinctions still carry substantive claim boundaries.

## Related Notes

- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [presentation_soundness_pattern_v0.md](presentation_soundness_pattern_v0.md)
- [continuation_deformation_nonfactorization_v0.md](continuation_deformation_nonfactorization_v0.md)
- [approximation_contract_v0.md](approximation_contract_v0.md)
