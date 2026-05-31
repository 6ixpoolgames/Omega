# Spec Formatting Guidelines

Status: permanent manual guideline  
Scope: all future Omega specs and run specs  
Purpose: keep specs compact, intention-preserving, and easy for human/Codex readers to execute without duplicating permanent project doctrine.

## 0. One-sentence rule

A spec should transmit the run's intention, constraints, and decision logic with the smallest amount of text that still prevents ambiguity.

In compact form:

```text
Say what is new.
Reference what is permanent.
Preregister what would change our mind.
Do not restate the whole project manual.
```

## 1. Intended reader

Write specs for two readers at once:

```text
human research lead:
  can check whether the experiment expresses the intended theory question;

implementation agent:
  can implement or run the spec without inventing missing degrees of freedom.
```

Do not write specs as public-facing papers, theory essays, or result notes.

A spec is an execution contract. It may contain motivation, but only enough motivation to constrain implementation and interpretation.

## 2. Required top matter

Every spec should begin with:

```text
# <Spec Title>

Status: <draft | active | implemented | superseded>
Builds on: <1-4 most relevant docs/results>
Scope: <branch and run family>
Claim boundary: <short pointer or compact one-line boundary>
```

Keep `Builds on` short. Prefer the latest result note, the active theory note, and the relevant runner/spec contract. Do not include the entire historical path unless the run explicitly revisits history.

## 3. Standard section skeleton

Use this skeleton by default. Remove sections that are genuinely irrelevant; do not add sections unless they change implementation or interpretation.

```text
## 0. One-sentence purpose
## 1. Why this spec exists
## 2. Inherited rules and claim boundary
## 3. Objects under test
## 4. Required run shape
## 5. Controls, nulls, and audits
## 6. Required outputs
## 7. Decision rules
## 8. Next-action forks
## 9. Non-goals
## 10. 3P check
```

For very small smoke/repair specs, use the compact form:

```text
## Purpose
## Change required
## Minimal verification
## Expected outputs
## Decision rule
## Non-goals
```

## 4. What belongs in a spec

Include only information that affects one of these:

```text
implementation:
  what code path, parameters, artifacts, or checks must exist;

interpretation:
  what a result may or may not mean;

decision:
  what outcome changes the next action;

reproducibility:
  what run shape, inputs, and retained outputs are required.
```

If a paragraph does not affect implementation, interpretation, decision, or reproducibility, move it to a theory note, result note, or omit it.

## 5. Permanent material should be referenced, not repeated

The following are recurrent project rules. In ordinary specs, reference them briefly rather than restating them in full:

```text
claim boundary:
  no Omega detection, agency detection, identity detection, valuer detection,
  value detection, holdout readiness, candidate promotion, or graph-channel
  causality unless a later spec explicitly opens that gate;

3P discipline:
  principled, parsimonious, predictive;

control philosophy:
  detector nulls test the instrument;
  perturbations map response profiles;
  destructive ablation maps viability boundaries;

response taxonomy:
  stable, amplified-aligned, weakened, rerouted, reopened, collapsed,
  control-equivalent, and measurement-limit classes retain their runner-defined
  meanings;

artifact policy:
  large raw outputs remain under results/local_runs unless a compact public
  artifact is deliberately promoted;

fixture discipline:
  fixture contracts must pass before empirical response classes are interpreted;

graceful-run discipline:
  long runs must emit status, config, progress, errors, manifests, and enough
  CSV/JSON artifacts to diagnose partial runs.
```

Use a compact line such as:

```text
Inherited rules: standard Omega claim boundary, matched-null/perturbation separation, response taxonomy, artifact policy, fixture discipline, and graceful-run discipline apply.
```

Only restate a permanent rule when this spec changes, narrows, or tests it.

## 6. Claim-boundary formatting

Prefer one compact claim-boundary block.

Good:

```text
Claim boundary: substrate characterization only; no Omega, agency, value,
identity, valuerhood, holdout, candidate-promotion, or graph-causality claim.
```

Avoid long repeated forbidden-claim lists unless the spec is public-facing or likely to be quoted outside context.

If a spec opens a normally blocked gate, it must say so explicitly and explain why.

## 7. Parameter formatting

Put parameter grids in compact `text` blocks or small tables.

Good:

```text
macro_invariant_kind:
  symbol_histogram_distance
  hamming_weight_or_nonzero_count

equivalent_beta_target:
  0.04
  0.05
  0.075
  0.10
  0.15
```

Avoid prose lists such as "we should probably test beta values..." in implementation sections. Spec values should be auditable.

When using old implementation names for renamed concepts, show the public/theory name first and the raw implementation name second:

```text
macro-invariant kind (`budget_kind` in retained runner outputs):
  symbol_histogram_distance
```

## 8. Outputs should be minimal and typed

Separate outputs by function:

```text
Core run artifacts:
  run_config.json
  status.json
  progress_checkpoints.csv
  errors.csv
  output_manifest.json

Decision artifacts:
  response_by_<main_axis>.csv
  threshold_table.csv
  matched_null_summary.csv

Audit artifacts:
  selected_edge_overlap_by_beta.csv
  paired_baseline_availability.csv
```

Do not list every inherited runner output unless the spec changes the output contract. Instead say:

```text
All standard horizon-transport runner outputs remain required.
Additional retained outputs:
  ...
```

## 9. Decision rules are mandatory

Every nontrivial spec must define what outcomes mean before the run.

Use this format:

```text
Promote / continue if:
  <condition>

Demote / narrow if:
  <condition>

Repair before interpreting if:
  <condition>

Pause if:
  <condition>
```

Decision rules should mention both signal and interpretability. Do not rank a substrate by a positive response class alone if coverage, paired baselines, matched nulls, or fixture gates are weak.

## 10. Non-goals prevent scope creep

Every spec should include a short non-goals section.

Good:

```text
This spec does not:
  open holdout scoring;
  test graph-channel causality;
  introduce agent/value/Omega labels;
  add new semantic probes;
  promote a candidate.
```

Non-goals should be short. Do not repeat the whole claim-boundary section.

## 11. 3P check should be concrete

End with a 3P check that names the specific object of the spec.

Good:

```text
Principled:
  tests whether macro-invariant preservation survives when moved from an
  explicit energy term to an ensemble-level constraint.

Parsimonious:
  keeps locality, out-degree, reversibility, and one macro-invariant marginal;
  removes hand-built symbolic law templates.

Predictive:
  ME0 amplification demotes preservation; MEP-only amplification strengthens
  preservation as a substrate-level ingredient; deterministic-only amplification
  identifies top-m energy geometry as loadbearing.
```

Avoid generic 3P statements that could appear unchanged in any spec.

## 12. Token and context-window discipline

Specs should be optimized for repeated loading by human and AI collaborators.

Guidelines:

```text
target length:
  ordinary run spec: 150-300 lines;
  smoke/repair spec: 50-120 lines;
  major program spec: 300-500 lines only when it replaces several smaller specs;

prefer:
  dense text blocks, small tables, explicit decision rules;

avoid:
  copied history, repeated permanent doctrine, full result tables from prior notes,
  motivational essays, and duplicate output lists.
```

If a spec needs more than ~500 lines, split it into:

```text
theory note:
  why the object matters;

spec:
  what to run and how to judge it;

result note:
  what happened.
```

## 13. Relationship between specs and result notes

Do not write future result interpretation into the spec as if known.

Specs should say:

```text
If X happens, interpret as Y and do Z next.
```

Result notes should say:

```text
X happened; therefore we choose Y/Z under the preregistered decision rule.
```

Do not copy large result tables into later specs. Summarize the calibration target and cite/link the retained result note.

## 14. Relationship between specs and theory notes

Use theory notes for conceptual development. Use specs for executable commitments.

A theory note may ask:

```text
Could preservation of coarse distinctions be a substrate-level precursor to
future-structure coherence?
```

A spec should ask:

```text
Does a max-entropy local transition ensemble matched on the symbol-histogram
`delta_I` edge marginal reproduce the beta-threshold aligned response?
```

## 15. Recommended spec template

```text
# <Run/Repair/Preflight Name>

Status: draft
Builds on:
- <latest result note>
- <relevant theory note>
- <runner/spec contract>
Scope: <branch>
Claim boundary: <one compact boundary sentence>

## 0. One-sentence purpose
<One sentence.>

## 1. Why this spec exists
<One short paragraph.>

## 2. Inherited rules
Standard Omega claim boundary, 3P discipline, matched-null/perturbation
separation, response taxonomy, fixture discipline, artifact policy, and
graceful-run discipline apply.

Only spec-specific deviations:
- <none, or explicit deviations>

## 3. Objects under test
<Substrate/probe/control definitions.>

## 4. Required run shape
<Compact parameter grid and run settings.>

## 5. Controls, nulls, and audits
<Only the controls/audits that matter for this spec.>

## 6. Required outputs
All standard <runner> outputs remain required.
Additional retained outputs:
- <output>

## 7. Decision rules
Promote / continue if:
- <condition>

Demote / narrow if:
- <condition>

Repair before interpreting if:
- <condition>

Pause if:
- <condition>

## 8. Next-action forks
Emit exactly one:
- <fork>
- <fork>

## 9. Non-goals
This spec does not:
- <non-goal>

## 10. 3P check
Principled:
  <specific statement>

Parsimonious:
  <specific statement>

Predictive:
  <specific statement>
```

## 16. Practical review checklist

Before committing a spec, check:

```text
Can the run be implemented without guessing hidden parameters?
Does every included section affect implementation, interpretation, decision, or reproducibility?
Are permanent project rules referenced instead of repeated?
Are claim boundaries compact but present?
Are decision rules explicit enough to prevent post-hoc interpretation drift?
Are non-goals clear enough to block scope creep?
Could this spec be loaded into a small context window without crowding out the runner/result note?
```

If any answer is no, streamline before committing.
