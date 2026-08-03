# Omega v2 Process Interface Transport Report v0

Status: retained finite factorization-transport instrument

Date: 2026-08-03

Protocol:
[Process Interface Transport Protocol v0](process_interface_transport_protocol_v0.md)

Protocol checkpoint:
`4583f82` (`Preregister process interface transport`)

Retained run:
[20260803_143204](../validation_results/process_interface_transport_v0/20260803_143204/)

## Verdict

The sprint retains:

```text
a validated finite component-partition object;
exact block-intervention decomposition;
explicit failed-transport witnesses;
factorization-relative interface profiling;
set-valued interface-family comparison;
and a small Lean transport spine.
```

The construction verdict is:

```text
finite_process_interface_transport_classified
```

All 11 preregistered cases passed. No kill condition fired.

The main result is:

> Process-interface results transport exactly across block relabeling and can
> be compared across genuine partition refinement. They do not transport
> merely because two presentations observe the same exact dynamics. A
> cross-cutting partition can make the required interventions inexpressible.

## Mathematical Object

The executable core is:

```text
omega_v2/finite/component_factorizations.py
```

For a fixed primitive component set `C`, a factorization is a partition:

```text
P = {B_1, ..., B_n}
```

The implementation rejects:

```text
empty blocks;
overlapping blocks;
omitted primitive components;
unknown primitive components;
and duplicate block identifiers.
```

A candidate interface is a nonempty proper family of blocks. Its concrete
support is their union in `C`. The existing process-interface feature analyzer
then evaluates that concrete primitive subset.

This reuses the predecessor machinery rather than assigning new semantics to
block names.

## Intervention Transport

For source partition `P` and target partition `Q`, a source block transports
exactly only when it is a union of target blocks.

Operationally:

```text
one source-block setting
```

must decompose into:

```text
target-block settings touching exactly the same primitive components.
```

The audit returns either:

```text
BlockTransport:
  source block;
  exact target blocks;
  equal concrete member set.
```

or:

```text
BlockTransportFailure:
  source block;
  overlapping target blocks;
  source members not covered by admissible contained blocks;
  target members that would be added.
```

The checker does not silently replace an unrepresentable interface by its
target saturation.

## Relabeling Invariance

The fine partition:

```text
{inside}, {aux}, {outside}
```

and a version with different block identifiers return:

```text
status:
  INVARIANT

minimal concrete family:
  {inside}

forward intervention transport:
  exact

reverse intervention transport:
  exact
```

Block names therefore do not affect the result.

## Strict Refinement

The coarse partition is:

```text
{inside, aux}, {outside}
```

Its retained primary-query minimum is:

```text
{inside, aux}
```

The fine partition splits the first block:

```text
{inside}, {aux}, {outside}
```

Its retained minimum is:

```text
{inside}
```

Every coarse intervention decomposes exactly in the fine partition:

```text
{inside, aux}
  -> {inside} + {aux}

{outside}
  -> {outside}
```

The comparison therefore returns:

```text
REFINED
```

This does not say that finer is universally better. It says that this exact
refinement exposes a strictly smaller minimum under the fixed evidence,
horizon, and feature query.

## Reverse Merge

Reversing the comparison returns:

```text
MERGED
```

The fine interface:

```text
{inside}
```

cannot be set through the coarse partition without also touching:

```text
{aux}
```

The coarse minimum is therefore reported explicitly as:

```text
{inside, aux}
```

It is not treated as an exact image of `{inside}`.

## Several Refined Minima

A symmetric three-component fixture uses:

```text
coarse:
  {left, right}, {sink}

fine:
  {left}, {right}, {sink}
```

Under the same persistent-causal-outflow query:

```text
coarse minimum:
  {left, right}

fine minima:
  {left}
  {right}
```

The comparison returns:

```text
REFINED
```

Both fine minima are retained. The implementation does not select a preferred
representative.

## Cross-cut Obstruction

The negative fixture uses one fixed four-bit reversible rotation and two
partitions:

```text
source:
  {a,b}, {c,d}

target:
  {a,c}, {b,d}
```

The exact dynamics, initial support, evidence mode, horizon, and feature query
are identical.

Each source block intersects both target blocks. For example, representing:

```text
{a,b}
```

in the target requires:

```text
{a,c} + {b,d}
```

which saturates to:

```text
{a,b,c,d}
```

and unavoidably adds:

```text
{c,d}.
```

Both directional intervention audits fail with explicit witnesses. The family
comparison returns:

```text
OBSTRUCTED
```

This remains true even though the observational signature is identical.

The result demonstrates:

```text
same observed dynamics
does not imply
transportable process interventions.
```

## Query and Evidence Controls

Changing only the feature query returns:

```text
OBSTRUCTED
reason:
  query_mismatch
```

A verdict relative to one operational query is not transported as though the
query were unchanged.

Under observation-only evidence, the refinement comparison returns:

```text
UNRESOLVED
```

Causal feature fields remain unknown. Partition refinement does not convert
observation into intervention evidence.

## Annotation Control

Adding an `agent` state annotation changes no:

```text
partition;
primitive dynamics;
interface profile;
minimal concrete family;
intervention audit;
or transport verdict.
```

The comparison remains:

```text
INVARIANT
```

## Verdict Vocabulary

The retained implementation distinguishes:

```text
INVARIANT:
  equal concrete minimal families under an exact partition relation.

REFINED:
  an exact target refinement exposes strictly smaller minima.

MERGED:
  the target block structure retains strictly larger merged minima.

OBSTRUCTED:
  substrate, query, evidence, intervention, or family transport fails.

UNRESOLVED:
  available evidence leaves required causal features unknown.
```

These are finite audit outcomes, not rankings of ontological truth.

## Lean Spine

The clean formal module:

```text
formal/lean/OmegaV2/Finite/InterfaceTransport.lean
```

defines:

```text
FeatureFiber;
UniquelyIdentified;
InterfaceEquivalence.
```

It retains:

```text
InterfaceEquivalence.image_featureFiber;
InterfaceEquivalence.uniquelyIdentified_toTarget;
noninjective_merge_can_erase_identification.
```

Thus a bijective, feature-preserving interface map transports the complete
feature fiber and unique identification. An explicit Boolean-to-unit merge
shows that non-injective merging can erase an identifying feature.

`lake build OmegaV2` completes with 949 jobs and no placeholder theorem in the
new module.

## Validation

Canonical commands:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_omega_v2_process_interface_transport.py -q

.\.venv\Scripts\python.exe -m omega_v2.validation.process_interface_transport_v0 --out-root docs\research_notes\validation_results\process_interface_transport_v0

powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaV2
```

The retained run includes:

```text
summary.json
factorizations.csv
block_transport.csv
interface_profiles.csv
family_transport.csv
negative_controls.csv
report.md
```

## Kill Conditions

All preregistered kill conditions are false:

```text
invalid partition accepted:
  false

relabeling changed family:
  false

refinement not decomposable:
  false

merge reported exact forward:
  false

refined representative selected:
  false

cross-cut called exact:
  false

saturation silently accepted:
  false

query mismatch called invariant:
  false

observational causality claimed:
  false
```

## Practical Boundary

This is exact finite machinery. Applying it to a real system requires:

```text
a candidate primitive decomposition;
a fitted or otherwise justified causal transition model;
an intervention semantics;
uncertainty bounds;
and a declared feature query.
```

When those inputs cannot be supported, the appropriate result is unresolved,
not a guessed process boundary.

The checker is nevertheless practical as a finite audit: for a supplied model
and pair of decompositions, it returns exact block transports or concrete
counterexamples.

## Claim Boundary

This sprint establishes finite, factorization-relative transport of
feature-defined interface families.

It does not establish:

```text
a canonical primitive decomposition;
a canonical component factorization;
a universally correct process-feature query;
identity across arbitrary physical scales;
agency;
consciousness;
valuerhood;
patienthood;
standing;
value;
responsibility;
moral license;
or Omega validation.
```

## Implication for Omega v2

The predecessor sprint replaced one inserted process label with a set of
evidence-compatible interfaces. This sprint adds a second guard:

```text
an interface family may enter a new factorization only with an explicit
transport classification.
```

This reduces another silent declaration:

```text
before:
  a component decomposition was supplied and then forgotten;

now:
  the decomposition remains indexed, and changes of decomposition must carry
  exact intervention evidence or an obstruction.
```

The result still does not derive the decomposition itself.

## Next Debt

The most useful next Omega v2 experiment is not another factorization class.
It is the strict Robust fixture in which:

```text
the May triple is nonempty;
every pair is robustly securable;
the full triple is not robustly securable across the declared environment
scope.
```

That would isolate joint indefensibility from joint unrealizability before
moving Robust Omega toward generated controllers and adversarial or stochastic
environments.

Separately, real-system interface transport will eventually need approximate
causal models and uncertainty-aware intervention contracts. Those are not part
of v0.

## Public Compression

A process boundary found in one decomposition need not survive another.
Relabelings preserve the result, and genuine refinements can expose smaller
candidate interfaces. But two decompositions of the same observed dynamics
may cut across one another so that neither can express the other's
interventions. In that case the correct result is an explicit obstruction,
not a translated identity claim.
