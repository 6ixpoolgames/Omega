"""Capped extraction-module smoke and compact first comparison."""
import argparse
from pathlib import Path
import run_domination_b1 as engine

ROOT = Path(__file__).resolve().parents[1]
engine.DOC = ROOT/'docs/research_notes/lushness_testbed/resource_transfer'
engine.LOCAL = ROOT/'results/local_runs/lushness_testbed/resource_transfer'
old_sources = engine.sources
engine.sources = lambda: old_sources()+['scripts/run_resource_transfer.py']


def cases(mode):
    base = {'charge_capacity': 1, 'd_energy_capacity': 2, 'd_energy_quantum': .5}
    common = {'parameters': base, 'entropy_backend': 'uniformized',
              'entropy_threads': 2, 'block_rows': 128}
    if mode == 'smoke':
        return [{**common, 'id': 'smoke-extract', 'transfer_policy': {'mode': 'extract'},
                 'horizons': [16, 64], 'cadences': [.25]}]
    base = {'charge_capacity': 2, 'd_energy_capacity': 3, 'd_energy_quantum': .25}
    common['parameters'] = base
    result = []
    for cost in (.25, .5, .75):
        for name, strength in (('passive', .2), ('extract', .2), ('extract', 2.)):
            result.append({**common, 'id': f'{name}-c{cost:g}-a{strength:g}',
                           'transfer_policy': {'mode': name, 'cost': cost, 'assistance': strength}})
    for name in ('ordinary', 'cooperate', 'sham'):
        result.append({**common, 'id': name+'-c0.5-a0.2',
                       'transfer_policy': {'mode': name, 'cost': .5, 'assistance': .2}})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['smoke', 'survey'])
    parser.add_argument('--jobs', type=int, default=1)
    parser.add_argument('--seconds', type=float, default=300)
    parser.add_argument('--budget', type=float, default=3600)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 2:
        raise ValueError('Use one or two capped workers')
    raise SystemExit(engine.execute(cases(args.mode), args.mode, args.jobs, args.seconds, args.budget))
