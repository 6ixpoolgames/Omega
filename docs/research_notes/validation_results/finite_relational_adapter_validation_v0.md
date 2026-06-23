# Finite Relational Adapter Validation V0

Date: 2026-06-23
Run context: working tree based on `8694d23`, with robust randomized stochastic
recovery adapter parity applied before commit.

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
  -q --basetemp .tmp/pytest-stochastic-robust-randomized-final -p no:cacheprovider

./.venv/Scripts/python.exe -m omega.validation.finite_relational_graph_pair_transfer `
  --out-root .tmp/finite_relational_graph_pair_transfer_characterization_final

./.venv/Scripts/python.exe -m omega.validation.finite_relational_stochastic_recovery `
  --out-root .tmp/finite_relational_stochastic_recovery_robust_randomized_final

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp/finite_relational_adapter_adversarial_graph_pair_refactor

./.venv/Scripts/python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp/finite_relational_adapter_smoke_robust_randomized

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
stochastic recovery pytest: 9 passed
graph-pair transfer characterization: PASS, 2 studies, 4 representative cases
stochastic recovery characterization: PASS, 9 families
adapter smoke: PASS, 15 fixtures, focused pytest 80 passed
generated/adversarial validation: PASS, 17 cases
focused ruff: passed
```

## Retained Fixture Smoke

Run root:

```text
.tmp/finite_relational_adapter_smoke_robust_randomized/20260623_173519
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
- `carrier_transfer_pass` and `carrier_transfer_fail_missing_return` exercise
  the adapter-level transfer contract. The negative case preserves endpoint
  correspondence but rejects transfer because the target carrier loses return
  structure.
