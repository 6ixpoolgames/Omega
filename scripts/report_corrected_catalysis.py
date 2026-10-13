"""Report shared-law preparations separately from acceleration ablations."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from omega_v2.testbed.workflow.manifest import verify_bundle
    folder = ROOT/'docs/research_notes/lushness_testbed/corrected_catalysis'
    status = json.loads((folder/'SCIENCE_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise ValueError('Complete science required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    result = json.loads((run/'result.json').read_text())
    rows = result['rows']
    if result['input_hash'] != manifest['input_hash'] or [r['case'] for r in rows] != manifest['config']['protocol']['cases']:
        raise ValueError('Frozen case mismatch')
    def select(cap, dt, enabled, inflow=True):
        return next(r for r in rows if r['case']['parameters']['apparatus_capacity'] == cap
                    and r['case']['parameters']['catalysis_enabled'] == enabled
                    and r['case']['parameters']['inflow_enabled'] == inflow
                    and r['case']['cadence'] == dt)
    contrasts = []
    for cap in (1, 2):
        for dt in (.125, .25, .5):
            a, b = select(cap, dt, True), select(cap, dt, False)
            contrasts.append({'capacity': cap, 'cadence': dt,
                              'preparation_bits64': a['bits']['64']['organized']-a['bits']['64']['unorganized'],
                              'acceleration_rate_increment': a['rates']['organized']-b['rates']['organized']})
    a = select(1, .25, True)
    claims = {'C1': a['bits']['64']['organized'] > a['bits']['64']['unorganized']+1e-10,
              'C2': all(c['acceleration_rate_increment'] > 1e-10 for c in contrasts if c['capacity'] == 1),
              'M1': max(abs(r['rates']['organized']-r['rates']['unorganized']) for r in rows) < 1e-10,
              'M2': max(abs(select(cap, dt, True, False)['rates']['organized']
                            -select(cap, dt, False, False)['rates']['organized'])
                        for cap in (1,2) for dt in (.125,.25,.5)) < 1e-10}
    summary = {'claims': claims, 'contrasts': contrasts, 'rows': rows,
               'input_hash': result['input_hash'], 'protocol': manifest['config']['protocol']}
    (folder/'SUMMARY.json').write_text(json.dumps(summary, separators=(',', ':'), allow_nan=False)+'\n')
    lines = ['# Corrected catalysis results', '',
             'Same law in both preparations: basal feedback remains active and apparatus speeds both directions.', '',
             '| Capacity | Cadence | Organized-minus-unorganized bits T64 | Acceleration-minus-basal-only rate |',
             '|---:|---:|---:|---:|']
    for c in contrasts:
        lines.append(f"| {c['capacity']} | {c['cadence']} | {c['preparation_bits64']:.6f} | {c['acceleration_rate_increment']:.6f} |")
    lines += ['', 'Frozen predictions: '+', '.join(f'{k}={v}' for k,v in claims.items()), '',
              'Preparation differences are transient/offset effects. Between-law acceleration ablation tests the mechanism, not sustained superiority of one starting preparation.',
              'The old always-available coupling was not ordinary uncatalyzed chemistry. It remains archived as a different mechanism control.', '']
    (folder/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(claims))


if __name__ == '__main__':
    main()
