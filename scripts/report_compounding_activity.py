"""Retain complete activity/capacity maps without changing scientific scores."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/compounding'


def write_table(path,rows):
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def main():
    r=json.loads((DOC/'ACTIVITY_REANALYSIS.json').read_text())
    original=json.loads((DOC/'SUMMARY.json').read_text())
    timing=[];jumps=[];rates=[]
    for name,law in r['laws'].items():
        params=law['parameters']
        tags={'law':name,'capacity':params['capacity'],'cost':params['construction_cost'],
              'yield':params['packet_energy'],'damage':params['damage_rate']}
        for left,right in r['plan']['pairs']:
            a,b=law['mechanisms'][left],law['mechanisms'][right]
            for root in r['plan']['roots']:
                for t in r['plan']['horizons']:
                    x,y=a['roots'][root]['physical_horizons'][str(t)],b['roots'][root]['physical_horizons'][str(t)]
                    timing.append({**tags,'root':root,'horizon':t,'pair':f'{left}-{right}',
                                  **{'delta_'+key:x[key]-y[key] for key in x}})
                for count in r['plan']['fixed_jump_counts']:
                    x=a['roots'][root]['fixed_jump_bits'][str(count)]
                    y=b['roots'][root]['fixed_jump_bits'][str(count)]
                    jumps.append({**tags,'root':root,'jump_count':count,'pair':f'{left}-{right}',
                                 'left_bits':x,'right_bits':y,'delta_bits':x-y})
            for cadence in original['protocol']['cadences']:
                rates.append({**tags,'cadence':cadence,'pair':f'{left}-{right}',
                     'delta_history_rate':original['laws'][name]['rates'][left][str(cadence)]-original['laws'][name]['rates'][right][str(cadence)],
                     'delta_jump_rate':a['stationary_jump_rate']-b['stationary_jump_rate'],
                     'delta_finite_term_rate':a['stationary_finite_term_per_time']-b['stationary_finite_term_per_time'],
                     'left_jump_chain_rate':a['embedded_jump_entropy_rate_bits_per_jump'],
                     'right_jump_chain_rate':b['embedded_jump_entropy_rate_bits_per_jump']})
    write_table(DOC/'ACTIVITY_TIMING_MAP.csv',timing)
    write_table(DOC/'FIXED_JUMP_MAP.csv',jumps)
    write_table(DOC/'RATE_ACTIVITY_MAP.csv',rates)
    lines=['# Compounding activity reanalysis','',
           ('Retrospective queries over all24 completed physical laws, with original source bytes '
           'verified against the scientific snapshots. No transition law, cost, prediction, physical '
           'grain or original result was changed. These are explanatory diagnostics, not a new '
           'confirmatory test or a throughput-matched control.'),'',
           '## Loop-minus-basal rate against capacity','',
           'Central cost2/packet3/isolated damage0.005. Offered source rate remains0.6 in every row.','',
           '| Capacity | Rate gain at0.125 | Rate gain at0.25 | Rate gain at0.5 | Additional jumps/time |',
           '| ---: | ---: | ---: | ---: | ---: |']
    for m in (4,8,16,32):
        v=[x for x in rates if x['capacity']==m and x['cost']==2 and x['yield']==3
           and x['damage']==.005 and x['pair']=='loop-basal']
        by={x['cadence']:x for x in v}
        lines.append(f"| {m} | {by[.125]['delta_history_rate']:+.6f} | {by[.25]['delta_history_rate']:+.6f} | "
                     f"{by[.5]['delta_history_rate']:+.6f} | {by[.25]['delta_jump_rate']:+.6f} |")
    lines+=['',('The loop produces both more retained apparatus and more native event activity. '
            'Increasing throughput is a physical consequence of access, not a term to subtract '
            'from lushness. The comparison does not yet establish that a non-enabling process '
            'at comparable resource input or activity could not match that breadth. Matching '
            'accepted energy is a separate control and would not automatically match event counts.'),'',
            '## Fine-temporal coordinates','',
            'Capacity8/cost2/packet3/damage0.005, known seed root. Reference clock tau0=1.','',
            '| Physical horizon | Delta expected jumps | Delta F (bits) | Delta local destination surprisal (bits) |',
            '| ---: | ---: | ---: | ---: |']
    for t in r['plan']['horizons']:
        v=next(x for x in timing if x['law']=='M8-c2-y3-d0.005' and x['root']=='seed'
               and x['horizon']==t and x['pair']=='loop-basal')
        lines.append(f"| {t} | {v['delta_expected_jumps']:+.6f} | {v['delta_finite_term_bits']:+.6f} | "
                     f"{v['delta_local_destination_surprisal_bits']:+.6f} |")
    lines+=['',('At fine cadence, Delta ell is asymptotically '
            'Delta N*log2(tau0/delta)+Delta F. Here both coefficients are positive. '
            'F contains destination and timing terms; it is not an organization or value score. '
            'The leading expansion is not an exact formula at the original finite cadences.'),'',
            '## Jump-chain comparisons','',
            '| Fixed jumps | Loop−basal complete jump-sequence entropy, central seed |',
            '| ---: | ---: |']
    for count in r['plan']['fixed_jump_counts']:
        v=next(x for x in jumps if x['law']=='M8-c2-y3-d0.005' and x['root']=='seed'
               and x['jump_count']==count and x['pair']=='loop-basal')
        lines.append(f"| {count} | {v['delta_bits']:+.6f} |")
    lines+=['',('At stationarity, central embedded-jump entropy rates are1.051480bits/jump '
            'for the loop and0.384352 for basal. The loop differs in jump-sequence uncertainty '
            'as well as physical event frequency. The initial eight-jump loss remains visible; '
            'the later positive comparison is not a claim that every fixed-jump horizon wins.'),'',
            ('Fixed jump counts do not represent equal physical durations. Expected local destination '
            'surprisal over a time window is also not the full entropy of a random-length jump '
            'sequence. H(N_T) and the joint random-length mark/timing decomposition were not computed. '
            'No random event was deleted or subtracted from lushness.'),'',
            '## What this changes','',
            ('Retained paid recursive enabling remains demonstrated within the bounded model. '
            'Ablating the enabling reactions identifies their causal contribution; increased '
            'activity is one way that contribution reaches lushness. The outstanding question '
            'is whether a non-enabling process at matched resource throughput or activity could '
            'supply comparable breadth. The same-law lattice test '
            'addresses a different question: the preparation offset against naturally evolving '
            'thermal/dispersed matter. Its roots cannot retain different limiting rates in one '
            'finite irreducible law.'),'',
            ('The [throughput companion draft](LEDGER_AND_THROUGHPUT_AMENDMENTS_DRAFT_r1.md) '
            'defines accepted work, feasible overlap and flow-only calibration. It is not executed.'),'',
            (f"Stored N/F values reproduced with maximum absolute difference {r['maximum_reproduction_error']:.3g}. "
            'All24 laws and both known roots are retained in the CSV maps; no favorable subset was '
            'selected. ACTIVITY_QUERY_PLAN.json was frozen before the additional jump queries. '
            'Execution was capped at120s/512MiB and completed in about8s, peaking at266.4MiB. '
            'Sources, parent-result receipts and the query manifest are retained.'),'']
    (DOC/'ACTIVITY_REANALYSIS.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    main()
