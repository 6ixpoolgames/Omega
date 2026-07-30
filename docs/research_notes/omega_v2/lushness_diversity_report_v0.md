# Lushness Diversity Pilot Report v0

Status: retained post-freeze finite pilot

Scope: duplicate-resistant continuation-attribute coverage, effective freedom
under plural possible preferences, and higher-order joint-realizability controls

Claim boundary: not value, standing, autonomy, patienthood, population ethics,
moral aggregation, universal lushness, paperclipper defeat, or Omega validation

## Protocol

Preregistered protocol:

```text
docs/research_notes/omega_v2/lushness_diversity_protocol_v0.md
```

Protocol commit:

```text
7290567 Preregister finite lushness diversity pilot
```

The protocol was committed before implementation and before the retained run.

## Validation

Focused test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_finite_relational_lushness_diversity.py -q
```

Result:

```text
13 passed
```

Full Python regression:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Result:

```text
433 passed
```

Focused lint:

```powershell
.\.venv\Scripts\python.exe -m ruff check omega\adapters\finite_relational\lushness_diversity.py omega\validation\finite_relational_lushness_diversity.py tests\test_finite_relational_lushness_diversity.py
```

Result:

```text
all checks passed
```

Repository-wide Ruff remains red on pre-existing historical-notebook lint debt.
No unrelated lint findings were changed during this pilot.

Retained run:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_lushness_diversity --out-root docs\research_notes\validation_results\lushness_diversity_v0
```

Retained output:

```text
docs/research_notes/validation_results/lushness_diversity_v0/20260730_121622/
```

Files:

```text
summary.json
case_results.csv
profiles.csv
report.md
```

## Verdict

```text
retained
```

All six preregistered cases and all negative controls passed.

The retained primary instrument is:

```text
profile inclusion over declared continuation attributes of jointly realizable
families
```

The Foster-style instrument remains separate:

```text
intersection of indirect-utility rankings over a declared family of possible
preferences
```

## Evidence Reclassification

All six retained cases in this pilot are instrument-correctness or consistency
checks.

In particular:

```text
pairwise shadow:
  confirms that the declared compatibility complex distinguishes a filled
  triangle from a hand-declared hollow triangle. It does not show that
  non-flagness emerges from underlying dynamics.

excisive paperclipper:
  confirms that the declared cooperative attribute profile strictly contains
  the declared excisive profile while a local paperclip score reverses the
  comparison. It does not independently derive those attributes.
```

The pilot therefore has:

```text
instrument-correctness results: 6
risky theory-discovery results: 0
```

The later adaptive-versus-switching dynamics case is the first result in this
post-freeze sequence classified as a risky finite separation.

## Results

### Duplicate resistance

The base and duplicated families have different token counts but the same
profile:

```text
base:
  {correction, persistence}

duplicate extension:
  {correction, persistence}
```

Verdict:

```text
equivalent
```

### Non-fungible extension

Adding a compatible trajectory carrying a previously uncovered attribute gives:

```text
base:
  {correction, persistence}

extension:
  {correction, persistence, translation}
```

Verdict:

```text
extension strictly refines base
```

The duplicate and non-fungible extensions have the same token count. The
profile order distinguishes them while cardinality does not.

### Pairwise shadow

The filled and hollow three-trajectory structures have:

```text
the same vertices;
the same compatibility edges;
the same singleton profiles;
the same pair profiles.
```

They differ at the triple:

```text
filled:
  triple jointly realizable;
  flag;
  realizes triadic_coordination.

hollow:
  every pair jointly realizable;
  triple not jointly realizable;
  not flag;
  triple profile request rejected.
```

This is a finite witness that pairwise compatibility does not determine joint
realizability. The relevant exact condition is flagness of the compatibility
complex. No identification with Nehring-Puppe attribute acyclicity is claimed.

### Effective freedom boundary

Three controls were retained:

```text
agreement:
  structural coverage and effective freedom both rank the extension higher.

coverage-only:
  the structural grammar sees a new attribute;
  every declared preference ignores it;
  coverage is strict while effective freedom is indifferent.

preference-only:
  a preference distinguishes two tokens;
  the structural grammar treats them as equivalent;
  effective freedom is strict while coverage is indifferent.
```

The orders agree only after an explicit bridge between the admitted attribute
grammar and admitted preference family.

Foster's order keeps its original quantifier reading:

```text
for every possible preference, there exists a suitable option.
```

It is not used as proof that one realization simultaneously supports several
valuers.

### Excisive paperclipper

The same attribute grammar is used for both outcomes.

```text
cooperative:
  controller_persistence;
  paperclip_production;
  independent_peer_continuation;
  independent_correction.

excisive:
  controller_persistence;
  paperclip_production.
```

The local paperclip score ranks excision higher. The structural profile order
ranks the cooperative realization strictly higher.

This establishes a finite disagreement:

```text
local objective gain and global structural contraction can coexist.
```

It does not establish that the paperclipper must care about the structural
order or that its action is morally forbidden.

## Negative Controls

All controls passed:

```text
identifier relabeling preserves the profile;
unrealizable families receive no profile;
two incomparable profiles can reverse under different scalar weights while
  remaining incomparable in the primary order;
marginal attribute coverage is submodular;
joint-augmented coverage is not submodular in the complementarity fixture.
```

The last result is load-bearing. Nehring-Puppe-style marginal coverage has
diminishing returns. A joint attribute requiring several trajectories can have
increasing returns. A full lushness object containing genuine joint emergence
therefore cannot be assumed to be one submodular diversity function.

## What Landed

The pilot retains a candidate finite instrument:

```text
joint realizability
+ idempotent marginal attribute coverage
+ explicit joint attributes
+ profile inclusion
+ structural relabeling invariance
```

It also retains a three-way separation:

```text
structural lushness profile:
  what continuation structure is realized.

effective freedom:
  what option sets preserve across possible preferences.

compatibility complex:
  which trajectory families admit one joint realization.
```

## Remaining Debt

The attribute family is exogenous.

The pilot does not derive:

```text
which continuation distinctions deserve attributes;
which attributes identify valuers;
which attributes possess standing;
which preference family is admissible;
why a local controller must accept the structural order;
how profiles transport across physical scale and certified presentation;
how to compare incomparable profiles.
```

The next theory move should derive or certify a minimal attribute grammar from
Alpha's oriented dynamics. Adding another scalar diversity measure would not
pay this debt.

## Public Compression

A finite pilot retained a duplicate-resistant partial order over continuation
attributes realized by compatible trajectory families. It distinguishes
non-fungible extension from duplicate counting and keeps structural coverage,
uncertain-preference freedom, and joint realization separate. The result is a
candidate lushness instrument, not a derivation of value or alignment.
