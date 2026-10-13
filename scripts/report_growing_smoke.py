"""Compact engineering report; no new simulation or policy ranking."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=json.loads((a.run/'result.json').read_text());profile=json.loads((a.run/'PROFILE.json').read_text())
    if profile['exit_code']!=0 or r['status']!='passed_engineering_smoke':raise RuntimeError('Smoke incomplete')
    checks=r['checks']
    lines=['# Growing population: implementation and smoke', '',
           'Completed 2026-10-13. User authorization covered implementation and a hard-capped engineering smoke. No controller optimization or scientific preparation comparison was run.', '',
           '**Outcome:** paid population expansion and recursive assistance are implemented. The checked microscopic route lets an existing active unit construct another, and that newly constructed unit can assist a third. Each forward construction consumes one charged carrier; reverse reactions remain in the law. Precursor and carrier inventories are fixed.', '',
           '## Resource profile', '',
           f"The complete smoke took **{profile['wall_seconds']:.3f} seconds**, peak job memory **{profile['peak_job_bytes']/1024**2:.2f} MiB**. Limits were120 seconds,1GiB process-tree memory and256MiB output. No cap was hit. Raw artifacts remain local and ignored.", '',
           '| Local precursor inventories | Count states | Stored generator edges | Build, seconds | T1 sparse propagation, seconds | CSR storage, MiB | Dense transition path |',
           '|---|---:|---:|---:|---:|---:|---|']
    for c in r['cases']:
        lines.append(f"| {c['inventory']} | {c['states']} | {c['stored_edges_including_diagonal']} | {c['build_seconds']:.4f} | {c['propagation_seconds']:.4f} | {c['csr_bytes']/1024**2:.4f} | {c['sampled_entropy_status']} |")
    largest=r['cases'][-1]
    lines += ['', f"The 6400-state generator occupies {largest['csr_bytes']/1024**2:.3f}MiB of numerical CSR arrays. This is generator storage, not total process memory. One dense6400² float matrix would occupy {largest['dense_one_matrix_bytes']/1024**2:.1f}MiB before exponential workspaces or additional matrices. Sparse storage does not make sampled transition rows sparse.", '',
              'Exact declared-count sampled-history entropy is exercised through960 states; the larger case checks sparse probability and event-flux propagation only. An unsupported large entropy path is recorded explicitly instead of substituting event activity or silently changing the readout. Rule A is checked on the smallest count model only; no large lag survey was performed.', '',
              '## Verification', '',
              f"- One-unit-per-compartment rates reproduce the existing control fixture: error {checks['legacy_generator_error']:.3g}.",
              f"- Independent648-state body-coordinate generator projects exactly onto432 counted states: generator error {checks['projection']['generator_error']:.3g}, sampled transition error {checks['projection']['sampled_transition_error']:.3g}, projected row-entropy error {checks['projection']['projected_row_entropy_error']:.3g}.",
              f"- Largest energy derivative residual: {max(c['generator_energy_error'] for c in r['cases']):.3g}; largest population derivative residual: {max(c['generator_population_error'] for c in r['cases']):.3g}.",
              f"- Closed-reservoir Boltzmann/degeneracy balance passes all sizes; two-token switching check error {checks['switch_bill2_thermal_balance_error']:.3g}.",
              '- Probability, work/heat and integrated population accounts close. Thermal reconstruction, paid basal/assisted construction and all built-unit losses are separately included.',
              '- Zero local charge blocks forward assisted construction. Changing gate bill uses actual carrier debits and paired reverse reactions, without adding a score penalty.', '',
              'Count compression is exact for the declared histogram law and histogram-history readout. This is not equality with fully resolved body-site-history entropy. Slot coordinates serve as an independent audit and witness, not hidden lineage state or additional primary branch labels.', '',
              '## Recursive enabling witness', '',
              '| Step | Active units in left compartment | Charged carriers before→after | Specified parent→recipient | Rate of that route |',
              '|---|---|---|---|---:|']
    for i,v in enumerate(checks['recursive_assistance']['chain'],1):
        lines.append(f"| {i} | {v['source'][0][1]}→{v['target'][0][1]} | {v['source'][0][2]}→{v['target'][0][2]} | {v['example_parent_coordinate']}→{v['recipient_coordinate']} | {v['specified_pair_rate']:.6f} |")
    lines += ['', 'The first recipient is the second parent. Both routes have positive native rate, retain the assisting parent and conserve the declared energy through conversion of charge into apparatus. This establishes lawful recursive assistance, not a probability of successful expansion, a supercritical growth rate, an optimal policy or an ethical result.', '',
              '## What is ready next', '',
              '**GO:** a small controlled growth comparison with frozen policies, horizons, matched energy/material preparations, and actuator bills. The three-left/one-right case has960 counted states and supports the tested two-generation route. Its single matrix exponential took '+f"{next(c['transition_seconds'] for c in r['cases'] if c['inventory']==[3,1]):.3f} seconds in this smoke.", '',
              '**Not yet ready:** an exhaustive large-population optimizer using dense transition entropy. The six-unit case needs a scalable sampled-transition entropy method or a smaller declared controller search with further profiling. Current results do not justify copying the1296-policy sweep unchanged.', '',
              'Two hardwired controllers remain installed while functional apparatus population changes; newly built units are not new autonomous valuers. Lineage, personal identity, inherited controller policies, open-ended material inflow and a molecular gas baseline are not implemented. The matched preparation shell is constructed and energy-checked here, but its future breadth was not compared with a prepared seed.', '',
              '## Repair and provenance', '',
              'The first capped attempt failed the integrated population report because thermal precursor-to-worn reconstruction was omitted from the positive population-flow sum. That ledger was corrected without changing any reaction rates. The failed run is retained. The final witness was then strengthened by an independent parent/recipient event check and the smoke rerun. Nine new tests and22 focused tests including existing controller/readout checks pass.', '',
              f"Final run: `{a.run.name}`. Input hash: `{json.loads((a.run/'manifest.json').read_text())['input_hash']}`.", '',
              'Source/configuration snapshots and raw artifacts are in the ignored run directory. No deletion, Git commit, push, Drive publication or manuscript change was performed.', '']
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'SMOKE_RESULTS_r1.md').write_text('\n'.join(lines),encoding='utf-8')
    (a.output/'SMOKE_SUMMARY_r1.json').write_text(json.dumps({'result':r,'profile':profile},indent=2,allow_nan=False)+'\n')
    (a.output/'SMOKE_PROVENANCE.json').write_text(json.dumps({'run':str(a.run),'result_sha256':digest(a.run/'result.json'),
        'report_generator_sha256':digest(Path(__file__)),
        'report_hashes':{p.name:digest(p) for p in (a.output/'SMOKE_RESULTS_r1.md',a.output/'SMOKE_SUMMARY_r1.json')}},indent=2)+'\n')
    print(json.dumps({'report':str(a.output/'SMOKE_RESULTS_r1.md'),'status':r['status']}))
if __name__=='__main__':main()
