"""Freeze the corrected basal-plus-catalytic benchmark before comparisons."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from omega_v2.testbed.resource_feedback import DEFAULT_PARAMETERS
from omega_v2.testbed.workflow.manifest import atomic_json


def main():
    folder = ROOT/'docs/research_notes/lushness_testbed/corrected_catalysis'
    path = folder/'PROTOCOL.json'
    if path.exists():
        raise FileExistsError('Frozen registration cannot be overwritten')
    base = dict(vars(DEFAULT_PARAMETERS))
    base['rates'] = dict(base['rates'])
    base['feedback'] = 'basal_catalytic'
    cases = [{'parameters': {**base, 'apparatus_capacity': cap, 'carrier_capacity': cap,
                             'catalysis_enabled': enabled, 'inflow_enabled': inflow}, 'cadence': dt}
             for cap in (1, 2) for enabled in (True, False) for inflow in (True, False)
             for dt in (.125, .25, .5)]
    atomic_json(path, {'status': 'frozen_before_scientific_ranking', 'cases': cases,
                      'horizons': [1, 4, 16, 64, 256], 'primary_cadence': .25,
                      'primary_capacity': 1,
                      'primary': 'same-law organized versus equal-energy unorganized finite-history breadth',
                      'secondary': 'enabled versus basal-only mechanism ablation, not preparation comparison',
                      'predictions': {
                          'C1': 'Organized root exceeds unorganized root at T64 under enabled driven law, primary capacity/cadence',
                          'C2': 'Enabled minus basal-only sustained rate positive across three cadences, primary capacity',
                          'M1': 'Within each finite law roots share asymptotic rate to 1e-10',
                          'M2': 'Depleted-inflow rates agree across acceleration ablation to 1e-10'},
                      'law': 'k_feedback(a)=0.002+0.04*a; both directions share this coefficient',
                      'no_catalyst': 'a=0 still has positive native paired feedback rate',
                      'legacy_control': 'always-available 0.04 coupling remains archived, not called ordinary uncatalyzed chemistry',
                      'caps': {'seconds': 120, 'memory': 1024**3, 'output_cap': 32*1024**2}})
    print(path)


if __name__ == '__main__':
    main()
