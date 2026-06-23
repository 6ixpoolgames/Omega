# Adapter Provenance v0

Status: audit-response doctrine
Scope: how declared exact structures earn credibility before abstraction contracts are trusted
Claim boundary: not empirical validation; not substrate-general transfer; not Omega validation

## Purpose

The formal stack proves many statements of this form:

```text
if exact facts are declared,
and an abstraction is sound for those exact facts,
then the abstraction does not lie about those exact facts.
```

That is useful, but it leaves a harder question:

```text
why trust the declared exact facts?
```

This note names that missing bridge: adapter provenance.

## Three Layers

### 1. Exact formal layer

The Lean layer works with declared structures:

```text
fragments;
contexts;
outcomes;
comparison;
transition relation;
safety predicate;
target predicate;
support / carrier candidate;
presentation map;
summary map.
```

Within that declared world, theorems can prove:

```text
this quotient is sound;
this presentation reflects reachability;
this summary does not determine this target;
this carrier candidate has a recurrent carrying certificate.
```

### 2. Abstraction contract layer

The abstraction layer relates coarse claims to exact claims:

```text
sound:
  abstract claim -> exact claim

complete:
  exact claim -> abstract claim
```

This prevents the abstraction from fabricating or hiding the declared exact
facts it claims to represent.

### 3. Adapter provenance layer

The adapter layer justifies the declared exact facts:

```text
where did the fragments come from?
why are these contexts admissible?
why is this comparison the right comparison?
why is this transition relation the intended dynamics?
why is this safety or target predicate legitimate?
why is this summary the benchmark/proxy under review?
what was declared before observing the outcome?
```

This is the layer that blocks adapter-side self-validation.

## The Main Failure Mode

The risk is:

```text
choose exact facts after seeing the desired conclusion;
prove the abstraction is sound for those chosen facts;
mistake the proof for external validation.
```

That is not a theorem failure. It is a provenance failure.

## Registry-First Pattern

The registry-first stochastic channel branch already uses the right discipline:

```text
declared registry recovery:
  decoder and target are registered before evaluation.

existence recovery:
  some decoder exists.

optimized diagnostic recovery:
  a decoder succeeds after search.
```

The project should generalize this pattern:

```text
declaration before search;
exact artifact retention;
digest or manifest checks where practical;
negative controls;
mutation checks;
explicit distinction between declared, existence, and optimized claims.
```

## Adapter Provenance Checklist

For every future adapter, record:

```text
1. Substrate:
   What system is being modeled?

2. Fragment carrier:
   What counts as a fragment/state/candidate?

3. Declared target:
   What exact fact is being protected or tested?

4. Declared contexts:
   Which contexts or observations are admissible, and why?

5. Comparison relation:
   What counts as compatible, equal, separated, or refused?

6. Dynamics:
   What transition relation, action relation, or stochastic kernel is used?

7. Safety / viability:
   What predicate defines staying in the corridor?

8. Presentation / summary:
   What abstraction, metric, benchmark, quotient, or proxy is under review?

9. Declaration timing:
   Was the target/panel/summary declared before seeing the result?

10. Controls:
   What mutation, null, or adversarial case would make the claim fail?

11. Retained artifacts:
   Which files, manifests, or digests prove what was run?

12. Claim boundary:
   What does the adapter not establish?
```

A reusable template now lives at:

```text
../../templates/ADAPTER_PROVENANCE_TEMPLATE.md
```

## Why This Matters For Alignment

In an alignment setting, a presentation may be:

```text
a benchmark score;
a reward model;
a safety monitor;
a mechanistic feature;
a compressed world model;
a policy abstraction;
a declared agent boundary;
a viability corridor estimate.
```

The formal layer can test whether the presentation preserves a declared exact
target. Adapter provenance explains why that declared exact target should be
treated as the target of interest rather than an artifact of our setup.

The finite relational adapter now includes two small target-scramble gates for
this purpose.

```text
target_scramble_sensitivity:
  compares bounded recovery for a declared target against bounded recovery for
  a supplied scrambled or erased target under the same observation and declared
  decoder family. This is decoder-relative.

target_scramble_capacity_sensitivity:
  compares unrestricted deterministic exact recovery for the declared target
  and supplied scramble under the same observation. This asks whether the
  observation has different exact recovery capacity for the two targets.
```

The capacity version is stronger than the decoder-relative gate because it does
not confuse a hand-picked decoder registry with the fixed observation's exact
recovery capacity. It also treats a pure Boolean label swap as unchanged when
both targets are recoverable. Neither version proves that the target is the
right empirical or ethical target.

## Non-Claims

Adapter provenance does not prove:

```text
the exact structure is correct for every substrate;
the abstraction is safe in deployment;
the target captures value;
the policy is aligned;
Omega has been validated.
```

It only records enough provenance for reviewers to audit whether a formal
claim is being used within its declared scope.

## Related Notes

- [bad_panel_taxonomy_v0.md](bad_panel_taxonomy_v0.md)
- [finite_relational_adapter_design_v0.md](finite_relational_adapter_design_v0.md)
- [loss_aware_presentation_contract_v0.md](loss_aware_presentation_contract_v0.md)
- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [compression_guardrails_v0.md](compression_guardrails_v0.md)
- [omega_adapters_finite_channel_decoder_provenance_v0.md](omega_adapters_finite_channel_decoder_provenance_v0.md)
- [../../templates/ADAPTER_PROVENANCE_TEMPLATE.md](../../templates/ADAPTER_PROVENANCE_TEMPLATE.md)
