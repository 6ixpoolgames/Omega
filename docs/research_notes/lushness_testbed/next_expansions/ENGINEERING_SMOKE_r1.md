# Reserve-sensitive implementation and capped smoke

2026-10-14. User authorized implementation, then limited execution to smoke before
reassessment. No scientific optimization or prediction scoring has been run.

## Implemented

`controllers/reserve.py` supplies explicit local active/worn response laws. Native
gate-switch reactions use this law without changing their stoichiometry, energy,
fuel bills or available thermal routes. Fuel, gate and foreign-state feedback are
rejected. Reserve controllers require embodied actuation. Existing tuple policies
retain their old path, kernel and ledgers.

The family has22 declared policies: six constant controls plus service below each
threshold2/3, with mix25/mix50/mix75/export above it, each with/without extra service
when worn material exists. Actual response surfaces are saved with kernel-plus-ledger
aliases. This is a restricted family, not an unrestricted optimum. Both compartments
share the same law; the one-slot compartment cannot exhibit a two-unit reserve.

`experiments/reserve_smoke.py` evaluates one preselected controller, threshold2,
mix50 above reserve, extra service when worn. It uses the existing depth-1 reversible
world with embodied actuation, basal relaxation0.003 and fully correlated shocks
h=0.02,p=1. Coverage checks compile the family but never rank it or solve its scores.

`run_reserve_smoke.py` freezes source/specification and executes a verified worker
under Windows process-tree limits:120s,1GiB,256MiB output, one numerical thread.
Workers cannot import live Omega source. Raw snapshots and vectors stay ignored
under results/local_runs. The smoke exercises conditional history entropy at physical
horizons1,4,16,64,256, common-deadline closure, endpoint probability and integrated
energy/population accounting. It reports checks and timings, not scientific scores.

## Measured runs

| Adapter | States | Declared / unique models | Wall time | Peak job memory | Result |
|---|---:|---:|---:|---:|---|
| 1+1 |256|22 /6|1.748s|113.16MiB|Pass|
| 3+1 |2560|22 /18|20.085s|482.86MiB|Pass|

The3+1 run spent5.199s in entropy/class analysis,1.085s in the full horizon
recurrence,0.812s in access/accounting queries and11.819s compiling the coverage
family. Maximum solver residual3.30e-13; integrated accounting residuals below
3.88e-14. Neither run hit a cap.

The initial1+1 attempt failed on a report-field name after calculations completed.
Corrected `estimated_dense_bytes` to the solver's `dense_bytes_estimate`, retained
the failed snapshot, and reran successfully. A direct full engineering regression
now checks the output contract. No physical parameter changed to repair this issue.

Provenance:
-1+1: reserve-smoke-1+1-20261013T172259Z-22d2d6,
 input89531137997dd72e34e42da32c7a174913639bbc8b69cc3833b56900db9e2e8b.
-3+1: reserve-smoke-3+1-20261013T172315Z-2e8ddd,
 inputcbaeedddef5b6802143700e7a3c2541f46316c8704a2d4a8faf2701d62240c9a.
-Failed initial report: reserve-smoke-1+1-20261013T172240Z-79a30c.

73 focused controller, actuation, shock, class/access, experiment, material, sampling,
contract, snapshot and companion tests pass, including a nonconstant threshold's
thermal detailed balance and reachable distinct response witnesses.

## Locked-resource companion

The15-state finite-store fixture also passes a separately frozen hard-capped smoke:
0.523s,75.66MiB peak job memory, no cap hit. Internal stored-fuel energy is recorded
separately from external work (zero in this fixture). Energy residual5.55e-17;
fuel-energy residual2.78e-17; transition row error2.22e-16. Both declared roots have
energy4 and preserve total probability. No entropy rankings have been run.

Run locked-resource/20261013T172722Z-0276d1; input hash
10f24ff3b61a2cb33fdb72b785bc0eecd5cd9e21d895ce6a31c891887cec36ef.
See ../locked_resource/README.md and PROTOCOL_DRAFT.json. The conserved resource
inventory is one; the apparatus/fuel slot budget is a coarse energy model, not a
complete molecular material ledger. There is no replenishment/maintained-drive
arm yet, so it is a finite access fixture, not a sustained-growth test.

## Reassessment

The existing3+1 exact solver fits the per-process cap. No inventory reduction or
memory redesign is needed for this module.18 distinct models rather than22 labels
must be evaluated per law/cadence. Extrapolating this fixed run gives roughly two to
three minutes per18-model case before reporting overhead; reducible absorbing
classes and other cadences can differ. This is a forecast, not a measured full batch.
Run jobs sequentially unless separately measured concurrent memory permits them.

The scientific orchestration still needs the new family wired into finite-horizon
optimization, all-tie outputs, fixed-policy replay, cadence sign audit and predictions.
The old channel runner accepts only binary observation tables and retains its old
rate-first scoring; do not use it to claim this new protocol has been run. Freeze
the new candidate list, exact cases and total budget only after that integration.

The companion locked-resource adapter is separately documented. Its smoke does not
demonstrate a generative advantage, and this smoke does not demonstrate adaptive
protection. Those are the scientific questions reserved for the subsequent batch.
