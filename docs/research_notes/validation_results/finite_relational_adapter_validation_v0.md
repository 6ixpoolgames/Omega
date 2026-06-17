# Finite Relational Adapter Validation V0

Date: 2026-06-18  
Run context: working tree based on `df99e3a`, with the carrier-transfer audit
batch applied before commit.

Claim boundary:

This retained summary reports finite adapter validation over declared toy
structures and generated finite hardening cases. It shows that the current
adapter code compiles these sources, runs the declared finite audits, retains
digests/artifacts, and observes the expected findings. It does not validate a
real substrate, prove Omega, infer value, establish agency, or certify that any
source abstraction is empirically correct.

## Commands

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp\finite_relational_adapter_smoke_retained_v0

.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp\finite_relational_adapter_adversarial_retained_v0
```

Additional focused check:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\test_finite_relational_adapter.py `
  tests\test_finite_relational_adapter_smoke.py `
  -q --basetemp .tmp\pytest-adapter-transfer -p no:cacheprovider
```

Result:

```text
adapter transfer pytest: 10 passed
adapter smoke: PASS, 10 fixtures, focused pytest 25 passed
generated/adversarial validation: PASS, 6 cases
```

## Retained Fixture Smoke

Run root:

```text
.tmp\finite_relational_adapter_smoke_retained_v0\20260618_031022
```

| Fixture | Audits | Findings | All passed | Source digest | Compiled/model digest |
| --- | ---: | --- | --- | --- | --- |
| `carrier_transfer_fail_missing_return` | 1 | `not_transferred` | true | n/a | `9b3f7c50982417a0368bd4f70877e522dd6b6dd49ab3cbfd07eecae4ff32b439` |
| `carrier_transfer_pass` | 1 | `transferred` | true | n/a | `d26b590398f7b1635bb8b50fe85904868f36445a5dee4a93b6a0373ea901821d` |
| `hidden_reachability_loss_fail` | 1 | `hidden_loss` | true | n/a | `d0c0260dd5809635a2ce3ae00141e174fc82a2ae0cb39d1c2505c353ba40e720` |
| `phantom_reachability_fail` | 1 | `phantom` | true | n/a | `93701309ef0f9fcfe9896b7769147bdb887005fc1677e6e2bed7111a63285a54` |
| `proxy_nonfactorization_fail` | 1 | `witness` | true | n/a | `98b2ec4a5872fed3d1bd4861d99e281690982f6f6e6b61c5f8ec1b86683b81a7` |
| `sound_pass` | 3 | `alpha_laws_hold`, `sound`, `certified` | true | n/a | `c43d2a78a8e6d9bb6260f4fb2b4a4229fb0af853661a83b3f706b1b2e72c010e` |
| `derived_graph_mixed_asymmetry` | 3 | `alpha_laws_hold`, `sound`, `certified` | true | `2d1c970a663dd6f32bc77e5d30a9a750bf3ff05053229942cce535030d80d61d` | `7ab8a1c62c7826083c28666d9f52bcc1c511abf30f3397a9709c05e2c5c8bf1f` |
| `derived_graph_recurrent_carrier` | 3 | `alpha_laws_hold`, `sound`, `certified` | true | `55544100fb48e025d143de39ab0cfb707b510a35b73de29ecfdf92513fc92384` | `44574d0c1997e2f37d02d5369320795a84e9b39a1bcde2f1e4ee3c697fc7926d` |
| `derived_graph_strict_asymmetry` | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | `43f268a9fc16054047c06a3f2af3827c1210e7522871c263f2d851127bfc9125` | `452befd489b49b738fac2b7634ea703038ee2e1f597808f1ed584236145b805f` |
| `finite_grid_east_asymmetry` | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | `6a8040b5f4af659576f7480e3029ac842380ad82189b167993ec726bf30bd639` | `1981d4ff89300c69788d49a1dfba8966d5c41f36c6e610921467530d1cd81eea` |

## Generated / Adversarial Cases

Run root:

```text
.tmp\finite_relational_adapter_adversarial_retained_v0\20260618_031029
```

| Case | Source format | Audits | Findings | All passed | Source digest | Compiled digest |
| --- | --- | ---: | --- | --- | --- | --- |
| `generated_derived_graph_asymmetry` | `derived_graph` | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | `0e9c20910a5e6626089cb973b57e0dfea9a9af69af9eada70f7206cea1c38ee1` | `72218b57d8c011e542bdb79c6c3707775dd2290099cb7c37d40c9717eb8cb374` |
| `generated_derived_graph_carrier` | `derived_graph` | 3 | `alpha_laws_hold`, `sound`, `certified` | true | `4f79a1c99411a488f33c9e28ba99a0d890e89253de44039c82a48eead1a592ab` | `edbc750fc7398a364e242eb9875b87b23f378aef477876e82d7ddf6f06d24b9c` |
| `generated_finite_grid_asymmetry` | `finite_grid` | 3 | `alpha_laws_hold`, `not_sound`, `sound` | true | `5fa177534f17c38e8f26cd92e986d8f06475c18455502f82b5d4310af2d69d81` | `70347caab151bc727a6498dd993225b11871fdedd1de74391a5df4a3bedf4961` |
| `generated_hidden_reachability_loss` | `finite_relational_ir` | 1 | `hidden_loss` | true | `dc5d5c4f94bb47db57e48775d8842388424fa01d2a5f9a2af302ad7c1fa55df3` | `dc5d5c4f94bb47db57e48775d8842388424fa01d2a5f9a2af302ad7c1fa55df3` |
| `generated_phantom_reachability` | `finite_relational_ir` | 1 | `phantom` | true | `8a1849acdaf2c564b959317fa977c53cb3bd93b3b148a537cb309dbb8485d5e5` | `8a1849acdaf2c564b959317fa977c53cb3bd93b3b148a537cb309dbb8485d5e5` |
| `generated_proxy_nonfactorization` | `finite_relational_ir` | 1 | `witness` | true | `c641b0aa1e5bd6dc155aab93bb2f73ecdca39377cfea86c2a3289740b65a2973` | `c641b0aa1e5bd6dc155aab93bb2f73ecdca39377cfea86c2a3289740b65a2973` |

## Notes

- The low-level finite relational IR fixtures do not have separate source
  digests because the model file is already the audit surface.
- The derived graph and finite grid fixtures retain both source and compiled
  model digests.
- The generated/adversarial cases are regenerated deterministically by
  `omega.adapters.finite_relational.adversarial_search`.
- `carrier_transfer_pass` and `carrier_transfer_fail_missing_return` exercise
  the adapter-level transfer contract. The negative case preserves endpoint
  correspondence but rejects transfer because the target carrier loses return
  structure.
