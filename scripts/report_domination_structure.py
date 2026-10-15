"""Explain the measured control using actual transition supports and flows."""
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from report_domination_b1 import load,DOC,csv_write


def main():
    probe=json.loads((DOC/'STRUCTURE_PROBE.json').read_text())
    if probe['status']!='complete':raise RuntimeError('Structural probe is incomplete')
    _,results,_=load('survey')
    rows=[]
    for receipt in probe['cases']:
        name=receipt['id'];a=results[name];b=results[name.split('-trap-',1)[0]+'-idle']
        for time,counts in receipt['result']['counts'].items():
            pa,pb=(r['physical']['device_present'][time] for r in (a,b))
            la,lb=pa['ledger'],pb['ledger'];T=float(time)
            native_moves=lambda l:sum(l.get(k,0) for k in ('S.move','S.discovery_paid','S.discovery_basal'))
            delta_moves=native_moves(la)+counts['movement']-native_moves(lb)
            S_events=pa['average']['S_event_rate']*T
            D_events=sum(v['jumps'] for v in pa['D_native_attribution']['families'].values())
            background_only=sum(la.get(k,0) for k in ('packet_thermal','source','export'))
            identity=pa['expected_jumps']-(D_events+S_events-counts['all_joint_actuation']+background_only)
            capture_check=(la['capture_S']+la['reverse_capture_S']-la['S.capture']-counts['capture_or_reverse'])
            if abs(identity)>1e-6 or abs(capture_check)>1e-6:
                raise ArithmeticError('Independent physical flow/support counts disagree')
            rows.append({'id':name,'horizon':T,**counts,
                'pocket_origin_share':counts['pocket_origin']/counts['all_joint_actuation'],
                'delta_S_location_changes':delta_moves,
                'delta_S_events':S_events-pb['average']['S_event_rate']*T,
                'delta_global_events':pa['expected_jumps']-pb['expected_jumps'],
                'delta_net_S_capture':la['net_capture_S']-lb['net_capture_S'],
                'delta_work':la['accepted_work']-lb['accepted_work'],
                'global_count_inclusion_exclusion_residual':identity,
                'capture_crosscheck_residual':capture_check})
    csv_write('STRUCTURAL_COUNTS.csv',rows)
    lines=['# Structural account of trap-entry steering','',
           'Query-only analysis of the original physical operators. No scores or laws were changed. '
           'The four physical source files were matched byte-for-byte to the scientific snapshot. '
           'Occupation integrals were computed independently of the entropy solver.', '',
           '## What the controller actually redirects','',
           '| Yield | Horizon | Ordinary-origin acts | Pocket-return acts | Redirects to movement | Redirects to capture/reverse |',
           '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in sorted(rows,key=lambda r:(r['id'],r['horizon'])):
        yield_value=int(r['id'].split('-')[0][1:])
        lines.append(f"| {yield_value} | {r['horizon']:g} | {r['ordinary_origin']:.4f} | "
                     f"{r['pocket_origin']:.4f} | {r['movement']:.4f} | {r['capture_or_reverse']:.4f} |")
    lines+=['','Most acts originate outside the pocket, so the result cannot be described simply '
            'as keeping S in the pocket. Return interception is nevertheless real. Steering also '
            'redirects some attempts into native local chemistry, including capture and its reverse, '
            'paid construction and thermal charge/assembly. The gross chemical count is not net yield.', '',
            '## Motion, capture and work can differ','',
            '| Yield | Horizon | S location changes Δ | S events Δ | Global events Δ | S net capture Δ | Work Δ |',
            '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in sorted(rows,key=lambda r:(r['id'],r['horizon'])):
        yield_value=int(r['id'].split('-')[0][1:])
        lines.append(f"| {yield_value} | {r['horizon']:g} | {r['delta_S_location_changes']:.3f} | "
                     f"{r['delta_S_events']:.3f} | {r['delta_global_events']:.3f} | "
                     f"{r['delta_net_S_capture']:.4f} | {r['delta_work']:.4f} |")
    lines+=['', 'At high yield, the T256 breadth advantage coexists with less net capture and '
            'accepted work, while S makes more physical transitions. The T1024 capture/work signs '
            'reverse. This is a finite-history trade among physical continuations, not evidence '
            'that more harvested energy alone explains the score.', '',
            '## Count overlap is kept explicit','',
            'In this adapter, joint D/S events are the paid steering acts. Full event count equals '
            'D changes plus S changes, minus joint changes, plus packet-only changes. The identity '
            'and the independent capture-flow cross-check close within 10⁻⁶ events. These are '
            'physical count identities, not an additive entropy decomposition. No motion, thermal '
            'activity or chemical cycling is subtracted from lushness.', '']
    (DOC/'STRUCTURAL_ACCOUNT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'rows':len(rows),'count_identity_max_error':max(abs(r['global_count_inclusion_exclusion_residual']) for r in rows)}))

if __name__=='__main__':main()
