# Growing population: implementation and smoke

Completed 2026-10-13. User authorization covered implementation and a hard-capped engineering smoke. No controller optimization or scientific preparation comparison was run.

**Outcome:** paid population expansion and recursive assistance are implemented. The checked microscopic route lets an existing active unit construct another, and that newly constructed unit can assist a third. Each forward construction consumes one charged carrier; reverse reactions remain in the law. Precursor and carrier inventories are fixed.

## Resource profile

The complete smoke took **3.446 seconds**, peak job memory **175.74 MiB**. Limits were120 seconds,1GiB process-tree memory and256MiB output. No cap was hit. Raw artifacts remain local and ignored.

| Local precursor inventories | Count states | Stored generator edges | Build, seconds | T1 sparse propagation, seconds | CSR storage, MiB | Dense transition path |
|---|---:|---:|---:|---:|---:|---|
| [1, 1] | 144 | 1158 | 0.0134 | 0.0020 | 0.0138 | exact_declared_count_readout |
| [2, 1] | 432 | 4248 | 0.0463 | 0.0027 | 0.0503 | exact_declared_count_readout |
| [3, 1] | 960 | 10460 | 0.1146 | 0.0043 | 0.1234 | exact_declared_count_readout |
| [3, 3] | 6400 | 88600 | 0.9521 | 0.0249 | 1.0384 | unsupported_by_dense_path_above_1000_states |

The 6400-state generator occupies 1.038MiB of numerical CSR arrays. This is generator storage, not total process memory. One dense6400² float matrix would occupy 312.5MiB before exponential workspaces or additional matrices. Sparse storage does not make sampled transition rows sparse.

Exact declared-count sampled-history entropy is exercised through960 states; the larger case checks sparse probability and event-flux propagation only. An unsupported large entropy path is recorded explicitly instead of substituting event activity or silently changing the readout. Rule A is checked on the smallest count model only; no large lag survey was performed.

## Verification

- One-unit-per-compartment rates reproduce the existing control fixture: error 8.88e-16.
- Independent648-state body-coordinate generator projects exactly onto432 counted states: generator error 8.88e-16, sampled transition error 5.55e-16, projected row-entropy error 5.77e-15.
- Largest energy derivative residual: 5.06e-14; largest population derivative residual: 1.82e-14.
- Closed-reservoir Boltzmann/degeneracy balance passes all sizes; two-token switching check error 8.67e-19.
- Probability, work/heat and integrated population accounts close. Thermal reconstruction, paid basal/assisted construction and all built-unit losses are separately included.
- Zero local charge blocks forward assisted construction. Changing gate bill uses actual carrier debits and paired reverse reactions, without adding a score penalty.

Count compression is exact for the declared histogram law and histogram-history readout. This is not equality with fully resolved body-site-history entropy. Slot coordinates serve as an independent audit and witness, not hidden lineage state or additional primary branch labels.

## Recursive enabling witness

| Step | Active units in left compartment | Charged carriers before→after | Specified parent→recipient | Rate of that route |
|---|---|---|---|---:|
| 1 | 1→2 | 3→2 | 0→1 | 0.133333 |
| 2 | 2→3 | 2→1 | 1→2 | 0.088889 |

The first recipient is the second parent. Both routes have positive native rate, retain the assisting parent and conserve the declared energy through conversion of charge into apparatus. This establishes lawful recursive assistance, not a probability of successful expansion, a supercritical growth rate, an optimal policy or an ethical result.

## What is ready next

**GO:** a small controlled growth comparison with frozen policies, horizons, matched energy/material preparations, and actuator bills. The three-left/one-right case has960 counted states and supports the tested two-generation route. Its single matrix exponential took 0.249 seconds in this smoke.

**Not yet ready:** an exhaustive large-population optimizer using dense transition entropy. The six-unit case needs a scalable sampled-transition entropy method or a smaller declared controller search with further profiling. Current results do not justify copying the1296-policy sweep unchanged.

Two hardwired controllers remain installed while functional apparatus population changes; newly built units are not new autonomous valuers. Lineage, personal identity, inherited controller policies, open-ended material inflow and a molecular gas baseline are not implemented. The matched preparation shell is constructed and energy-checked here, but its future breadth was not compared with a prepared seed.

## Repair and provenance

The first capped attempt failed the integrated population report because thermal precursor-to-worn reconstruction was omitted from the positive population-flow sum. That ledger was corrected without changing any reaction rates. The failed run is retained. The final witness was then strengthened by an independent parent/recipient event check and the smoke rerun. Nine new tests and22 focused tests including existing controller/readout checks pass.

Final run: `growing-smoke-20261013T061035Z-f73909`. Input hash: `28c167af2dc8881c91d6d79162b977b6e2a5da233583f77f39581b371b341eca`.

Source/configuration snapshots and raw artifacts are in the ignored run directory. No deletion, Git commit, push, Drive publication or manuscript change was performed.
