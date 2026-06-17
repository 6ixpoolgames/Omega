# Carrier Certificate v0

Status: support-validity repair
Scope: recurrently carried consequence distinctions
Claim boundary: not identity, not objecthood, not agency, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/CarrierCertificate.lean
```

The repair is simple:

```text
support is a candidate;
certificate is what gives it standing.
```

A declared support predicate `C` is not treated as a real object, boundary, or
self. It is only a carrier candidate. It becomes valid for a declared pair
`x/y` when it is certified by the existing recurrent-carrying package.

## Main Lean shape

```text
CarrierCandidate X := X -> Prop

CarrierCertificate S Next safe C x y :=
  RecurrentSupportCarries S Next safe C x y
```

The name changes the claim hygiene without breaking the old stack.

## What a certificate gives

A certificate implies:

```text
C contains x and y;
C is recurrent viable;
x reaches y internally inside C;
y reaches x internally inside C;
x/y are merge-separated by consequence;
x and y are viable under safe.
```

Main theorem names:

```text
certificate_recurrent
certificate_contains_left
certificate_contains_right
certificate_forward_path
certificate_reverse_path
certificate_mergeSeparated
certificate_left_viable
certificate_right_viable
missing_left_blocks_certificate
missing_right_blocks_certificate
missing_forward_path_blocks_certificate
missing_reverse_path_blocks_certificate
```

## Why this matters

This prevents a subtle slide:

```text
declared support -> valid support -> object-like thing
```

The correct reading is:

```text
declared support -> candidate carrier
certified support -> pair-relative carrier certificate
```

The certificate is still not identity, agency, or objecthood.

## Related notes

- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)
- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)
- [generated_carrier_v0.md](generated_carrier_v0.md)
