# Adapter Provenance Template

Use this template when adding an adapter, empirical probe, benchmark proxy, or
toy environment that claims to instantiate exact facts used by the formal
stack.

## Adapter Name

```text
Name:
Version:
Owner:
Date:
```

## Substrate

```text
What system is being modeled?
What is intentionally excluded?
```

## Fragment Carrier

```text
What counts as a fragment/state/candidate?
How is the carrier generated or selected?
```

## Declared Target

```text
What exact target fact is being protected or tested?
Was it declared before evaluation?
```

## Contexts / Observations

```text
Which contexts, probes, observations, or channels are admissible?
Why these and not others?
```

## Comparison Relation

```text
What counts as equal, compatible, allowed, blocked, separated, or refused?
What degeneracy would make the comparison vacuous or all-refusing?
```

## Dynamics / Transition Structure

```text
What transition relation, action relation, stochastic kernel, or update rule is used?
How was it derived or declared?
```

## Safety / Viability Predicate

```text
What defines staying inside the corridor?
What target loss should become visible?
```

## Summary / Presentation Under Review

```text
What abstraction, metric, benchmark, quotient, class, or proxy is being audited?
What exact fact is it supposed to preserve?
```

## Declaration Timing

```text
Which pieces were declared before seeing outcomes?
Which pieces were optimized or selected after inspection?
```

## Controls

```text
What null, mutation, adversarial case, or degenerate panel should fail?
What would show the adapter is self-validating?
```

## Artifacts

```text
Retained inputs:
Retained outputs:
Manifest or digest:
Validation command:
```

## Claim Boundary

This adapter does not prove:

```text
value;
valuerhood;
agency;
identity;
Omega validation;
substrate-general transfer;
deployment safety.
```

Add any adapter-specific non-claims here.
