"""Additional descriptive summaries of the unchanged completed Stage A data."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'


def read(name):
    with (DOC/name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    comparisons, fuel, crossings = (read(p) for p in ('COMPARISON_MAP.csv', 'FUEL_MATCH.csv', 'CROSSINGS.csv'))
    disagreement = [r for r in comparisons if int(r['S_sign']) and int(r['global_sign'])
                    and int(r['S_sign']) != int(r['global_sign'])]
    by_target = Counter((r['target'], r['mode'], int(r['S_sign'])) for r in disagreement)
    by_horizon = Counter(float(r['horizon']) for r in disagreement)
    statuses = Counter(r['status'] for r in crossings)
    stable = [r for r in crossings if r['status'] == 'corridor_stable_bracket']
    # Status name is recorded by the original report, not guessed from row order.
    if not stable:
        stable = [r for r in crossings if 'stable' in r['status'] and 'conditional' not in r['status']]
    grouped_fuel = defaultdict(list)
    for r in fuel:
        if float(r['horizon']) == 256 and float(r['cadence']) == .25:
            # role_id contains the original target/mode; preserve the exact ID.
            target = r['role_id'].split('-k1-', 1)[1].split('-'+r['mode'], 1)[0]
            grouped_fuel[target, r['mode']].append(float(r['global_role_minus_interpolated_random']))
    lines = ['# Updated interpretation: Stage A descriptive follow-ups', '',
             '15 October 2026 (analysis of the completed Stage A map; no new physical runs).', '',
             '## Subject disagreement', '',
             f'{len(disagreement)} resolved comparison rows have opposite S and whole-field signs. '
             'These are case × horizon × cadence rows, not independent experiments. '
             'A positive S sign means S gains while the whole loses; a negative sign means the reverse.', '',
             '| Target | Mechanism | S sign | Rows |', '| --- | --- | ---: | ---: |']
    lines += [f'| {t} | {m} | {s:+d} | {n} |' for (t,m,s),n in sorted(by_target.items())]
    lines += ['', 'By horizon: '+', '.join(f'T{t:g}: {n}' for t,n in sorted(by_horizon.items()))+'.', '',
              'The whole includes D and the shared packet, so an improvement for S can be outweighed '
              'by intervention costs or changed D/background continuation. The converse is also possible. '
              'These groupings describe where disagreement occurs; they do not identify a unique causal entropy split.', '',
              '## Strength crossings that survive all three cadences', '',
              f'{len(stable)} recorded brackets are corridor-stable. Each bracket is a target/mode/environment/'
              'bill/horizon comparison, not an exact root or a new optimum.', '',
              '| Target | Mechanism | Brackets |', '| --- | --- | ---: |']
    lines += [f'| {t} | {m} | {n} |' for (t,m),n in sorted(Counter((r['target'],r['mode']) for r in stable).items())]
    lines += ['', '## Role targets against random routes at matched interpolated fuel', '',
              'T256, cadence 0.25, supply 0.12, κ=1. Every observed nonmonotonic interpolation branch '
              'is retained. These are descriptive fuel-matched curve comparisons, not exact kernels at '
              'equal realized fuel or a certified causal isolation.', '',
              '| Target | Mechanism | Branch comparisons | Positive / negative | Median Δ bits | Range |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for (t,m), values in sorted(grouped_fuel.items()):
        lines.append(f'| {t} | {m} | {len(values)} | {sum(v>1e-5 for v in values)} / '
                     f'{sum(v < -1e-5 for v in values)} | {statistics.median(values):.3f} | '
                     f'{min(values):.3f}…{max(values):.3f} |')
    lines += ['', 'This table addresses whether target role matters beyond the measured bill. '
              'A route-matched randomized action is a real physical intervention; its randomness counts. '
              'The spread over random routes and branches remains part of the result.', '',
              '## Conservative-field subject conflict already present in Stage A', '',
              'Reanalysis of the existing field control gives a second resolved direction. '
              'For the unit trap potential at T1024, D loses marginal-history breadth while '
              'S and the whole gain at every tested cadence. Device formation/loss and S '
              'transitions account for the field energy; the field remains in the native '
              'dark detailed-balance test. This is not a new simulation or a fuel-matched '
              'actuator comparison.', '',
              '| Cadence | Whole Δ bits | D interval | S interval |',
              '| ---: | ---: | ---: | ---: |']
    native = sorted([r for r in comparisons if r['slice']=='A6' and r['target']=='trap'
                     and float(r['field_shift'])==1 and float(r['horizon'])==1024],
                    key=lambda r:float(r['cadence']))
    for r in native:
        lines.append(f"| {float(r['cadence']):g} | {float(r['global_delta']):.3f} | "
                     f"[{float(r['D_difference_lower']):.3f}, {float(r['D_difference_upper']):.3f}] | "
                     f"[{float(r['S_difference_lower']):.3f}, {float(r['S_difference_upper']):.3f}] |")
    lines += ['', 'The individual and whole can disagree both when restriction benefits the '
              'individual and when helping another costs the individual. A positive private '
              'gain is not necessary for the general subject distinction.', '',
              '## Current C5 status', '',
              'Stage A already resolves paid private/whole conflicts at T256. The next gap is the '
              'mechanism of private gain and materially profitable appropriation, not the first existence '
              'of a subject conflict. Apparatus channels remain functional controller proxies rather than '
              'established conscious valuers. Discovery, bilateral choice and self-defence are separate expansions.', '']
    (DOC/'UPDATED_FOLLOWUPS.md').write_text('\n'.join(lines), encoding='utf-8')
    summary = {'S_whole_opposing_rows': len(disagreement), 'crossing_statuses': dict(statuses),
               'stable_brackets': len(stable), 'fuel_branch_comparisons_at_T256': sum(map(len,grouped_fuel.values()))}
    (DOC/'FOLLOWUP_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
