# Omega v2 Process Interface Identifiability Report v0

Status: retained finite identifiability instrument and exact census

Date: 2026-08-03

Protocol:
[Process Interface Identifiability Protocol v0](process_interface_identifiability_protocol_v0.md)

Protocol checkpoint:
`84d3ddd` (`Preregister process interface identifiability`)

Retained run:
[20260803_022459](../validation_results/process_interface_identifiability_v0/20260803_022459/)

## Verdict

The sprint retains:

```text
a reusable finite synchronous causal model;
exact coordinate-intervention witnesses;
observational and interventional interface profiles;
a set-valued identification fiber;
an exhaustive 256-system feature census;
common-driver and copied-record negative controls;
an observational non-identifiability witness;
and a memory-update injectivity audit.
```

The construction verdict is:

```text
finite_process_interfaces_set_identified
```

All 14 preregistered cases passed. No kill condition fired.

The main result is not that one process boundary has been found. It is:

> Process-interface identification is relative to both evidence and a declared
> feature query. Observation alone can leave causal requirements unresolved.
> Complete finite interventions can identify one minimal interface in some
> systems and retain several incomparable minimal interfaces in others.

## Clean Machinery

The executable core lives in:

```text
omega_v2/finite/process_interfaces.py
```

It defines:

```text
BinarySynchronousSystem;
InfluenceWitness;
ContinuationInfluenceWitness;
ProcessInterfaceProfile;
InterfaceQuery;
InterfaceIdentification;
EvidenceMode;
IdentificationStatus;
MemoryInjectivityAudit;
ClosedLoopMapAudit.
```

The state space is the complete Boolean product over a declared component
factorization. The update map is total and deterministic. Exact
single-coordinate source interventions are therefore defined without
inventing missing states.

The analyzer enumerates every nonempty proper component subset. It retains all
certified or evidence-compatible interfaces and all inclusion-minimal members.
It never selects a representative from several incomparable minima.

This is reusable causal-analysis machinery. The Boolean synchronous adapter is
a finite laboratory, not an ontology of physical or agentic processes.

## Identification Results

### Observation only

For the primary query:

```text
persistent variation;
record acquisition;
record-sensitive outflow;
bounded continuation influence;
```

the identified-control fixture returns:

```text
status:
  UNRESOLVED

minimal evidence-compatible interfaces:
  {inside}
  {outside}
```

Observation computes persistent variation and latent-state multiplicity.
Causal features remain `UNKNOWN`. The analyzer does not convert correlation or
temporal association into causal influence.

### Complete intervention evidence

For the same system and query:

```text
status:
  IDENTIFIED

minimal certified interface:
  {inside}
```

The exact continuation witness retains:

```text
source state;
intervened source state;
changed coordinate;
baseline outside trace;
intervened outside trace.
```

Thus intervention evidence strictly shrinks the compatible interface fiber in
this fixture.

### Symmetric positive

The symmetric swap fixture returns:

```text
status:
  SET_IDENTIFIED

minimal certified interfaces:
  {left}
  {right}
```

Both are retained. No representative is selected.

This is the important global lesson: complete finite causal evidence need not
produce a unique process boundary.

## Feature Dependence

On the identified fixture, changing only the declared feature query changes:

```text
primary query:
  IDENTIFIED
  {inside}

causal-continuation query:
  SET_IDENTIFIED
  {inside}, {outside}
```

Therefore process-interface identification is feature-relative in v0. The
feature query is an instrument input, not a derived fact about the substrate.

This result blocks a silent move from:

```text
identified under this operational contract
```

to:

```text
the process boundary.
```

## Exact Feature Census

The run enumerates all:

```text
4^4 = 256
```

deterministic synchronous update maps over two Boolean components, with the
fixed initial support and horizon from the protocol.

Each rule row retains its four target states in source order:

```text
(0,0), (0,1), (1,0), (1,1).
```

Retained totals:

| Feature | True | False | Verdict | Witness rules |
| --- | ---: | ---: | --- | --- |
| persistent variation | 136 | 120 | ISOLATED | 1, 50 |
| internal influence | 192 | 64 | ISOLATED | 3, 59 |
| incoming influence | 192 | 64 | ISOLATED | 0, 17 |
| outgoing influence | 192 | 64 | ISOLATED | 0, 8 |
| latent-state multiplicity | 136 | 120 | ISOLATED | 1, 38 |
| record-sensitive outflow | 68 | 188 | ISOLATED | 6, 142 |
| continuation influence | 160 | 96 | ISOLATED | 2, 8 |

Joint feature signatures:

```text
28
```

Manifest digest:

```text
b8cda68726d7dc8fca1e13c109e316721d8556014edab43d0055ae35532f2340
```

Every `ISOLATED` verdict has an exact pair of update maps that agrees on every
other listed feature and differs on the target feature.

The result is limited to this exhaustive finite class. It is not a universal
logical-independence theorem.

`record_acquisition` is not in the independence panel because v0 defines it
as:

```text
incoming influence
and latent-state multiplicity.
```

The conjunction holds in all 256 rows. It is a derived composite, not another
primitive feature.

## Annotation and Renaming

Adding an `agent` atom to every state changes no:

```text
influence edge;
interface profile;
query fiber;
minimal interface;
or identification status.
```

A bijective component renaming transports the complete result covariantly.

This shows that the implementation does not discover a process by searching
for privileged names.

## Common-Driver Control

The common-driver fixture has two descendants whose observed values are
perfectly correlated after update.

The exact influence graph contains:

```text
driver -> left
driver -> right
```

It does not contain:

```text
left -> right
right -> left
```

The analyzer therefore distinguishes shared causal ancestry from direct
descendant influence.

## Copied-Record Control

The copied coordinate exactly receives the source's current value during
update and remains correlated with the output.

Nevertheless:

```text
copy -> output:
  absent

copy outgoing influence:
  false

copy primary-query certified:
  false
```

The copied record does not inherit the causal effect of the source it mirrors.

## Observational Non-identifiability

The retained pair has:

```text
the same component set;
the same initial support;
the same reachable observational transition rows;
and equal observational interface profiles.
```

Both observational analyses return:

```text
UNRESOLVED
```

The models differ under a declared intervention. Their `{inside}`
interventional profiles differ on outgoing influence.

Consequently:

```text
interventional equivalence implies observational equivalence;
observational equivalence does not imply interventional equivalence.
```

The second statement is also retained as an explicit finite Lean
counterexample.

## Memory-Update Injectivity

The copy and XOR controls share the same two-state world and fixed world
dynamics.

```text
copy update:
  memory' = observation

conditional update injectivity:
  false

closed-loop image:
  2 / 4 states

closed-loop injective:
  false
```

```text
XOR update:
  memory' = memory XOR observation

conditional update injectivity:
  true

closed-loop image:
  4 / 4 states

closed-loop injective:
  true
```

This establishes that non-injective record-writing is sufficient to produce
functional contraction in this matched world fixture. A reversible update can
carry the correlation without contracting the closed-loop state map.

It does not settle the earlier stochastic record-selector result. The two
updates do not implement the same memory semantics, and this sprint does not
derive a thermodynamic cost.

## Lean Spine

The clean formal module:

```text
formal/lean/OmegaV2/Finite/Identifiability.lean
```

retains:

```text
EvidenceFiber;
EvidenceRefines;
IdentifiedBy;
ObservationallyEquivalent;
InterventionallyEquivalent;

refined_fiber_subset;
identified_under_coarse_implies_identified_under_refinement;
interventional_equivalence_implies_observational_equivalence;
observational_equivalence_does_not_imply_interventional_equivalence.
```

`lake build OmegaV2` completes with 948 jobs and no placeholder theorem in the
new module.

## Validation

Canonical commands:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_omega_v2_process_interface_identifiability.py -q

.\.venv\Scripts\python.exe -m omega_v2.validation.process_interface_identifiability_v0 --out-root docs\research_notes\validation_results\process_interface_identifiability_v0

powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaV2
```

The retained run includes:

```text
summary.json
interface_profiles.csv
identification_results.csv
influence_edges.csv
independence_census.csv
independence_witnesses.csv
negative_controls.csv
memory_injectivity.csv
report.md
```

## Kill Conditions

All preregistered kill conditions are false:

```text
injected atom changed structure:
  false

component renaming changed structure:
  false

observational causality fabricated:
  false

common-driver phantom edge:
  false

copied-record phantom effect:
  false

observational pair declared identified:
  false

set-identified representative selected:
  false

census incomplete:
  false

memory controls changed world:
  false

memory-injectivity control failed:
  false
```

## Claim Boundary

This sprint establishes finite, feature-relative, set-valued process-interface
identification under an explicit component factorization and intervention
semantics.

It does not establish:

```text
a canonical component factorization;
a universally correct feature query;
process identity across arbitrary presentations;
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

Candidate inputs to May/Robust Omega no longer need to be represented only as
hand-labeled atoms. They can now be supplied as a retained family of finite
interfaces supported by declared evidence and feature contracts.

That is a real reduction in arbitrariness, but not its elimination:

```text
previously:
  one candidate boundary was inserted;

now:
  all boundaries consistent with the declared factorization, evidence, and
  feature query are retained.
```

The next interface debt is the factorization itself. A later sprint may test
transport across certified factorizations or move Robust Omega from
deterministic environment cases to adversarial/nondeterministic outcomes. This
report does neither.

## Public Compression

Exact dynamics do not automatically supply a unique process boundary.
Observation alone may leave several boundaries compatible with the data.
Interventions can shrink that evidence fiber, but even complete finite causal
evidence may retain several incomparable minimal interfaces. A process
interface should therefore be identified as a set-valued, feature-relative
object, not inserted by an `agent` label or selected by fiat.
