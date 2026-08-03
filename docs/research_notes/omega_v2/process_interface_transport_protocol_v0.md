# Omega v2 Process Interface Transport Protocol v0

Status: preregistration / finite factorization-transport protocol

Date: 2026-08-03

## Purpose

Process Interface Identifiability v0 retained all minimal component subsets
compatible with declared evidence and a declared feature query. It did not
derive the component factorization on which those subsets were defined.

This sprint asks:

> When two finite component factorizations describe the same exact dynamics,
> which process-interface results transport between them, and when must the
> transport be refused?

The sprint tests stability under finite partitions. It does not search for a
canonical factorization.

## Claim Boundary

This sprint is not:

```text
process identity;
agency;
valuerhood;
consciousness;
patienthood;
standing;
value;
responsibility;
moral license;
or Omega validation.
```

It does not claim that one factorization is physically correct. It does not
infer a process from a name, annotation, observer choice, or preferred scale.

## Fixed Substrate

All comparisons use one exact finite Boolean synchronous system:

```text
primitive component set:
  C

state space:
  {0,1}^C

total deterministic update:
  T : {0,1}^C -> {0,1}^C

initial support:
  I subseteq {0,1}^C
```

The exact primitive transition table, initial support, evidence mode, horizon,
and feature query are fixed during a comparison.

Changing any of those inputs is not a factorization transport.

## Component Factorization

A component factorization is a finite partition of `C`:

```text
P = {B_1, ..., B_n}
```

such that:

```text
every block is nonempty;
blocks are pairwise disjoint;
their union is C.
```

Block identifiers are presentation labels only. A candidate interface is a
nonempty proper family of blocks. Its concrete support is the union of the
primitive components in those blocks.

Interface features are evaluated on that concrete support using the exact
v0 process-interface analyzer.

## Exact Intervention Transport

For source factorization `P` and target factorization `Q`, a source block
`B in P` is exactly expressible in `Q` iff it is a union of target blocks:

```text
B = union {D in Q | D subseteq B}.
```

The transport `P -> Q` is intervention-preserving iff every source block is
exactly expressible in `Q`.

Equivalently, `Q` refines `P`.

This condition is operational:

```text
setting every primitive coordinate in B
```

must decompose into target-block settings without also setting a primitive
coordinate outside `B`.

The checker must retain, for every failed source block:

```text
source block;
source members;
overlapping target blocks;
unavoidably added target members.
```

No approximate or best-effort intervention transport is allowed in v0.

## Interface Representation

For a concrete primitive subset `S subset C`, a target factorization represents
`S` exactly iff `S` is a union of target blocks.

If not, the target saturation is:

```text
Sat_Q(S) =
  union {D in Q | D intersects S}.
```

Saturation is retained as diagnostic evidence. It is not treated as exact
transport.

## Evidence and Query Controls

An interface-family comparison is valid only when both sides use:

```text
the same exact substrate;
the same initial support;
the same evidence mode;
the same horizon;
the same InterfaceQuery.
```

A query mismatch is an obstruction, not a transported verdict.

Observation-only comparisons retain causal fields as `UNKNOWN`, as in the
predecessor sprint.

## Verdict Classes

The comparison returns one of:

```text
INVARIANT:
  both retained minimal families have the same concrete primitive supports,
  and those supports are exactly representable on both sides.

REFINED:
  the target factorization is intervention-preserving from the source and
  exposes one or more strictly smaller retained minimal concrete supports.

MERGED:
  the reverse transport is intervention-preserving, and the target retains
  one or more strictly larger minimal supports produced by block merging.

OBSTRUCTED:
  an exact intervention or retained interface cannot be transported, the
  feature/query contract changes, or neither directional refinement relation
  accounts for the two retained families.

UNRESOLVED:
  evidence leaves causal requirements unknown on either side.
```

`REFINED` and `MERGED` are descriptions of the declared finite comparison.
They do not rank factorizations by truth or moral importance.

## Batch A: Reusable Finite Machinery

Add:

```text
omega_v2/finite/component_factorizations.py
```

Minimal objects:

```text
FactorBlock;
ComponentFactorization;
FactorizedInterfaceProfile;
FactorizedInterfaceIdentification;
BlockTransport;
BlockTransportFailure;
InterventionTransportAudit;
InterfaceTransportStatus;
InterfaceFamilyTransport.
```

Required functions:

```text
factorized_interface_profiles;
identify_factorized_interfaces;
audit_intervention_transport;
represent_interface;
saturate_interface;
compare_interface_families.
```

All returned families and witnesses must be deterministic and serializable.

## Batch B: Exact Positive Controls

### Block relabeling

Two factorizations with the same blocks and different block identifiers must
return:

```text
INVARIANT
```

with equal concrete profile families and bidirectional exact intervention
transport.

### Harmless refinement

A target factorization splits one source block. The exact source intervention
must decompose into target interventions.

If the target query exposes a strictly smaller minimal interface, return:

```text
REFINED
```

and retain every target minimum.

### Reverse merge

Reverse the preceding comparison. If the coarse target can represent only the
larger retained interface, return:

```text
MERGED
```

The merged support must be reported explicitly.

## Batch C: Negative Controls

### Cross-cut obstruction

Use four primitive components and partitions of the form:

```text
source:
  {a,b}, {c,d}

target:
  {a,c}, {b,d}
```

Both presentations observe the same exact transition system. Neither
factorization refines the other.

The intervention checker must return explicit failed-block witnesses and the
family comparison must return:

```text
OBSTRUCTED
```

Observation equality must not override the failed intervention transport.

### Feature-query mismatch

Hold substrate, factorization, evidence, and horizon fixed; change only the
query. Transport must be refused as:

```text
OBSTRUCTED
```

### Several refined minima

A coarse source interface refines into several incomparable target minima.
The result must retain all minima and return `REFINED`. It must not select one.

### Annotation invariance

Adding state annotations must not change any partition, intervention audit, or
transport verdict.

## Batch D: Lean Transport Spine

Add:

```text
formal/lean/OmegaV2/Finite/InterfaceTransport.lean
```

The formal layer may remain independent of the Python adapter.

Required objects:

```text
InterfaceEquivalence;
FeatureFiber.
```

Required theorem content:

```text
an interface bijection that preserves the declared feature profile transports
the complete feature fiber;

unique identification transports across such an equivalence;

a non-injective merge need not preserve identification.
```

The final item must be an explicit finite counterexample, not an axiom.

No `sorry`, `admit`, placeholder theorem, or imported historical Omega
namespace is permitted.

## Batch E: Validation and Retained Artifacts

Add:

```text
omega_v2/experiments/process_interface_transport_v0.py
omega_v2/validation/process_interface_transport_v0.py
tests/test_omega_v2_process_interface_transport.py
docs/research_notes/omega_v2/process_interface_transport_report_v0.md
```

The retained run must include:

```text
summary.json;
factorizations.csv;
block_transport.csv;
interface_profiles.csv;
family_transport.csv;
negative_controls.csv;
report.md.
```

## Success Conditions

The sprint is retained only if:

```text
1. the partition validator rejects overlap, omission, and empty blocks;
2. relabeling returns INVARIANT;
3. refinement returns REFINED with exact block decompositions;
4. reverse comparison returns MERGED;
5. several refined minima remain set-valued;
6. cross-cut partitions return explicit intervention failures;
7. query mismatch returns OBSTRUCTED;
8. annotations change no structural result;
9. observation equality cannot override intervention failure;
10. the Lean transport theorems compile without placeholders;
11. the full Python and Lean regression suites remain green.
```

## Kill Conditions

Stop and report failure if:

```text
a factorization omits or duplicates a primitive component;
an intervention touching extra primitive components is called exact;
an unrepresentable interface is silently saturated and accepted;
one target is selected from several incomparable minima;
a query mismatch is reported as invariant;
observational equality is treated as causal transport;
the implementation requires changing retained predecessor verdicts;
or the docs promote the result to identity, agency, valuerhood, or value.
```

## Public Compression

A process boundary identified in one component decomposition need not survive
another. Exact transport requires more than observing the same dynamics: the
new decomposition must be able to express the relevant interventions and
feature query without adding or erasing primitive components. When several
transported boundaries remain possible, the result stays set-valued.
