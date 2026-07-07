# Static Compensation Certificate Staleness Report v0

Status: retained Lean theorem / Omega close checkpoint
Scope: fixed-domain coverage staleness for time-indexed declared registers
Claim boundary: not rights, not no-replacement theorem, not cross-valuer
compensation, not value, not standing, not patienthood, not agency, not Omega
validation

## Purpose

This report closes the preregistered staleness protocol in the narrow coverage
sense.

## Formal File

```text
formal/lean/OmegaProper/Decision/CertificateStaleness.lean
```

## Retained Theorems

```text
static_certificate_stale
exists_time_not_covers_of_fact_outside_domain
```

## Reading

A static certificate has a fixed domain of facts. If a soundly growing register
later contains a fact outside that fixed domain, the certificate no longer
covers the later register.

This is coverage language only:

```text
fixed domain;
new fact outside domain;
therefore stale.
```

## What This Pays

The result closes the protocol-to-proof loop for same-frame NOLP staleness in
Omega before migration. It does not authorize broader replacement, rights, or
cross-valuer compensation claims.

## Validation

```text
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper.Decision
```

## Public Compression

A static certificate can cover only the facts in its fixed domain. If the
register soundly grows beyond that domain, the certificate is stale until
extended by a certified route.
