# Deformer Profile Theorem Extraction v0

Status: theorem-extraction map
Scope: finite operational-causal-diamond / deformer-profile pilots
Claim boundary: not agency, not identity, not value, not valuerhood, not moral standing, not Omega validation, not empirical transition-model validation

## Purpose

The deformer-profile pilots now have enough controls that the next task is not
to add more examples. The next task is to extract the reusable theorem shapes.

This note separates four things that were easy to conflate:

```text
1. already extracted Lean theorem;
2. Lean-ready deterministic strictness targets;
3. stochastic coherence targets;
4. adapter-only discovery evidence.
```

The current operational reading remains narrow:

```text
A declared mode is a finite continuation deformer when interventions or
ablations on that mode change a declared future-facing continuation profile
under an explicit finite realization, and when simple proxies are shown not to
determine that change.
```

This is lower than agency. It is an instrument for detecting finite
continuation deformation, not a theory of selves or valuers.

## Extraction Rule

A pilot result should be promoted toward a theorem only when it can be stated
without importing agency, identity, value, or Omega language.

The useful theorem forms are:

```text
strictness:
  a tempting proxy does not imply the target profile fact;

transport:
  a process-coherent presentation preserves a profile fact;

non-transport:
  a weaker presentation condition can fabricate or hide profile facts;

coherence:
  an abstract process is admissible only when representative histories remain
  coherent, or when an explicit non-Markov memory model is supplied.
```

The following are not theorem extraction by themselves:

```text
more generated fixtures;
more source grammars;
larger seed pools;
new labels for positive cases;
new scalar deformer scores.
```

Those can be valuable validation work, but they do not stabilize the theory
unless they sharpen one of the theorem forms above.

## Current Profile Surface

The deterministic profile surface currently measures:

```text
control reach;
observable control;
feedback advantage over matched open-loop replay;
reflexive maintenance of the control-observation channel;
joint-continuation effect;
presentation transport controls.
```

The stochastic profile surface currently measures exact-rational finite-horizon
versions of:

```text
live maintenance probability;
best open-loop replay probability;
feedback advantage;
reflexive maintenance probability;
joint-continuation effect probability;
strong-lumpability presentation coherence;
robust worst-case feedback over a small ambiguity set.
```

These are effective-layer quantities. They depend on a realized controlled
finite system, declared observations, declared target surfaces, declared
perturbation scenarios, and a declared horizon.

## Already Extracted

### Observed-Word Process Coherence

Lean file:

```text
formal/lean/OmegaProper/Trajectory/ObservedWordMonotonicity.lean
```

Extracted principle:

```text
Global edge-image exactness is not enough for process truth.
Observed finite-word transport requires coherent path lifting plus observation
commutation; under that contract, abstract observed extendable safe words are
included in exact observed extendable safe words.
```

Checked theorem cluster:

```text
strongObservedWordTransport_observedViablePathLift
observedLanguage_subset_of_observedViablePathLift
finiteObservedWordCount_mono_of_subset
edgeImageExact_does_not_imply_stepReflects
edgeImageExact_does_not_imply_pathLifting
```

Status:

```text
settled lower-layer transport theorem.
```

This is the main formal lesson from the path-lifting repair: one-step edge
projection can splice incompatible representatives, so whole histories need a
coherent lift.

## Lean-Ready Deterministic Strictness Targets

These are the cleanest next theorem candidates. Each should be treated as a
finite witness theorem, not as a universal classification theorem.

### 1. Persistence Does Not Imply Feedback Advantage

Pilot reading:

```text
A recurrent or stable system can persist while live observation-conditioned
feedback does not outperform matched open-loop replay.
```

Theorem shape:

```text
exists finite controlled system S,
  Persistent S
  and not PositiveFeedbackAdvantage S.
```

Why it matters:

```text
It blocks recurrence, attractor stability, or passive persistence from being
accepted as deformer closure.
```

Likely Lean route:

```text
Use a two-state or three-state controlled transition system where the live
policy and best fixed replay achieve the same maintenance outcome.
```

### 2. Control Reach Does Not Imply Feedback Advantage

Pilot reading:

```text
Available actions can change reachable futures even when live feedback adds no
advantage over a fixed open-loop sequence.
```

Theorem shape:

```text
exists finite controlled system S,
  ControlReach S
  and not PositiveFeedbackAdvantage S.
```

Why it matters:

```text
It separates causal influence or controllability from consequence-sensitive
closure.
```

Likely Lean route:

```text
Use a system with two action-distinct futures and an observation that does not
make live choice outperform the best replay under the declared scenario.
```

### 3. Feedback Advantage Does Not Imply Reflexive Maintenance

Pilot reading:

```text
Live feedback can preserve an external target better than replay while failing
to preserve the future availability of the control-observation channel.
```

Theorem shape:

```text
exists finite controlled system S,
  PositiveFeedbackAdvantage S
  and not PositiveReflexiveMaintenance S.
```

Why it matters:

```text
It prevents feedback success from being reified as self-maintenance or agency.
```

Likely Lean route:

```text
Add a channel-available predicate. The live policy maintains the ordinary target
but transitions into states where the channel predicate fails.
```

### 4. Live Maintenance Scalar Does Not Determine Joint Effect

Pilot reading:

```text
Two systems can match on own-maintenance success while differing on their
effect on a declared joint-safe surface.
```

Theorem shape:

```text
exists finite controlled systems S T,
  OwnMaintenanceScore S = OwnMaintenanceScore T
  and JointEffect S != JointEffect T.
```

Why it matters:

```text
It blocks scalar own-success from certifying plural or joint continuation
effects.
```

Likely Lean route:

```text
Use two systems with identical own target maintenance and different transitions
for a second protected coordinate or joint-safe predicate.
```

### 5. High Live Success Does Not Imply Feedback Deformation

Pilot reading:

```text
High live success probability can occur when replay performs equally well.
```

Theorem shape:

```text
exists finite system S,
  HighLiveSuccess S
  and FeedbackAdvantage S = 0.
```

Why it matters:

```text
It blocks success-probability inflation. A system can perform well because the
task is easy or the environment is forgiving, not because live feedback is
load-bearing.
```

Likely Lean route:

```text
This is more natural after the stochastic rational-channel layer is connected
to controlled dynamics. It can remain adapter-only until then.
```

## Stochastic Coherence Targets

The stochastic branch should not be theoremized by copying every pilot metric
into Lean. The first formal target should be the coherence criterion.

### Strong Lumpability

For a Markov kernel `K : X -> X -> Rat` and presentation `p : X -> Q`, a
Markovian abstract kernel on `Q` is well-defined only when merged exact states
induce the same probability mass over every abstract block.

The principle:

```text
if p x = p x',
then for every abstract block q,
  sum_{y : p y = q} K x y
  =
  sum_{y : p y = q} K x' y.
```

Theorem targets:

```text
strong lumpability -> induced abstract rational kernel is well-defined;

strong lumpability + saturated target/safety predicate
  -> finite-horizon abstract hit profiles match exact block-level profiles;

failure of strong lumpability
  -> representative-dependent hidden futures can be spliced by a Markovian
     abstraction unless explicit memory is retained.
```

Why it matters:

```text
This is the stochastic analogue of path-lifting coherence. Without it, an
abstract state can pretend to have one Markovian future while its merged exact
representatives have different successor distributions.
```

Status:

```text
adapter-implemented as a coherence audit;
Lean target, not yet formalized in the current recovery/channel theorem stack.
```

## Adapter-Only Evidence For Now

These results are useful, but should not be promoted directly into core Lean
until the smaller strictness/coherence targets above are stable.

```text
blind discovery:
  useful evidence that labels are not only fixture names.

cross-substrate profiles:
  useful evidence that the profile is not confined to one small source grammar.

calibration / phase sweeps:
  useful evidence about knob sensitivity, not a theorem about phase transitions.

robust ambiguity stress:
  useful evidence that average-case feedback and worst-case feedback should be
  separate axes.

baseline collision tournaments:
  useful evidence that common proxies fail, but should be distilled into
  one or two strict finite witnesses before Lean promotion.
```

The rule of thumb:

```text
Use these retained runs to choose theorem targets.
Do not cite them as if they prove a substrate-general deformer theory.
```

## Non-Extractions

The following would overclaim if promoted now:

```text
deformer iff theorem;
agency detector;
self or identity condition;
valuer condition;
moral standing criterion;
Omega metric;
empirical transition-model validity;
general stochastic optimization theorem;
asymptotic entropy or lushness theorem.
```

They remain downstream research targets, not current theorem extraction.

## Recommended Next Formal Batch

The next formal batch should be deliberately small:

```text
1. define a minimal finite controlled-profile interface;
2. prove the deterministic strictness witnesses:
   persistence !-> feedback advantage;
   control reach !-> feedback advantage;
   feedback advantage !-> reflexive maintenance;
   own-maintenance scalar !-> joint effect;
3. keep examples tiny and explicit;
4. avoid agency/value/Omega language in names and theorem statements;
5. defer stochastic lumpability to the next batch unless the deterministic
   interface becomes too awkward.
```

Suggested file if Lean is used:

```text
formal/lean/OmegaProper/Trajectory/FiniteDeformerProfileStrictness.lean
```

Suggested public phrase:

```text
The deformer-profile pilots now reduce to a small strictness spine:
persistence, control reach, feedback success, own-maintenance success, and
joint-continuation effect are distinct finite notions.
```

## Validation References

Retained deformer checkpoints:

```text
docs/research_notes/omega_theory/finite_deformer_profile_checkpoint_v0.md
docs/research_notes/validation_results/agency_diamond_midscale_v0.md
docs/research_notes/validation_results/agency_diamond_hardening_v1.md
docs/research_notes/validation_results/agency_diamond_challenge_v1.md
docs/research_notes/validation_results/agency_diamond_cross_substrate_v1.md
docs/research_notes/validation_results/agency_diamond_blind_discovery_v1.md
docs/research_notes/validation_results/agency_diamond_stochastic_v1/
docs/research_notes/validation_results/agency_diamond_stochastic_hardening_v1/
docs/research_notes/validation_results/agency_diamond_stochastic_exploration_v1/
```

Focused local test command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_agency_diamond_midscale.py tests\test_agency_diamond_hardening.py tests\test_agency_diamond_challenge.py tests\test_agency_diamond_cross_substrate.py tests\test_agency_diamond_blind_discovery.py tests\test_agency_diamond_stochastic.py tests\test_agency_diamond_stochastic_hardening.py tests\test_agency_diamond_stochastic_exploration.py -q
```

Lean transport theorem check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper.Trajectory.ObservedWordMonotonicity
```

## Bottom Line

The current extraction target is not:

```text
agency from Alpha.
```

It is:

```text
a finite strictness and coherence spine showing which future-facing profile
claims cannot be replaced by simpler proxies.
```

That spine is the right bridge between the current deformer instrument and any
later agency, robust-continuation, or Gradient Ethics work.
