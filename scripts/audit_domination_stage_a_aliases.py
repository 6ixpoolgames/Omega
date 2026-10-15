"""Identify bookkeeping aliases and verify their native generators coincide."""
from collections import defaultdict
from dataclasses import asdict
import hashlib
import json

from report_domination_stage_a import DOC, load_status
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import FrictionParameters, FrictionPolicy, build_world
from omega_v2.testbed.workflow.manifest import atomic_json


def main():
    status, results, configs = load_status()
    groups = defaultdict(list)
    for name, case in configs.items():
        p, policy = FrictionParameters(**case['parameters']), FrictionPolicy(**case['policy'])
        parameters = {k: float(v) for k, v in asdict(p).items()}
        effective = None if policy.phi == 0 else {
            'mode': policy.mode, 'phi': policy.phi, 'cost': policy.cost,
            'edges': [(a, b) for a in range(4) for b in range(4)
                      if a != b and policy.targets(a, b)]}
        key = hashlib.sha256(json.dumps([parameters, effective], sort_keys=True).encode()).hexdigest()
        groups[key].append(name)
    aliases = []
    maximum_error = 0.
    for names in groups.values():
        if len(names) < 2:
            continue
        names.sort(key=lambda n: (configs[n]['slice'] == 'A3', n))
        representative = names[0]
        first = configs[representative]
        compiled = compile_world(build_world(FrictionParameters(**first['parameters']),
                                            FrictionPolicy(**first['policy'])))
        for name in names[1:]:
            other = configs[name]
            compared = compile_world(build_world(FrictionParameters(**other['parameters']),
                                                FrictionPolicy(**other['policy'])))
            difference = compiled['Q']-compared['Q']
            if max(abs(difference.data), default=0) > 1e-14:
                raise ArithmeticError('Declared physical alias changed the generator')
            for cadence, row in results[name]['cadences'].items():
                for time, point in row['profiles']['device_present'].items():
                    maximum_error = max(maximum_error, abs(point['global_bits']-
                        results[representative]['cadences'][cadence]['profiles']['device_present'][time]['global_bits']))
        aliases.append({'representative': representative, 'aliases': names[1:],
                        'native_generator_equality_verified': True})
    atomic_json(DOC/'ALIASES.json', {'status': status['status'], 'configurations': len(configs),
        'distinct_physical_generators': len(groups), 'groups': aliases,
        'max_alias_global_difference': maximum_error,
        'random_samples_retained': True, 'aliases_are_not_independent_replications': True})
    print(json.dumps({'configurations': len(configs), 'distinct_laws': len(groups),
                      'alias_groups': len(aliases), 'max_score_difference': maximum_error}))


if __name__ == '__main__':
    main()
