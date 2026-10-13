# Binding calibration report

Status: **pass**

One bivalent A, two B; normalized association/dissociation constants both 1.
The symmetric occupancy chain has rates 4, 1 forward and 1, 2 backward.
The resolved-site model has four states; its projection reproduces that chain.

| Cadence | Coarse bits at T=4 | Resolved bits | Difference |
|---|---:|---:|---:|
| 0.25 | 18.682151974 | 24.072045103 | 5.389893129 |
| 0.125 | 28.865146147 | 34.865023513 | 5.999877366 |
| 0.5 | 10.624661122 | 14.575087101 | 3.950425979 |
| 1.0 | 5.495671692 | 7.763674027 | 2.268002336 |

## Checks

- P1: True
- P2: True
- P3: True
- P4: True
- P5: True
- P6: True
- closed_binding_balance: True
- semigroup: True

Own SSA: 10000 independent trials; upstream SSA: 256 trials.
Category-wise errors and predeclared sampling bounds are in summary.json.

This distinguishes bookkeeping invariance from physical resolution sensitivity.
It does not identify a universal grain or test an ethical policy.

Frozen input hash: bc608b1541360c02b93144f331350765f85bd83bd948357de9a8029bccf7dcef

## Engineering record

Date: 2026-10-13. Original Omega branch: codex/operational-continuation-comparison.
BioNetGen Python distribution 0.8.7; bundled engine 2.9.3; direct engine invocation.
Final run: binding-20261013T011034Z-3f9800.

Seven focused tests passed. All three hand-generator errors are zero. The
strong-lumping projection error is zero. Passive relabeling error is approximately
1.1e-14 bits; duplicated-channel error is zero. Both sampler comparisons passed
the predeclared categorywise diagnostic bounds.

The final capped run took 6.73 seconds with
115.71 MiB peak reported job memory.
The finalized local run, including source snapshots, is 211,496 bytes. All 285
manifest-listed artifact hashes and the frozen input hash were verified.

The first engine attempt failed because Git Perl could not locate BioNetGen's
modules through Windows backslash paths. Setting BNGPATH and using forward-slash
paths fixed it without changing kinetics. A first successful run exposed an
artifact-finalization ordering issue during review; finalization now happens
in the parent after worker status/profile/log completion. The corrected repeat
produced identical generators, breadth profiles, SSA frequencies and verdicts.
The earlier attempts remain local and indexed by directory; nothing was erased.

A smaller-model read-only audit found no central numerical error, confirmed the
scope of the entropy and multiplicity checks, and noted the now-fixed finalization
issue. The Python wrapper is used only to locate the engine; engine files and
Perl executable are hashed. General dependency replay across machines is still
an implementation obligation.

## Interpretation and next step

We can correct the bookkeeping issue: the symmetric model's factors 2,1,1,2 and
the homodimer's factor 0.5 produce the expected stochastic rates without a second
symmetry division. Resolving left/right occupancy is different: it changes the
history readout while preserving the projected occupancy law. At cadence 0.25,
that difference is 5.389893129 bits through T=4. This is real resolution sensitivity
in the declared fixture, not a generativity advantage or preferred grain.

This closes the tiny engine/multiplicity calibration. The next scientific task
is to freeze the reversible, metastable-unused and feedback assembly rules,
including resource/thermodynamic scope and physically possible feedback at each
inventory. The controlled access fixture remains required for optimizer behavior.

Raw networks, traces and manifests are local under the run directory. The report
and reproduction instructions are compact retained evidence. No Git commit,
push, cleanup service or new-repository publication occurred.