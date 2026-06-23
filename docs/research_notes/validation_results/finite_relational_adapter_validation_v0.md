# Finite Relational Adapter Validation V0

Date: 2026-06-23
Run context: working tree based on `79b8403`, with declared finite randomized
decoder-family parity applied before commit.

Claim boundary:

This retained summary reports finite adapter validation over declared toy
structures and generated finite hardening cases. It shows that the current
adapter code compiles these sources, runs the declared finite audits, retains
digests/artifacts, and observes the expected findings. It does not validate a
real substrate, prove Omega, infer value, establish agency, or certify that any
source abstraction is empirically correct.

## Commands

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter_adversarial.py `
  tests/test_finite_relational_graph_pair_transfer.py `
  -q --basetemp .tmp/pytest-graph-pair-refactor -p no:cacheprovider

./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_stochastic_recovery.py `
  tests/test_stochastic_recovery_theorem_spine.py `
  -q --basetemp .tmp/pytest-randomized-family-final -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_graph_pair_transfer `
  --out-root .tmp/finite_relational_graph_pair_transfer_characterization_final

./.venv/Scripts/python.exe -m omega.validation.finite_relational_stochastic_recovery `
  --out-root .tmp/finite_relational_stochastic_recovery_randomized_family

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_graph_pair_refactor

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_randomized_family

./.venv/Scripts/ruff.exe check omega/adapters/finite_relational/__init__.py `
  omega/adapters/finite_relational/adversarial_search.py `
  omega/adapters/finite_relational/graph_pair_transfer.py `
  omega/adapters/finite_relational/stochastic_recovery.py `
  tests/test_finite_relational_adapter_adversarial.py `
  tests/test_finite_relational_graph_pair_transfer.py `
  tests/test_finite_relational_stochastic_recovery.py `
  omega/validation/finite_relational_graph_pair_transfer.py
```

Result:

```text
graph-pair/adversarial pytest: 18 passed
stochastic recovery pytest: 12 passed
graph-pair transfer characterization: PASS, 2 studies, 4 representative cases
stochastic recovery characterization: PASS, 9 families
adapter smoke: PASS, 15 fixtures, focused pytest 83 passed
generated/adversarial validation: PASS, 17 cases
focused ruff: passed
```

## Retained Fixture Smoke

Run root:

```text
.tmp/finite_relational_adapter_smoke_randomized_family/20260623_175526
```

| Fixture | Audits | Findings | All passed | Source digest | Compiled/model digest |
| --- | --- | --- | --- | --- | --- |
| bounded_recovery_entropy_fail | 1 | `not_recoverable` | true | n/a | d58043dedf827c7d14156afbb206e4379f299725abdedc4ad074f360677e6afd |
| bounded_recovery_pass | 1 | `recoverable` | true | n/a | 38d67cc7f84c37afd948d63e56caabb1aaa0089d7ece1357fd421816cc389f1b |
| carrier_transfer_fail_missing_return | 1 | `not_transferred` | true | n/a | 9b3f7c50982417a0368bd4f70877e522dd6b6dd49ab3cbfd07eecae4ff32b439 |
| carrier_transfer_pass | 1 | `transferred` | true | n/a | d26b590398f7b1635bb8b50fe85904868f36445a5dee4a93b6a0373ea901821d |
| entropy_controlled_nonfactorization_fail | 1 | `witness` | true | n/a | 017008be69997421d8eb330d23537f03419fab826c48f3e65a150b1714788534 |
| hidden_reachability_loss_fail | 1 | `hidden_loss` | true | n/a | d0c0260dd5809635a2ce3ae00141e174fc82a2ae0cb39d1c2505c353ba40e720 |
| ordered_trace_nonfactorization_fail | 1 | `witness` | true | n/a | ee8de787256fd4574aca3ee4f8c814f4b2a67a911a7950126c59d9249f525520 |
| phantom_reachability_fail | 1 | `phantom` | true | n/a | 93701309ef0f9fcfe9896b7769147bdb887005fc1677e6e2bed7111a63285a54 |
| proxy_nonfactorization_fail | 1 | `witness` | true | n/a | 98b2ec4a5872fed3d1bd4861d99e281690982f6f6e6b61c5f8ec1b86683b81a7 |
| simple_form_nonfactorization_fail | 1 | `witness` | true | n/a | 8fab91005591ba138ada662ebe52880d17bea3afbca49575189234435b4618dd |
| sound_pass | 3 | `alpha_laws_hold`, `sound`, `certified` | true | n/a | c43d2a78a8e6d9bb6260f4fb2b4a4229fb0af853661a83b3f706b1b2e72c010e |
| derived_graph_mixed_asymmetry | 3 | `alpha_laws_hold`, `sound`, `certified` | true | 2d1c970a663dd6f32bc77e5d30a9a750bf3ff05053229942cce535030d80d61d | 7ab8a1c62c7826083c28666d9f52bcc1c511abf30f3397a9709c05e2c5c8bf1f |
| derived_graph_recurrent_carrier | 3 | `alpha_laws_hold`, `sound`, `certified` | true | 55544100fb48e025d143de39ab0cfb707b510a35b73de29ecfdf92513fc92384 | 44574d0c1997e2f37d02d5369320795a84e9b39a1bcde2f1e4ee3c697fc7926d |
| derived_graph_strict_asymmetry | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | 43f268a9fc16054047c06a3f2af3827c1210e7522871c263f2d851127bfc9125 | 452befd489b49b738fac2b7634ea703038ee2e1f597808f1ed584236145b805f |
| finite_grid_east_asymmetry | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | 6a8040b5f4af659576f7480e3029ac842380ad82189b167993ec726bf30bd639 | 1981d4ff89300c69788d49a1dfba8966d5c41f36c6e610921467530d1cd81eea |

## Generated / Adversarial Cases

Run root:

```text
.tmp/finite_relational_adapter_adversarial_graph_pair_refactor/20260623_171903
```

| Case | Source format | Audits | Findings | All passed | Source digest | Compiled digest |
| --- | --- | --- | --- | --- | --- | --- |
| generated_derived_graph_asymmetry | derived_graph | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | 0e9c20910a5e6626089cb973b57e0dfea9a9af69af9eada70f7206cea1c38ee1 | 72218b57d8c011e542bdb79c6c3707775dd2290099cb7c37d40c9717eb8cb374 |
| generated_derived_graph_carrier | derived_graph | 3 | `alpha_laws_hold`, `sound`, `certified` | true | 4f79a1c99411a488f33c9e28ba99a0d890e89253de44039c82a48eead1a592ab | edbc750fc7398a364e242eb9875b87b23f378aef477876e82d7ddf6f06d24b9c |
| generated_crosscutting_presentation_closure | finite_relational_ir | 4 | `closure_ok`, `closure_ok`, `closure_ok`, `closure_ok` | true | ef8d5210832711ae0bad4250475dadd82408b02e28e0780f839d495b34f0332a | ef8d5210832711ae0bad4250475dadd82408b02e28e0780f839d495b34f0332a |
| generated_failed_transport_fact_closure | finite_relational_ir | 3 | `not_transferred`, `closure_ok`, `closure_ok` | true | ea4d533fc65c033ddc47d968369b62e2f5f87f13091af4fd3d0207641668ed10 | ea4d533fc65c033ddc47d968369b62e2f5f87f13091af4fd3d0207641668ed10 |
| generated_finite_grid_asymmetry | finite_grid | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | 5fa177534f17c38e8f26cd92e986d8f06475c18455502f82b5d4310af2d69d81 | 70347caab151bc727a6498dd993225b11871fdedd1de74391a5df4a3bedf4961 |
| generated_graph_pair_transfer | derived_graph_pair | 1 | `transferred` | true | ae10f9028d5ebff08d38eb314f70c799c305780e6b05d7ab6ae1e518e44a718b | f62728b2b33d2512397808fd41fdd45d893690b8129ce4815111be4135ec0402 |
| generated_graph_pair_transfer_missing_return | derived_graph_pair | 1 | `not_transferred` | true | 994976cdf0cbdee385d04b1a4780d28de618b0c05209c59c08c1e3072be38f32 | 6ded5dccb4d76aa87451bfe686bbb0cb887769de3527fb9ea20bc53646200b6f |
| generated_hidden_reachability_loss | finite_relational_ir | 1 | `hidden_loss` | true | dc5d5c4f94bb47db57e48775d8842388424fa01d2a5f9a2af302ad7c1fa55df3 | dc5d5c4f94bb47db57e48775d8842388424fa01d2a5f9a2af302ad7c1fa55df3 |
| generated_multi_presentation_fact_closure | finite_relational_ir | 3 | `closure_ok`, `closure_ok`, `closure_ok` | true | 9dbf98b6cd49109dc899f221d6297320d5d9978e5d92756fb94258d268febd99 | 9dbf98b6cd49109dc899f221d6297320d5d9978e5d92756fb94258d268febd99 |
| generated_phantom_reachability | finite_relational_ir | 1 | `phantom` | true | 8a1849acdaf2c564b959317fa977c53cb3bd93b3b148a537cb309dbb8485d5e5 | 8a1849acdaf2c564b959317fa977c53cb3bd93b3b148a537cb309dbb8485d5e5 |
| generated_presentation_fact_closure | derived_graph | 6 | `alpha_laws_hold`, `not_sound`, `sound`, `certified`, `closure_ok`, `closure_ok` | true | ecf97c6f6f74390fb31f59469f930430c1c9c8d0a6568ccabd33bc102da027ea | 355cd4034071c1f15dec74b0ff62285e8033ac4403cad4db52646d0d890d8965 |
| generated_proxy_nonfactorization | finite_relational_ir | 1 | `witness` | true | c641b0aa1e5bd6dc155aab93bb2f73ecdca39377cfea86c2a3289740b65a2973 | c641b0aa1e5bd6dc155aab93bb2f73ecdca39377cfea86c2a3289740b65a2973 |
| generated_reachability_fact_closure | finite_relational_ir | 2 | `closure_ok`, `closure_ok` | true | c5023c24255914dbcbc47a51784daeb4c8db44992108c5c163c8ef98899262dc | c5023c24255914dbcbc47a51784daeb4c8db44992108c5c163c8ef98899262dc |
| generated_recovery_fact_closure | finite_relational_ir | 4 | `recoverable`, `not_recoverable`, `closure_ok`, `closure_ok` | true | 8e493ae551b89ef7d484983b63e45d156dbc8a14c52ec77ffab4dcf0f851dff4 | 8e493ae551b89ef7d484983b63e45d156dbc8a14c52ec77ffab4dcf0f851dff4 |
| generated_stale_reflected_fact_closure | finite_relational_ir | 3 | `closure_ok`, `closure_ok`, `closure_ok` | true | b37b63c504e4923e770149ed8ad313f8316b4f439dbd01cf0a36be6227e3e144 | b37b63c504e4923e770149ed8ad313f8316b4f439dbd01cf0a36be6227e3e144 |
| generated_transport_fact_closure | finite_relational_ir | 3 | `transferred`, `closure_ok`, `closure_ok` | true | ea2b1b0d4d45a52c05bd4503a52619fef541ec43616530ef573a784ebac8a811 | ea2b1b0d4d45a52c05bd4503a52619fef541ec43616530ef573a784ebac8a811 |
| generated_viability_fact_closure | finite_relational_ir | 2 | `closure_ok`, `closure_ok` | true | b78ede8c782d159e8ca33bccfeead1219d5a1c44a16780ae4e28d19d7cc8e86c | b78ede8c782d159e8ca33bccfeead1219d5a1c44a16780ae4e28d19d7cc8e86c |

## Grid Obstacle Characterization

Run root:

```text
.tmp/finite_relational_grid_obstacle_characterization_final/20260623_170426
```

| Study | Movement | Search space | Hidden-loss sets | No-loss sets | Representatives | All passed |
| --- | --- | --- | --- | --- | --- | --- |
| grid_obstacle_insertion_hidden_loss | orthogonal | 3x3, max obstacles 3 | 9 | 55 | 2 | true |
| grid_obstacle_east_south_diagonal_hidden_loss | east_south | 3x3, max obstacles 2 | 2 | 27 | 2 | true |
| grid_obstacle_orthogonal_rectangle_hidden_loss | orthogonal | 4x2, max obstacles 2 | 6 | 16 | 2 | true |

## Graph-Pair Transfer Characterization

Run root:

```text
.tmp/finite_relational_graph_pair_transfer_characterization_final/20260623_171412
```

| Study | Target graph | Target edge subsets | Transferred | Forward but not transferred | Not transferred | Representatives | All passed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_pair_two_node_transfer_sweep | 2 nodes | 4 | 1 | 1 | 3 | 2 | true |
| graph_pair_three_node_extension_transfer_sweep | 3 nodes | 64 | 18 | 22 | 46 | 2 | true |

## Notes

- The low-level finite relational IR fixtures do not have separate source
  digests because the model file is already the audit surface.
- The derived graph and finite grid fixtures retain both source and compiled
  model digests.
- The generated/adversarial cases are regenerated deterministically by
  `omega.adapters.finite_relational.adversarial_search`.
- The graph-pair transfer cases retain high-level source/target graph sources
  and a declared correspondence, then compile both graphs before running the
  carrier-transfer audit. The negative case keeps endpoint correspondence but
  rejects transfer because the target graph loses return structure.
- The source-contract helper centralizes the reserved finite relational IR
  fields (`predicates`, `relations`, `functions`, `profiles`, `audits`) and is
  exercised by derived graph, finite grid, grid-obstacle, and generated
  graph-pair source tests.
- The graph and grid compiler tests now require named compiled derivation
  rules, so source compilers are checked for explicit provenance rather than
  trusted by inspection alone.
- The grid obstacle characterization now covers three source-level grid
  classes. Each study retains a hidden-loss representative and a no-hidden-loss
  control, with all representatives checked by the same generic
  hidden-reachability-loss and presentation/fact-closure audits.
- The graph-pair transfer characterization now covers target graph dynamics
  while holding the source carrier and endpoint correspondence fixed. The
  three-node target sweep tests support extension without treating endpoint
  correspondence as identity.
- The closure-generated cases now include carrier-pair visibility,
  reachability target facts, viability target facts, bounded-recovery target
  facts, stale/reflected reach-status facts, multi-presentation row/column fact
  intersections, a crosscutting row/column/parity closure stress case,
  transported endpoint-role facts under a carrier-transfer contract, and a
  failed-transfer label-closure control.
- Presentation/fact-closure audit payloads now report seeded facts, common
  facts, surplus common facts, and nonconstant surplus target predicates. This
  exposes whether a closure case is merely certifying supplied seed facts or
  forcing additional nonconstant structure under the declared presentations.
- Target-scramble sensitivity now compares bounded-recovery behavior for a
  declared target against a supplied scrambled/erased target under the same
  observation and decoder family. The generated suite includes both a
  `sensitive` case and a decorative-target `not_sensitive` control.
- Dynamic presentation equivariance now checks whether a declared abstract
  transition is exactly the projection of exact dynamics under a presentation.
  The generated suite includes both an `equivariant` case and a
  `not_equivariant` control with one missing projected edge and one phantom
  abstract edge.
- Viable trajectory count now records finite safe-prefix count profiles for a
  declared transition and safety predicate. The generated suite includes a
  flat recurrent-cycle profile and a branching profile.
- Viable trajectory count comparison now compares exact and abstract count
  profiles under a declared presentation. The generated suite includes
  non-equivariant count inflation and count hiding controls under identity
  presentation.
- `carrier_transfer_pass` and `carrier_transfer_fail_missing_return` exercise
  the adapter-level transfer contract. The negative case preserves endpoint
  correspondence but rejects transfer because the target carrier loses return
  structure.

## Addendum: Target Scramble Sensitivity

Run roots:

```text
.tmp/finite_relational_adapter_smoke_scramble_sensitivity/20260623_210643
.tmp/finite_relational_adapter_adversarial_scramble_sensitivity/20260623_210650
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-scramble-sensitivity -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_scramble_sensitivity

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_scramble_sensitivity
```

Result:

```text
focused adapter/adversarial pytest: 31 passed
adapter smoke: PASS, 15 fixtures, focused pytest 87 passed
generated/adversarial validation: PASS, 19 cases
```

New generated cases:

| Case | Finding | Meaning |
| --- | --- | --- |
| generated_target_scramble_sensitivity | `sensitive` | Scrambling the declared target changes recoverability and the successful decoder surface. |
| generated_decorative_target_scramble_control | `not_sensitive` | Declared target and scrambled target are both unrecoverable under a constant observation. |

## Addendum: Dynamic Presentation Equivariance

Run roots:

```text
.tmp/finite_relational_adapter_smoke_dynamic_equivariance/20260623_211711
.tmp/finite_relational_adapter_adversarial_dynamic_equivariance/20260623_211711
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-dynamic-equivariance -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_dynamic_equivariance

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_dynamic_equivariance
```

Result:

```text
focused adapter/adversarial pytest: 34 passed
adapter smoke: PASS, 15 fixtures, focused pytest 90 passed
generated/adversarial validation: PASS, 21 cases
```

New generated cases:

| Case | Finding | Meaning |
| --- | --- | --- |
| generated_dynamic_equivariance | `equivariant` | Abstract label dynamics exactly matches the projection of exact state dynamics. |
| generated_dynamic_non_equivariance | `not_equivariant` | Abstract label dynamics misses one projected edge and adds one phantom edge. |

## Addendum: Viable Trajectory Count

Run roots:

```text
.tmp/finite_relational_adapter_smoke_viable_trajectory_count/20260623_212321
.tmp/finite_relational_adapter_adversarial_viable_trajectory_count/20260623_212324
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-viable-trajectory-count -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_viable_trajectory_count

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_viable_trajectory_count
```

Result:

```text
focused adapter/adversarial pytest: 37 passed
adapter smoke: PASS, 15 fixtures, focused pytest 93 passed
generated/adversarial validation: PASS, 23 cases
```

New generated cases:

| Case | Finding | Count profile |
| --- | --- | --- |
| generated_viable_trajectory_count_cycle | `count_ok` | `[2, 2, 2, 2]` |
| generated_viable_trajectory_count_branching | `count_ok` | `[2, 4, 8, 16]` |

## Addendum: Viable Count Distortion

Run roots:

```text
.tmp/finite_relational_adapter_smoke_viable_count_distortion/20260623_213312
.tmp/finite_relational_adapter_adversarial_viable_count_distortion/20260623_213312
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-viable-count-distortion -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_viable_count_distortion

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_viable_count_distortion
```

Result:

```text
focused adapter/adversarial pytest: 40 passed
adapter smoke: PASS, 15 fixtures, focused pytest 96 passed
generated/adversarial validation: PASS, 25 cases
```

New generated cases:

| Case | Finding | Exact profile | Abstract profile | Direction |
| --- | --- | --- | --- | --- |
| generated_viable_count_inflation | `distorted` | `[2, 2, 2]` | `[2, 4, 8]` | inflated by phantom abstract edges |
| generated_viable_count_hiding | `distorted` | `[2, 4, 8]` | `[2, 2, 2]` | hidden by missing abstract edges |

## Addendum: Dynamic Path Lifting And Extendable Prefix Counts

Run roots:

```text
.tmp/finite_relational_adapter_smoke_semantic_repairs/20260623_225619
.tmp/finite_relational_adapter_adversarial_semantic_repairs/20260623_225619
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-semantic-repairs -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_semantic_repairs

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_semantic_repairs
```

Result:

```text
focused adapter/adversarial pytest: 44 passed
adapter smoke: PASS, 15 fixtures, focused pytest 100 passed
generated/adversarial validation: PASS, 27 cases
```

New generated cases:

| Case | Findings | Meaning |
| --- | --- | --- |
| generated_edge_exact_path_lifting_failure | `edge_exact`, `not_step_lifts`, `not_path_lifts` | Global edge projection is exact, but an abstract path switches representatives inside a merged fiber and has no coherent exact lift. |
| generated_dead_end_safe_prefix | `count_ok`, `count_ok` | Safe-prefix counts report transient safe branching, while extendable safe-prefix counts are zero because the finite viability kernel is empty. |

Semantic repair:

```text
dynamic_presentation_equivariance is now documented as the legacy
edge-projection exactness audit. New adapter-facing process checks should use
dynamic_edge_projection_exactness together with dynamic_step_lifting or
dynamic_path_lifting.

viable_trajectory_count is now documented as the legacy safe-prefix count.
New count work should distinguish safe_prefix_count from
extendable_safe_prefix_count.
```

## Addendum: Family-Relative Closure And Generated Derive Mode

Run roots:

```text
.tmp/finite_relational_adapter_smoke_closure_derive/20260624_003632
.tmp/finite_relational_adapter_adversarial_closure_derive/20260624_003603
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-closure-derive -p no:cacheprovider

./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_source_parity.py `
  -q --basetemp .tmp/pytest-closure-source-parity -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_closure_derive

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_closure_derive
```

Result:

```text
focused adapter/adversarial pytest: 46 passed
source-parity pytest: 2 passed
adapter smoke: PASS, 15 fixtures, focused pytest 102 passed
generated/adversarial validation: PASS, 29 cases
```

Semantic repair:

```text
presentation_fact_closure now marks its surplus as family-relative:
  closure_mode = declared_family_candidate_fact_surface
  surplus_scope = family_relative

presentation_fact_derive_closure is a separate generated-universe audit:
  all finite partitions/presentations of the selected carrier;
  all Boolean predicate facts;
  all ordered visible-pair facts;
  seed facts filter admissible presentations;
  closure is the intersection of generated facts over admissible presentations.
```

New generated cases:

| Case | Findings | Meaning |
| --- | --- | --- |
| generated_presentation_fact_derive_closure | `derive_ok` | A nonconstant seed target filters the generated presentation universe and forces complement and visible-pair facts without a supplied candidate fact list. |
| generated_presentation_fact_derive_closure_constant_control | `derive_ok` | A constant seed admits every generated presentation, so only constant predicate facts survive and no visible pair is forced. |

## Addendum: Target Scramble Capacity Sensitivity

Run roots:

```text
.tmp/finite_relational_adapter_smoke_target_capacity/20260624_004406
.tmp/finite_relational_adapter_adversarial_target_capacity/20260624_004406
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-target-scramble-capacity -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_target_capacity

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_target_capacity
```

Result:

```text
focused adapter/adversarial pytest: 49 passed
adapter smoke: PASS, 15 fixtures, focused pytest 105 passed
generated/adversarial validation: PASS, 31 cases
```

Semantic repair:

```text
target_scramble_sensitivity is now explicitly decoder-relative:
  it compares exact recoverability and successful decoders within a declared
  decoder family.

target_scramble_capacity_sensitivity is a separate exact-capacity audit:
  it compares unrestricted deterministic exact recovery from the fixed
  observation for the target and supplied scramble.
```

New generated cases:

| Case | Finding | Meaning |
| --- | --- | --- |
| generated_target_scramble_capacity_sensitivity | `capacity_sensitive` | A four-state same-prevalence crosscut scramble changes unrestricted exact recovery from the fixed observation. |
| generated_target_scramble_capacity_label_swap_control | `not_capacity_sensitive` | A two-state Boolean complement scramble is only a target-label swap when both targets are exactly recoverable from the same observation. |

## Addendum: Observed Extendable Safe Word Counts

Run roots:

```text
.tmp/finite_relational_adapter_smoke_observed_words/20260624_005914
.tmp/finite_relational_adapter_adversarial_observed_words/20260624_005914
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter.py `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-observed-word-count -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_observed_words

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_observed_words
```

Result:

```text
focused adapter/adversarial pytest: 52 passed
adapter smoke: PASS, 15 fixtures, focused pytest 108 passed
generated/adversarial validation: PASS, 33 cases
```

Semantic repair:

```text
observed_extendable_safe_word_count counts distinct observation words generated
by safe prefixes whose endpoints lie in the finite viability kernel. This keeps
raw exact-state branching separate from distinguishable finite continuation
language.
```

New generated cases:

| Case | Finding | Meaning |
| --- | --- | --- |
| generated_observed_word_count_collapses_branching | `count_ok` | Fully branching two-state dynamics has state-path and extendable profiles `[2, 4, 8]`, but a constant observation collapses the observed-word profile to `[1, 1, 1]`. |
| generated_observed_word_count_labeled_cycle | `count_ok` | A labeled two-state recurrent cycle keeps visible alternating words with observed-word profile `[2, 2, 2]`. |

## Addendum: Closure Discovery

Run root:

```text
.tmp/finite_relational_closure_discovery_final/20260624_013131
```

Command:

```powershell
./.venv/Scripts/python.exe -m omega.validation.finite_relational_closure_discovery `
  --out-root .tmp/finite_relational_closure_discovery
```

Result:

```text
closure discovery: PASS
families: 3
cases: 136
nonconstant-surplus cases: 50
collapse cases: 86
```

Family summary:

| Family | Cases | Nonconstant surplus | Collapse |
| --- | ---: | ---: | ---: |
| predicate_seed_partition_sweep | 8 | 6 | 2 |
| reachability_seed_graph_sweep | 64 | 32 | 32 |
| viability_seed_graph_sweep | 64 | 12 | 52 |

Semantic repair:

```text
closure discovery does not predeclare expected surplus facts. It computes
generated-universe closure over small finite seed families and then records
whether nonconstant surplus facts appear or collapse.
```

Claim boundary:

```text
This is finite adapter-relative discovery. It does not validate a real
substrate, establish generic positive content at scale, or prove value,
agency, identity, valuerhood, or Omega.
```

## Addendum: Observed Word Lifting Monotonicity

Run roots:

```text
.tmp/finite_relational_adapter_smoke_observed_word_lifting/20260624_014141
.tmp/finite_relational_adapter_adversarial_observed_word_lifting/20260624_014141
```

Commands:

```powershell
./.venv/Scripts/python.exe -m pytest `
  tests/test_finite_relational_adapter_adversarial.py `
  -q --basetemp .tmp/pytest-observed-word-lifting-adversarial -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_observed_word_lifting

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_observed_word_lifting
```

Result:

```text
focused adversarial pytest: 23 passed
adapter smoke: PASS, 15 fixtures, focused pytest 109 passed
generated/adversarial validation: PASS, 35 cases
```

Semantic repair:

```text
observed_word_lifting_monotonicity checks the finite contract needed before an
abstract observed-word count can be treated as process-coherent: edge
projection, path lifting, observation compatibility, start compatibility,
safety reflection, and viability-kernel reflection.
```

New generated cases:

| Case | Finding | Meaning |
| --- | --- | --- |
| generated_observed_word_lifting_monotonicity | `monotone` | Path lifting and observation compatibility hold; exact and abstract observed-word profiles are both `[2, 2, 2]`. |
| generated_observed_word_lifting_inflation | `not_monotone` | Global edge projection is exact, but path lifting fails and the abstract observed-word profile `[1, 1, 2]` inflates exact profile `[1, 1, 1]`. |
