# Alpha / Agency Underdetermination v0

Status: theorem note / effective-layer boundary witness
Scope: Alpha trace, higher-layer agency-realization profile, nonfactorization
Claim boundary: not an agency definition, not value, not valuerhood, not identity, not Omega validation

## Purpose

This note records the finite witness added in:

```text
formal/lean/OmegaProper/EffectiveLayers/Underdetermination.lean
```

The core lesson is:

```text
Alpha-facing traces do not canonically determine higher-layer agency
realizations.
```

This formalizes the reorientation from:

```text
Alpha directly derives agency.
```

to:

```text
agency is a higher effective-layer realization that should forget down to
Alpha-compatible traces, but is not reconstructed from those traces alone.
```

## The Witness

The Lean module defines a minimal two-point Alpha trace:

```text
Point := left | right

AlphaTrace :=
  rel  : Point -> Point -> Prop
  sep  : Point -> Point -> Prop
  asym : Point -> Point -> Prop
```

Both toy realizations share the same Alpha trace:

```text
passiveRealization.alpha  = sharedAlphaTrace
feedbackRealization.alpha = sharedAlphaTrace
```

They differ only in higher-layer realization fields:

```text
passive:
  hasEndogenousAlternatives = false
  feedbackMaintainsSelector = false

feedback:
  hasEndogenousAlternatives = true
  feedbackMaintainsSelector = true
```

The toy agency profile is:

```text
agencyProfile(R)
  = R.hasEndogenousAlternatives && R.feedbackMaintainsSelector
```

This is not a full agency definition. It is a deliberately small profile bit
used to show non-determination.

## Theorem Shape

The proof is an instance of the standard nonfactorization schema:

```text
same summary,
different target,
therefore target does not factor through summary.
```

Here:

```text
summary = forgetAlpha
target  = agencyProfile
```

The checked theorem is:

```text
alphaTrace_does_not_determine_agencyProfile :
  NonFactorization forgetAlpha agencyProfile
```

and therefore:

```text
alphaTrace_blocks_agencyProfile_factorization :
  Not (FactorsThrough forgetAlpha agencyProfile)
```

## Interpretation

The theorem does not say Alpha is irrelevant.

It says:

```text
higher-layer agency facts may forget down to Alpha traces, but Alpha traces
alone do not choose the higher-layer realization.
```

This blocks a common category mistake:

```text
relation + distinction + asymmetry
  therefore agency.
```

The correct future theorem direction is two-sided:

```text
agentic power -> lower consequence-bearing Alpha trace
Alpha trace -/-> agentic power.
```

This note lands the second half. The downward necessity theorem remains future
work.

## Why The Witness Is Toy-Level

The witness is intentionally small. Its job is not to model agency. Its job is
to establish that the effective-layer tower needs realization data above Alpha.

Richer agency work should add:

```text
controlled alternatives;
feedback;
live-versus-replay advantage;
maintenance of the observation-selection-action channel;
presentation robustness;
joint-continuation effects.
```

Those belong in the agency-realization layer, not in bare Alpha.

## Non-Claims

This theorem does not claim:

```text
agency has been defined;
agency has been detected;
the feedback toy is a real agent;
Alpha has no role in agency;
value or valuerhood follows;
identity or selfhood follows;
Omega has been validated.
```

It claims only:

```text
the lower Alpha trace is not sufficient to determine the higher agency-profile
realization.
```

## Next Bridge

The companion theorem should be a downward necessity theorem:

```text
minimal agentic-power witness
  -> selection changes future continuation
  -> consequence-bearing separation
  -> Alpha-compatible relation/distinction/asymmetry trace.
```

Together, the pair would establish:

```text
agency -> Alpha trace
Alpha trace -/-> agency.
```

