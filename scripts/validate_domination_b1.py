"""Check immutable receipts, numerical readouts and retained storage."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from report_domination_b1 import load, DOC
from omega_v2.testbed.workflow.manifest import verify_bundle


def validate(mode):
    status,results,configs=load(mode)
    maxima={key:None for key in ('generator_energy','integrated_energy','stationarity','occupation','sampled_occupation','sampled_poisson','kernel_mass')}
    def keep(key,value):
        if value is not None:
            maxima[key]=max(maxima[key] or 0.,abs(value))
    sources=set()
    for receipt in status['cases']:
        if receipt['status']!='complete':continue
        manifest=verify_bundle(Path(receipt['run']))
        if manifest['config']!=receipt['configuration']:
            raise RuntimeError('Receipt configuration differs from immutable bundle')
        if receipt['profile']['cap_reason'] or receipt['profile']['exit_code']:
            raise RuntimeError('Incomplete process marked complete')
        r=results[receipt['id']]
        sources.add(status.get('source_hash'))
        keep('generator_energy',r['energy_residual'])
        keep('stationarity',r.get('stationary_residual'))
        for physical in r['physical'].values():
            for row in physical.values():
                keep('integrated_energy',row['integrated_energy_residual'])
                keep('occupation',row.get('occupation_residual'))
        for clock in r['cadences'].values():
            keep('sampled_poisson',clock['poisson_residual'])
            keep('kernel_mass',clock['kernel_diagnostics'].get('kernel_mass',clock['kernel_diagnostics'].get('mass_residual')))
            for scores in clock['profiles'].values():
                for row in scores.values():
                    keep('sampled_occupation',row['sampled_occupation_residual'])
                    for subject in ('D','S'):
                        interval=row['subjects'][subject]
                        if interval['lower_bits']>interval['upper_bits']+1e-7:
                            raise RuntimeError('Inverted subject bounds')
    if any(v is not None and v>1e-6 for v in maxima.values()):
        raise ArithmeticError('Reported residual exceeds declared validation envelope')
    storage={str(p.relative_to(ROOT)):sum(x.stat().st_size for x in p.rglob('*') if x.is_file())
             for p in (DOC,ROOT/'results/local_runs/lushness_testbed/domination_b1')}
    summary={'mode':mode,'status':status['status'],'completed':len(results),
             'source_hashes':list(sources),'residual_maxima':maxima,
             'storage_bytes':storage,'large_kernels_retained':False,
             'wall_seconds':sum(r['profile']['wall_seconds'] for r in status['cases'] if r['status']=='complete'),
             'peak_job_bytes':max((r['profile']['peak_job_bytes'] for r in status['cases'] if r['status']=='complete'),default=0)}
    (DOC/(mode.upper()+'_VALIDATION.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':
    validate(sys.argv[1] if len(sys.argv)>1 else 'survey')
