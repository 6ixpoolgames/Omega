"""Fixed-controller engineering smoke for richer spectator observations."""
from __future__ import annotations

import hashlib
import time
import numpy as np
from scipy.sparse.linalg import expm_multiply

from ..controllers.reserve import ReservePolicy, candidate_family
from ..compiler import compile_world
from ..modules.growth import build_world
from ..modules.actuation import ActuationSpec
from ..modules.material_sink import MaterialSink
from ..modules.shocks import ShockSpec
from ..analysis.finite_classes import analyze, reachable_indices
from ..analysis.channel_access import closure_mask, closure_certificate, first_passage
from .channel_comparison import root_for, flux_survey, time_key


def fingerprint(model):
    q = model['Q']
    return hashlib.sha256(q.indptr.tobytes()+q.indices.tobytes()+q.data.tobytes()+
        b''.join(k.encode()+model['flows'][k].tobytes() for k in sorted(model['flows']))).hexdigest()


def engineering(config, progress=lambda value: None):
    inv = tuple(config['inventory'])
    controller = ReservePolicy(**config['fixed_controller'])
    actuator = ActuationSpec('embodied', .003)
    sink = MaterialSink(mode='reversible', rate=.04, energy=-1, exposure=(0.,1.,0.))
    shocks = ShockSpec(**config['shocks'])
    start = time.perf_counter()
    model = compile_world(build_world(inv, controller, damage=sink,
                                     actuation=actuator, shocks=shocks))
    build_seconds = time.perf_counter()-start
    n = len(model['states']); q = model['Q']
    root = root_for(inv); initial = np.zeros(n); initial[model['index'][root]] = 1
    progress({'phase':'fixed-controller entropy analysis','states':n})
    start = time.perf_counter()
    result = analyze(q, config['cadence'], config['max_dense_bytes'])
    analysis_seconds = time.perf_counter()-start
    horizons = config['horizons']; delta = config['cadence']
    steps = {int(round(t/delta)):t for t in horizons}
    if any(abs(t/delta-round(t/delta)) > 1e-10 for t in horizons):
        raise ValueError('Physical horizons must align to declared cadence')
    # Exercise the complete-horizon recurrence without publishing scientific scores.
    total = np.zeros(n); previous = -1.; finite_checks = {}
    start = time.perf_counter()
    for step in range(1, max(steps)+1):
        total = result['row_entropy'] + result['P'] @ total
        if step in steps:
            value = float(initial@total)
            if not np.isfinite(value) or value < previous-1e-9:
                raise ArithmeticError('History entropy must be finite and nondecreasing')
            previous = value
            finite_checks[time_key(steps[step])] = 'finite and nondecreasing'
    history_seconds = time.perf_counter()-start
    # Do not retain dense propagation vectors in public output.
    start = time.perf_counter()
    physical = compile_world(build_world(inv, ReservePolicy('all-actions', surplus='mix50'),
                                        damage=sink, actuation=actuator, shocks=shocks))
    active = model['observables']['active'] > 0
    closed = closure_mask(physical['Q'], active)
    cert = closure_certificate(q, closed)
    if not cert['closed']:
        raise ArithmeticError('Structural closure must be closed under a policy')
    deadline = config['common_deadline']
    hit = first_passage(q, model['index'][root], closed, deadline)
    flux = flux_survey(model, initial, deadline)
    endpoint = expm_multiply(q.T*deadline, initial)
    if abs(endpoint.sum()-1) > 1e-9 or min(endpoint) < -1e-12:
        raise ArithmeticError('Endpoint distribution failed normalization')
    query_seconds = time.perf_counter()-start
    progress({'phase':'controller coverage, no optimization'})
    # Enumerate physical aliases without entropy evaluation or policy rankings.
    start = time.perf_counter(); family = candidate_family(3); aliases = {}; rows=[]
    for p in family:
        candidate = compile_world(build_world(inv,p,damage=sink,actuation=actuator,shocks=shocks))
        key = fingerprint(candidate)
        alias = aliases.setdefault(key, p.id)
        keep = reachable_indices(candidate['Q'], [candidate['index'][root]])
        witness = {}
        for c in (0,1):
            feasible = {p.response(candidate['states'][i][c]) for i in keep
                        if candidate['states'][i][c][1] > 0}
            witness[str(c)] = {'distinct_positive_reach_responses':len(feasible),
                               'responses':[list(x) for x in sorted(feasible)]}
        rows.append({'policy':p.manifest(), 'audit_surfaces':[p.audit_vector(m) for m in inv],
                     'kernel_ledger_hash':key,'canonical_id':alias,'support_witness':witness})
        del candidate
    coverage_seconds = time.perf_counter()-start
    return {'status':'engineering_smoke_pass','scope':'one fixed controller; no ranking or scientific predictions scored',
            'inventory':inv,'states':n,'controller':controller.manifest(),
            'candidate_count':len(rows),'unique_kernel_ledger_models':len(aliases),'candidates':rows,
            'timings':{'build':build_seconds,'analysis':analysis_seconds,'history':history_seconds,
                       'queries':query_seconds,'coverage':coverage_seconds},
            'dense_analysis_estimate_bytes':result['dense_bytes_estimate'],
            'numerical_residuals':result['residuals'],
            'history_checks':finite_checks,'endpoint_mass_error':float(abs(endpoint.sum()-1)),
            'closure_certificate':cert,'deadline_query_status':'evaluated',
            'accounting_residuals':{'energy':flux['energy_residual'],'population':flux['population_residual']},
            'scientific_scores_withheld':True,'closure_query_finite':bool(np.isfinite(hit['hit_probability']))}
