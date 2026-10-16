"""Complete finite-controller search with physical response delays and bills."""
import argparse
from pathlib import Path
import run_domination_b1 as engine

ROOT = Path(__file__).resolve().parents[1]
previous_sources = engine.sources
engine.sources = lambda: previous_sources()+[
    'scripts/run_c5_policy_search.py', 'scripts/c5_policy_worker.py',
    'tests/test_reactive_allocation.py',
    'docs/research_notes/lushness_testbed/c5_policy_search/SPECIFICATION.md']


def configure():
    engine.DOC = ROOT/'docs/research_notes/lushness_testbed/c5_policy_search'
    engine.LOCAL = ROOT/'results/local_runs/lushness_testbed/c5_policy_search'


def plan(smoke=False):
    import sys
    sys.path.insert(0, str(ROOT))
    from omega_v2.testbed.reactive_allocation import policies
    if smoke:
        return [{'id': 'engineering-paid-selector', 'parameters': {},
                 'controller': {'responses': ['productive', 'combined']},
                 'cadences': [.25], 'horizons': [16, 64, 256], 'subject_depth': 2}]
    return [{'id': p.id, 'parameters': {}, 'controller': {'responses': p.responses},
             'cadences': [.125, .25, .5], 'horizons': [16, 64, 256, 1024], 'subject_depth': 2}
            for p in policies()]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--budget', type=float, default=14400)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 2:
        raise ValueError('One or two capped workers')
    configure()
    raise SystemExit(engine.execute(plan(args.smoke), 'smoke' if args.smoke else 'survey',
        args.jobs, args.seconds, args.budget, worker='scripts/c5_policy_worker.py'))
