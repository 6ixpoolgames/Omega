# RFS-MB0 Boundary Recurrence Measurement Limits

Date: 2026-05-27

## Summary

The current RFS-MB0 boundary workflow finds local/pre-control and fresh-seed
recurrent boundary structure, but the focused pass did not produce clean
recurrent boundary candidates.

Update after detector instrumentation repair:

```text
The measurement limit remains, but the diagnosis is sharper.
The old generic probe-limited label decomposes mostly into collision-limited
recurrence, with a smaller weak-control-bundle class.
```

The decisive result is:

```text
20 / 20 selected groups were evidence-probe recurrent
20 / 20 were non-saturation recurrent by the row-level saturation flag
0 / 20 were clean recurrent boundary candidates
20 / 20 were classified as evidence_probe_recurrent_but_probe_limited
```

Corrected rerun:

```text
independent_axis_recurrent_but_collision_limited: 16 / 20
weak_control_bundle_recurrence: 4 / 20
clean recurrent boundary candidates: 0 / 20
```

## Measurement Limit

The current probe/detector stack can detect recurrence in selected boundary
groups, but the recurrence remains probe-limited. That means the system is not
yet demonstrating robust cross-probe support/distribution deformation in a form
strong enough for stable-band promotion.

This is not a theory validation result. It is a measurement boundary:

```text
the branch can produce recurrent boundary behavior
but the present evidence probes cannot separate clean deformation from
probe-resolution limitations
```

## Consequence

Do not run n=6 from this state.

Do not use broader breadth as the next move.

The next useful work is probe repair:

```text
1. reduce collision in the evidence probe panel
2. introduce stricter but non-identity-like evidence probes
3. strengthen focused matched-control bundles
4. rerun a small focused pass only after collision is reduced
```

If probe-limited recurrence persists after probe repair, MB0 should be paused
or reframed as a measurement-limits branch rather than scaled further.

## Claim Boundary

This note does not claim Omega, agency, value, identity, viability,
path-process detection, stable candidate bands, n=6 transfer, or
scientific-gate passage.
