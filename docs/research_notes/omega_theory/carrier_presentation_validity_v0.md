# Carrier Presentation Validity v0

Status: sound-presentation bridge
Scope: certified carrier endpoints under sound presentations
Claim boundary: not boundary realism, not identity, not agency, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/CarrierPresentationValidity.lean
```

The repair target is presentation validity for carrier claims.

If a carrier certificate says a pair `x/y` is merge-separated and recurrently
carried, then a sound presentation cannot erase that pair. A presentation that
does erase the certified endpoints is not sound.

## Main Lean shape

```text
PairVisibleUnderPresentation present x y
certificate_pair_invariant_under_soundQuotients
soundPresentation_keeps_certified_pair_visible
erases_certified_pair_not_sound
reachabilitySafePresentation_keeps_certified_pair_visible
viabilitySafePresentation_keeps_certified_pair_visible
```

## Why this matters

This connects the carrier-certificate repair back to the sound quotient and
safe presentation stack:

```text
candidate carrier + certificate
  -> merge-separated endpoints
  -> presentation-invariant under sound quotients
  -> erased certified pair means unsound presentation
```

It does not claim the presentation preserves an object or boundary. It only
says certified consequence-bearing endpoints cannot be soundly collapsed.

## Related notes

- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [safe_presentation_contract_v0.md](safe_presentation_contract_v0.md)
- [boundary_invariant_continuation_roadmap_v0.md](boundary_invariant_continuation_roadmap_v0.md)
- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)
