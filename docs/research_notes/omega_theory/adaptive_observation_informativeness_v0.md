# Adaptive Observation Informativeness v0

Status: Lean theorem checkpoint / B2.1 epistemic weld
Scope: deterministic observation factorization for finite adaptive fixed-world
possibilistic corridors
Claim boundary: not stochastic observation, not POMDP theory, not sensor
validity, not value, not agency, not valuerhood, not moral standing, not Omega
validation

## Purpose

B2.1 showed that unknown-but-fixed ambiguity can sometimes be converted into
information by sound update. This note records the first formal bridge between
that adaptive corridor and Blackwell-shaped observation comparison:

```text
If a coarser deterministic observation factors through a finer deterministic
observation, then any coarser-observation adaptive corridor certificate
transports to a nonempty finer information state that refines it.
```

Informally:

```text
certified better observations do not shrink the adaptive corridor.
```

## Lean Surface

The theorem lives in:

```text
formal/lean/OmegaProper/Decision/AdaptiveObservation.lean
```

It adds an observation-parametric adaptive lift:

```text
observedUpdate:
  keeps possible models whose concrete successor has the observed output.

ObservedLiftedStep:
  lifted information-state step using a deterministic observation interface.

ObservedAdaptiveKernel:
  robust corridor of the observed lifted system.

InfoRefines:
  a finer information state has the same concrete state, is nonempty, and has
  a possible-model set contained in the coarser information state's possible
  set.
```

The main theorem is:

```text
observedAdaptiveKernel_mono_of_factorization
```

Given a deterministic factorization:

```text
Coarse.observe s = h.map (Fine.observe s)
```

and an information-state refinement:

```text
FineInfo.state = CoarseInfo.state
FineInfo.possible subset CoarseInfo.possible
FineInfo.possible is nonempty
```

the theorem proves:

```text
CoarseInfo in ObservedAdaptiveKernel(Coarse)
  ->
FineInfo in ObservedAdaptiveKernel(Fine).
```

## Reading

The theorem is the corridor analogue of deterministic Blackwell
informativeness. A coarser observer can be simulated by a finer observer: every
coarse observation is recoverable from the fine observation. In the adaptive
kernel, that means the finer observer can reproduce the coarser update while
possibly retaining strictly sharper model information.

This is not a claim that every sensor is valid. The factorization and update
contracts are assumptions. The fake-update phantom corridor witness in B2.1
shows why this matters: fabricated model elimination can make a false
information state look safe by deleting the world that would refute the action.

## What It Connects

This is the first direct weld between:

```text
ODT1 / Blackwell-shaped comparison:
  deterministic factorization as observation informativeness.

B2.1 adaptive corridors:
  information-state robust viability under unknown-but-fixed ambiguity.
```

The resulting slogan is precise only under the theorem hypotheses:

```text
More informative certified observation weakly widens the adaptive corridor.
```

## Nonclaims

This note does not claim:

```text
stochastic observation monotonicity;
POMDP theory;
empirical validity of an observation interface;
that more data is always useful under arbitrary update rules;
that fabricated model elimination is sound;
value;
agency;
identity;
valuerhood;
moral standing;
Omega validation.
```

## Public Compression

Certified better observation cannot make an adaptive fixed-world corridor
smaller. If a coarse observation factors through a finer one, any coarse-safe
information state has a corresponding fine-safe refinement.
