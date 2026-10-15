"""Validate receipts, immutable source snapshots and first-map score continuity."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
from report_domination_stage_a import load_status

DOC = ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'
OLD = ROOT/'docs/research_notes/lushness_testbed/domination_friction'


def main(allow_partial=False):
    status, loaded, configs = load_status()
    if not allow_partial and (status['status'] != 'complete' or len(loaded) != status['total']):
        raise RuntimeError('Complete batch required for final validation')
    signature = None
    for receipt in status['cases']:
        if receipt['status'] != 'complete':
            continue
        profile = receipt['profile']
        if (profile['exit_code'] or profile['cap_reason'] or
                profile['peak_job_bytes'] > profile['job_memory_cap_bytes'] or
                profile['wall_seconds'] > profile['wall_cap_seconds']+.5):
            raise RuntimeError('Worker cap or completion violation')
        manifest = verify_bundle(receipt['run'])
        if manifest['input_hash'] != profile['input_hash']:
            raise RuntimeError('Receipt source/configuration mismatch')
        current = [(r['path'], r['sha256']) for r in manifest['sources']]
        signature = current if signature is None else signature
        if current != signature:
            raise RuntimeError('Scientific batch used changing source versions')
        result = loaded[receipt['id']]
        source = (Path(receipt['run'])/'source').resolve()
        if not result['imports_from_snapshot'] or any(not Path(p).is_relative_to(source)
                            for p in result['imported_source_paths'].values()):
            raise RuntimeError('Worker imported mutable live sources')
    old_status = json.loads((OLD/'SURVEY_STATUS.json').read_text())
    old_receipts = {r['id']: r for r in old_status['cases']}
    suffixes = {'access_entry-blocking': 'access-block', 'access_entry-steering': 'access-steer',
        'construction_entry-blocking': 'construction-block', 'trap_entry-steering': 'trap-entry-steer',
        'trap_exit-steering': 'trap-exit-steer'}
    checked, largest = 0, 0.
    for name, case in configs.items():
        if case['slice'] != 'A5':
            continue
        p = case['parameters']
        old_name = f"s{p['supply']:g}-k{p['kappa']:g}-"+suffixes[case['target']+'-'+case['policy']['mode']]
        receipt = old_receipts[old_name]
        path = OLD/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['result_sha256']:
            raise RuntimeError('Original-map result hash mismatch')
        old = json.loads(path.read_text())
        for cadence, clock in loaded[name]['cadences'].items():
            for time, point in clock['profiles']['device_present'].items():
                prior = old['cadences'][cadence]['profiles']['device_present'][time]
                error = abs(point['global_bits']-prior['global_bits'])
                largest = max(error, largest)
                if error > 1e-7:
                    raise ArithmeticError('Extension changed an existing whole-history score')
                for s in ('D', 'S'):
                    a, b = point['subjects'][s], prior['subjects'][s]
                    if a['lower_bits'] < b['lower_bits']-1e-7 or a['upper_bits'] > b['upper_bits']+1e-7:
                        raise ArithmeticError('Tightened subject bounds widened original interval')
                checked += 1
    validation = {'status': 'verified' if status['status'] == 'complete' else 'partial_verified',
                  'cases': len(loaded), 'planned': status['total'], 'immutable_source_files': len(signature),
                  'original_map_comparisons': checked, 'max_original_global_score_difference': largest,
                  'all_original_subject_bounds_tightened_or_preserved': True,
                  'all_receipts_and_source_imports_verified': True,
                  'large_kernels_retained': False}
    atomic_json(DOC/'SOURCE_MANIFEST.json', {'source_hash': status['source_hash'],
                'sources': [{'path': path, 'sha256': digest} for path, digest in signature],
                'source_snapshots': 'retained locally under each receipt run/source path',
                'physical_source_in_repo': True})
    atomic_json(DOC/'VALIDATION.json', validation)
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main('--partial' in sys.argv)
