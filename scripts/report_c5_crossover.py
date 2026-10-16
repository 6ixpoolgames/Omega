"""Validate and present the historical finite-horizon crossover probes."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import verify_bundle
import archive_domination_b1_sources as archive

def main():
    doc=ROOT/'docs/research_notes/lushness_testbed/c5_upgrade/historical-crossover'
    status=json.loads((doc/'PROBE_STATUS.json').read_text());receipt=status['cases'][0]
    if receipt['status']!='complete':raise RuntimeError('Probe is not complete')
    manifest=verify_bundle(Path(receipt['run']))
    if manifest['config']!=receipt['configuration']:raise ValueError('Config differs')
    payload=(doc/'cases'/(receipt['identity']+'.json')).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=receipt['result_sha256']:raise ValueError('Result differs')
    r=json.loads(payload)
    if not r['imports_from_snapshot'] or receipt['profile']['cap_reason'] or receipt['profile']['exit_code']:
        raise RuntimeError('Source or process validation failed')
    lines=['# Historical C5 crossover: exact finite probes','',
        '**Numerical follow-up, not new mobility evidence.** This historical case uses chemistry-inclusive steering. Its scope is corrected in the audit note.',
        '',f"Cadence {r['cadence']}; rate Δ {r['rate_delta']:+.9f} bits/time; offset Δ {r['offset_delta']:+.9f} bits.",
        f"Asymptotic horizon estimate: {r['asymptotic_horizon_estimate']:.6f}. This estimate does not certify a finite ranking.",'',
        '| Horizon | Exact sampled-history difference | Numerical allowance |',
        '| ---: | ---: | ---: |']
    for row in r['exact_sampled_finite_probes']:
        lines.append(f"| {row['horizon']:g} | {row['whole_delta']:+.9f} | {row['numerical_allowance']:.3g} |")
    signs=[1 if row['whole_delta']>row['numerical_allowance'] else -1 if row['whole_delta']< -row['numerical_allowance'] else 0
           for row in r['exact_sampled_finite_probes']]
    lines+=['',f"A resolved sign bracket is {'present' if 1 in signs and -1 in signs else 'absent'} among these probes. No exact crossover root is claimed.",
        f"Historical T256 reproduction error: {r['historical_T256_bridge_error']:.3g} bits.",
        f"Source `{status['source_hash']}`; retained receipt and compact result certify inputs and caps.",'']
    (doc/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    archive.DOC=doc;archive.LOCAL=ROOT/'results/local_runs/lushness_testbed/c5_upgrade_historical-crossover';archive.main()

if __name__=='__main__':main()
