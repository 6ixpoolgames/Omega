"""Compact batch accounting and temporal-corridor summaries; no new objective."""
import csv
import json
import platform
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/c5_upgrade'

def main():
    import numpy
    import scipy
    studies=[];corridor=[]
    for directory in sorted(p for p in DOC.iterdir() if p.is_dir()):
        status_file=directory/'SURVEY_STATUS.json'
        if not status_file.exists():continue
        status=json.loads(status_file.read_text());completed=[c for c in status['cases'] if c['status']=='complete']
        rows=[]
        if (directory/'COMPARISONS.csv').exists():
            rows=[r for r in csv.DictReader((directory/'COMPARISONS.csv').open()) if r['id']!=r['reference']]
        groups=defaultdict(list)
        for row in rows:groups[row['id'],row['horizon']].append(row)
        for (key,horizon),values in groups.items():
            signs={r['whole_sign'] for r in values}
            corridor.append({'study':directory.name,'case':key,'horizon':float(horizon),
                'cadences':','.join(str(x) for x in sorted(float(r['cadence']) for r in values)),
                'whole_corridor':'positive' if signs=={'positive'} else 'negative' if signs=={'negative'} else 'mixed_or_unresolved',
                'D_corridor':'positive' if all(float(r['D_lower'])>float(r['tolerance']) for r in values) else 'negative' if all(float(r['D_upper'])< -float(r['tolerance']) for r in values) else 'mixed_or_unresolved',
                'S_corridor':'positive' if all(float(r['S_lower'])>float(r['tolerance']) for r in values) else 'negative' if all(float(r['S_upper'])< -float(r['tolerance']) for r in values) else 'mixed_or_unresolved'})
        studies.append({'study':directory.name,'status':status['status'],'completed_cases':len(completed),
            'planned_cases':status['total_cases'],'source_hash':status['source_hash'],
            'worker_wall_seconds_sum':sum(c['profile']['wall_seconds'] for c in completed),
            'worker_wall_is_not_cpu_time':True,
            'peak_worker_bytes':max((c['profile']['peak_job_bytes'] for c in completed),default=0),
            'signed_clock_horizon_comparisons':len(rows),
            'positive':sum(r['whole_sign']=='positive' for r in rows),
            'negative':sum(r['whole_sign']=='negative' for r in rows),
            'unresolved':sum(r['whole_sign']=='unresolved' for r in rows)})
    with (DOC/'CORRIDOR.csv').open('w',newline='',encoding='utf-8') as f:
        keys=list(corridor[0]) if corridor else ['study','case']
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(corridor)
    expected={'pump','loss','opportunity','audit-controls','cost-boundary','supplied-pump','opportunity-active'}
    probe=DOC/'historical-crossover/PROBE_STATUS.json'
    probe_complete=probe.exists() and json.loads(probe.read_text())['status']=='complete'
    smokes={}
    for name in ('pump','loss','opportunity','audit-controls','cost-boundary'):
        path=DOC/name/'SMOKE_STATUS.json'
        smokes[name]=json.loads(path.read_text())['status'] if path.exists() else 'missing'
    record={'studies':studies,'expected_studies':sorted(expected),
        'reporting_environment':{'python':platform.python_version(),'numpy':numpy.__version__,
                                 'scipy':scipy.__version__,'platform':platform.platform()},
        'total_completed_cases':sum(s['completed_cases'] for s in studies),
        'all_survey_studies_complete':expected=={s['study'] for s in studies} and all(s['status']=='complete' for s in studies),
        'historical_crossover_probe_complete':probe_complete,'engineering_smokes':smokes,
        'report_bytes':sum(p.stat().st_size for p in DOC.rglob('*') if p.is_file()),
        'ignored_local_bytes':sum(p.stat().st_size for d in (ROOT/'results/local_runs/lushness_testbed').glob('c5_upgrade_*') for p in d.rglob('*') if p.is_file())}
    (DOC/'EXECUTION_ACCOUNT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    lines=['# C5 physical upgrade — execution index','',
        '[Updated interpretation](INTERPRETATION.md) · [Specification](SPECIFICATION.md) · [Reproduction](REPRODUCE.md) · [Historical corrections](../C5_AUDIT_CORRECTIONS_2026-10-16.md)','',
        '| Study | Complete / planned | State | Positive / negative / unresolved finite contrasts | Peak worker MiB |',
        '| --- | ---: | --- | ---: | ---: |']
    for s in studies:
        lines.append(f"| [{s['study']}]({s['study']}/RESULTS.md) | {s['completed_cases']} / {s['planned_cases']} | {s['status']} | {s['positive']} / {s['negative']} / {s['unresolved']} | {s['peak_worker_bytes']/1024**2:.1f} |")
    lines+=['','Counts are case × cadence × horizon contrasts, not independent trials or evidence weights. CORRIDOR.csv groups the three clocks without assuming that cadence tests full state-grain invariance.',
        'Whole-field finite lushness, marginal-history bounds, energy return and functioning are distinct readouts. A positive history difference does not certify material profit, donation, persistent enabling or an ethical verdict.',
        'Funded-pump pathway names specify forward stoichiometry; net direction is measured. Historical steering interpretation changes retain the old numbers and frozen source.',
        'Source hashes may differ between studies, including preserved historical newline conventions and added orchestration scripts; each result has its own verified frozen-source archive.',
        'The historical crossover query, when complete, is reported separately in [historical-crossover](historical-crossover/RESULTS.md). No commit, push or Drive publication is performed by these scripts.','']
    (DOC/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'completed':record['total_completed_cases'],'survey_complete':record['all_survey_studies_complete'],
                      'report_bytes':record['report_bytes'],'local_bytes':record['ignored_local_bytes']}))

if __name__=='__main__':main()
