# Claims Ledger

Status: public claim-hygiene ledger.

Purpose: separate checked theorems, reproduced empirical results, instrument
audits, conjectures, philosophical motivations, and historical/deprecated
claims. This file is meant to make the project easier to audit from outside the
repo.

Claim boundary:

```text
This repository does not currently validate Omega.
It does not detect value, valuers, agency, identity, life, selfhood, or
compatibility.
```

## Status Classes

```text
Lean theorem:
  checked in Lean under the assumptions in the cited file.

Empirical result:
  produced by a retained run or reproducibility smoke.

Instrument audit:
  a check that an instrument, registry, provenance chain, or output contract
  behaved as declared.

Reproducibility smoke:
  a small external reproduction path with explicit pass/fail gates.

Conjecture:
  plausible but not yet proved or empirically established.

Philosophical motivation:
  project-orienting language, not a theorem or empirical result.

Deprecated / historical:
  retained for provenance, but no longer an active claim target.
```

## Current Ledger

| Claim | Status | Evidence | Validation | Not Claimed | Next Pressure |
| --- | --- | --- | --- | --- | --- |
| Alpha asymmetry supplies primitive contact: relation, separation, and non-sameness of endpoints. | Lean theorem | `formal/lean/AlphaCore/Primitive.lean`; `formal/lean/AlphaCore/Nondegenerate.lean` (`primitiveWitness_implies_relationWitness`, `primitiveWitness_implies_distinctionWitness`, `primitiveWitness_implies_distinct_relata`) | `powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega` | Value, purpose, agency, continuation, or Omega. | Keep examples showing relation, separation, and asymmetry do not collapse into one decorative field. |
| A joint primitive witness blocks total relation collapse and total identification collapse. | Lean theorem | `formal/lean/AlphaCore/Nondegenerate.lean` (`jointWitness_blocks_relationCollapse`, `jointWitness_blocks_identificationCollapse`) | Lean build command above. | That every Alpha frame is nondegenerate; only frames with the witness satisfy the theorem. | Maintain negative examples: empty/decorative/subsingleton presentations should not get the witness for free. |
| Primitive-preserving maps preserve primitive work and cannot map nondegenerate primitive work into collapsed targets. | Lean theorem | `formal/lean/AlphaCore/PrimitiveMap.lean` (`preserves_primitiveNondegenerate`, `no_map_to_identificationCollapse`, `no_map_to_relationCollapse`, `no_map_to_asymmetryCollapse`) | Lean build command above. | Scale invariance, recoverability, or all coarse-grainings being admissible. | Add consequence-preservation/reflection maps only after their failure modes are explicit. |
| Consequence separation blocks symmetric identification. | Lean theorem | `formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean` (`ConsequenceSeparated`, `ConsequenceIdentifiable`, `mergeSeparated_blocks_identifiable`) | Lean build command above. | Identity theory, object persistence, or metaphysical sameness. | Keep directional allowance distinct from symmetric merge; add examples where one-way allowance fails as identification. |
| Chain-connected compatibility does not license endpoint identification unless transitivity is proven. | Lean theorem / guardrail example | `formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean` (`connected_chain_does_not_license_endpoint_identification`, `toy_compare_not_transitive`) | Lean build command above. | Quotienting by paths or connected components. | Use this as a standing guardrail for clustering/coarse-graining proposals. |
| Proposed classes must be pairwise consequence-compatible unless stronger transitivity has been earned. | Lean theorem / guardrail | `formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean` (`ClassRespectsConsequences`, `class_respects_no_separated_pair`, `separated_pair_blocks_class_respect`, `toy_full_class_has_separated_pair`) | Lean build command above. | That arbitrary clusters or labels define valid objects. | Add future class-family checks before accepting any empirical cluster as a quotient candidate. |
| Vacuous evaluation and universal comparison collapse the consequence apparatus. | Lean theorem | `formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean`; `formal/lean/OmegaProper/Trajectory/ConsequenceDiscipline.lean` (`collapsed_of_no_evaluated_contexts`, `collapsed_of_universal_compare`, `universal_comparison_collapses`) | Lean build command above. | That noncollapse is meaningful structure by itself. | Pair noncollapse with over-separation/pathology checks. |
| A proto-teleological seed, as currently named, is only primitive Alpha contact plus evaluated consequence merge-separation. | Lean definition + theorem bundle | `formal/lean/OmegaProper/Trajectory/AlphaConsequenceSeed.lean`; `formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean` | Lean build command above. | Purpose, goals, value, agency, identity, deformer structure, boundary, Omega-seed, or Omega-terminal. | Consider renaming in public prose to "directed consequence condition" when avoiding teleology-loaded language. |
| Proto seed implies primitive nondegeneracy, consequence noncollapse, and a witness blocking symmetric consequence identification. | Lean theorem | `formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean` (`asymmetrySeed_implies_primitiveNondegenerate`, `asymmetrySeed_implies_consequenceNoncollapsed`, `asymmetrySeed_has_witness_blocking_identification`) | Lean build command above. | That primitive nondegeneracy alone or consequence noncollapse alone is sufficient. | Keep negative guardrails from `ProtoTeleologicalSeedDiscipline.lean` visible in onboarding docs. |
| Proto seed supplies a nonempty exact merge-block profile and defeats universal-allow abstraction soundness. | Lean theorem | `formal/lean/OmegaProper/Trajectory/ProtoTeleologicalProfile.lean` (`protoSeed_hasBlockProfile`, `protoSeed_blocks_universalAllowSoundness`) | Lean build command above. | Recoverability, identity, persistence, coarse-graining, deformer structure, value, valuerhood, or Omega-terminal. | Next formal bridge should compare exact profiles to baseline abstractions without treating profiles as identity. |
| Coarse profile abstractions are not trusted unless soundness/completeness contracts are explicit. | Lean theorem / guardrail | `formal/lean/OmegaProper/Trajectory/ProfileAbstraction.lean` (`SoundAllows`, `SoundBlocks`, `soundProfile_no_allow_and_block`, `universalAllow_not_soundAllows_of_block`, `total_not_soundProfile_of_block`) | Lean build command above. | That abstraction labels, clusters, or buckets are ontological objects. | Develop baseline and non-reduction examples before expanding abstraction machinery. |
| Strict deformation profile compares block-vs-allow changes between consequence systems over the same Alpha carrier. | Speculative Lean bridge | `formal/lean/OmegaProper/Trajectory/DeformationProfile.lean`; `formal/lean/OmegaProper/Trajectory/DeformationProfileExamples.lean` | Lean build command above. | Recoverability, persistence, identity, propagation, boundary, value, or Omega. | Treat this as a speculative extension until non-reduction and baseline witnesses are packaged. |
| Declared registry recovery is stricter than existence/capacity recovery and optimized diagnostic recovery. | Empirical result + instrument audit | `omega/stochastic_distinction_channel/registry_first_x3_probe.py`; `docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_x3_result.md`; `tests/test_stochastic_registry_first_x3_probe.py` | `powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1` | Semantic recovery, value, agency, identity, or substrate-general transfer. | Package non-reduction witnesses showing where optimized recovery would overclaim compared to declared recovery. |
| The X3 registry-first probe reproduces an 8-state, 15-channel, 120-registered-row, 120-provenance-gap-row surface. | Reproducibility smoke / empirical result | `docs/REPRODUCIBILITY_SMOKE.md`; `scripts/validation/run_reproducibility_smoke.ps1`; retained X3 result note | `powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1` | Omega validation or trajectory-level viability. | Add one-command reproduction for future baseline/non-reduction witness suites. |
| The X3 adversarial audit passes with 105 audit rows and zero failures. | Instrument audit / reproducibility smoke | `omega/stochastic_distinction_channel/registry_first_adversarial_audit.py`; `tests/test_stochastic_registry_first_x3_probe.py`; `docs/REPRODUCIBILITY_SMOKE.md` | Same reproducibility smoke command. | That the empirical branch is holdout-ready or externally validated beyond this finite probe. | Add mutated-output fixtures to documentation so outside readers see what the audit rejects. |
| Future Field Atlas is retained as reachable-frontier morphology instrumentation, not as the central empirical object for Omega or valuerhood. | Deprecated / historical posture + instrument boundary | `docs/EXTERNAL_READER_GUIDE.md`; `docs/OMEGA_FORMALISM_PRIMER.md`; `docs/OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md`; `docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md` | Documentation review; no theorem-transfer claim from FFA morphology alone. | Value, valuerhood, agency, identity, compatibility, support, capture, erasure, or Omega validation. | Freeze large FFA expansion unless tied to a sharper trajectory-level or non-reduction question. |
| "A difference matters when erasing it changes what can follow" is the current public bridge sentence. | Philosophical motivation / framing | `README.md`; `docs/EXTERNAL_READER_GUIDE.md`; `docs/OMEGA_FORMALISM_PRIMER.md` | Not a standalone validation command. | Moral value, valence, preference, or valuerhood. | Translate into testable non-reduction witnesses and continuation-profile examples. |
| Omega as maximal compatible unfolding of consequence-bearing continuation remains a downstream ambition. | Conjecture / philosophical motivation | `README.md`; `docs/OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md` | No current validation command. | Omega-terminal existence in any substrate; value or valuer detection. | Do not promote until trajectory/process-bundle, compatibility, perturbation, and irreversible-loss layers have checked witnesses. |

## Immediate Missing Ledger Rows

The next scientific credibility target is non-reduction to familiar baselines.
The ledger should add rows only after we have canonical examples for:

```text
same reachability, different recoverability;
same entropy, different consequence-bearing distinction structure;
same optimized decoder success, different declared recovery;
same marginal preservation, different joint preservation;
same frontier morphology, different irreversible loss.
```

Those rows should cite concrete fixtures, baseline metrics, and pass/fail
commands rather than relying on prose analogy.
