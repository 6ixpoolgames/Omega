"""Compact engineering receipts only. No scientific scores or automatic cleanup."""
import importlib.metadata
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/robust_generativity'


def main():
    protocol = json.loads((DOC/'ENGINEERING_PROTOCOL.json').read_text())
    names = ['TESTS']+[job['id'] for job in protocol['jobs']]
    receipts, rows = {}, []
    for name in names:
        status = json.loads((DOC/(name+'_STATUS.json')).read_text())
        if status['status'] != 'complete':
            raise RuntimeError(f'Incomplete validation: {name}')
        manifest = verify_bundle(status['run'])
        # Do not silently summarize a stale engineering gate after code changes.
        import hashlib
        if any(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() != r['sha256']
               for r in manifest['sources']):
            raise RuntimeError(f'Source changed after engineering: {name}')
        receipts[name] = status
        if name != 'TESTS':
            result = json.loads((DOC/(name+'_RESULTS.json')).read_text())
            if result['rankings_inspected']:
                raise RuntimeError('Engineering report cannot hide scientific inspection')
            for case in result['rows']:
                row = {'id': name, **case, 'profile': status['profile']}
                rows.append(row)
    tests = (Path(receipts['TESTS']['run'])/'worker.log').read_text(encoding='utf-8')
    count = int(re.findall(r'(\d+) passed', tests)[-1])
    attempts = []
    for profile_path in sorted((ROOT/'results/local_runs/lushness_testbed/robust_generativity').glob('*/PROFILE.json')):
        attempt = json.loads(profile_path.read_text())
        attempts.append(attempt)
    atomic_json(DOC/'ENGINEERING_ATTEMPTS.json', {'attempts': attempts,
        'retention': 'frozen local bundles unchanged; this index retains failed attempt receipts'})
    errors = {k: max(abs(r.get(k, 0.)) for r in rows) for k in
              ('dark_balance_residual', 'bank_ledger_residual', 'energy_ledger_residual',
               'poisson_residual', 'harmonic_rate_residual', 'one_step_identity_residual')}
    output = {'status': 'engineering_complete_science_unfrozen', 'tests_passed': count,
              'max_residuals': errors, 'rows': rows, 'receipts': receipts,
              'rankings_inspected': False,
              'environment_recorded_same_session': {'python': sys.version,
                   **{p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'pytest')}}}
    atomic_json(DOC/'ENGINEERING_SUMMARY.json', output)
    table = ['| Validation | Physical states | Tracker states | Seconds | Peak MiB | Result |',
             '| --- | ---: | ---: | ---: | ---: | --- |']
    for r in rows:
        prof = r['profile']
        tracker = str(r.get('initial_seed', {}).get('query_states', '—'))
        result = 'passed' if r['status'] == 'complete' else 'kernel gate; not run'
        table.append(f"| {r['id']} | {r['states']:,} | {tracker} | {prof['wall_seconds']:.2f} | "
                     f"{prof['peak_job_bytes']/1024**2:.1f} | {result} |")
    text = f'''# Robust compounding: engineering result

15 October 2026. **Engineering complete; scientific protocol remains unfrozen.**
No preparation ranking, mechanism winner, C/R/L/J verdict or hypothesis score
has been inspected. The implemented chemistry is ready for scientific-batch
integration and freeze, not an already completed robust-compounding experiment.

{count} focused tests pass. They cover full-packet dark detailed balance for all
six mechanisms and both feedback shapes; saturated capture reverses; conserved
material and bank/energy accounting; constant damage hazard with irreversible
loss; graph-defined closure; neutral depth monitors; exact versus sampled
dynamics; pulse/recovery conditioning; and class-aware finite entropy, rates and
offsets against the independent dense backend.

## Measured budget

Every job ran from a hash-verified source/config snapshot with hard limits of
120 seconds, 512 MiB process-tree memory and 32 MiB output. The full physical
sampled kernel has a separate 160 MiB gate. Tracker matrices remain sparse and
are excluded from the physical entropy readout.

{chr(10).join(table)}

M6 profiles execute the finite-history numerical route through horizons
16/64/256/1024/4096 and the strong path query through 256. These computations
retain timing and validity receipts only, not scientific arm comparisons.
Corner cases additionally cover the all-assistance-off low-source sink at
cadence 0.125 and high-source, high-damage sublinear sink at cadence 0.5.
All ran within caps. The 8,910-state sink kernel needs about 606 MiB **for the
kernel alone**, so it is rejected before calculation; the physical world is
not pruned or made less stochastic to fit memory.

Maximum absolute residuals across completed cases:

{chr(10).join('- '+k+': '+format(v,'.3g') for k,v in errors.items())}

## Corrections made during engineering

The first M6 smoke exposed rare-state amplification at the arbitrary Poisson
anchor. The solve now uses a normalized stationary equation and a high-mass
anchor per recurrent class. A regression test retains the failed case. The
failed receipt and all subsequent attempts remain in
[ENGINEERING_ATTEMPTS.json](ENGINEERING_ATTEMPTS.json); frozen runs were not
overwritten or deleted.

Reversible capture also required a funding correction before science. Gross
capture can recycle initial, bath-return and reverse-capture packets. The
external-spending lower bound deducts their full possible contribution; a
zero-drive test verifies that recycling cannot become external funding. The
complete bank ledger includes reverse capture's charge debit.

## Implemented foundation and next boundary

- Physical cycle A→B→C→A, positive basal chemistry, paid construction/capture,
  fractional feedback, bilateral link ablations, repairable damage and a real
  material sink.
- Permanent initial-seed witness and separately resetting any-start detector.
  Detected-chain intensity is a conservative lower bound, not complete genealogy.
- Joint depth/retained-expansion/later-function query, deterministic one-B pulse,
  unconditional recovery, functional uptime and graph closure.
- Memory-gated sampled kernels, sparse recurrent/transient Poisson analysis and
  exact finite-history identities. Finite lushness stays primary; rates diagnose
  sustained contribution under the declared boundary.

The next stage implements the scientific batch/report orchestration, including
the complete piecewise history score for pulse arms, coordinate/activity
decomposition, all registered C/R/L/J maps, and final prediction/tolerance
freeze. No scientific run is authorized by this engineering report. Individual
modules are validated; the complete scientific workload is not yet profiled.
The measured M6 costs support proceeding without increasing caps or reducing
the declared physical inventory.

The source-window test remains separate. A repayment estimate applies only to
an appropriate positive mechanism-rate contrast; same-Q irreducible roots
cannot acquire different limiting rates. Persistence-versus-repayment is a
restricted prediction, not a general theorem. Whole-type knockout and a
matched single-type comparator remain follow-ups. Count-stage success cannot
overturn the earlier spatial seed-versus-unbound reversal.

See [specification](PROPOSED_SPEC_r1.md), [monitor contract](MONITOR_CONTRACT.md),
[physics/numerics](PHYSICS_AND_NUMERICS.md), and
[machine-readable receipts](ENGINEERING_SUMMARY.json). No commit, push or Drive
change was made.
'''
    (DOC/'ENGINEERING.md').write_text(text, encoding='utf-8')
    print(json.dumps({'status': output['status'], 'tests': count,
                      'report': str(DOC/'ENGINEERING.md')}, indent=2))


if __name__ == '__main__':
    main()
