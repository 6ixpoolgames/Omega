# Carrier Trajectory Language v0

Status: path-language repair
Scope: trajectory-language reading of carrier certificates
Claim boundary: not identity, not agency, not value, not deformer theory, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/CarrierTrajectoryLanguage.lean
```

The repair is conceptual but formal:

```text
do not treat carrier predicates as object-like supports when path language is
the relevant fact.
```

A carrier candidate induces a path language:

```text
which endpoint pairs are internally connected through the candidate carrier?
```

Recurrent carrying can then be read as recurrence plus round-trip language
membership plus merge separation.

## Main Lean shape

```text
CarrierPathLanguage Next C x y :=
  InternalPath (dynFromNext Next) C x y

CarrierRoundTripLanguage Next C x y :=
  CarrierPathLanguage Next C x y
  and CarrierPathLanguage Next C y x
```

Main theorem names:

```text
certificate_roundTripLanguage
certificate_forwardLanguage
certificate_reverseLanguage
certificate_of_roundTripLanguage
cycle_roundTripLanguage
```

## Why this matters

This is the first small bridge from support predicates to trajectory language.

The current support stack remains valid, but future work can increasingly talk
about languages of admissible paths rather than object-like regions.

## Related notes

- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [generated_carrier_v0.md](generated_carrier_v0.md)
- [simulation_transfer_v0.md](simulation_transfer_v0.md)
- [viable_trajectory_language_v0.md](viable_trajectory_language_v0.md)
