"""Independent labelled-body generator for the finite growing-population model.

This deliberately does not call ``growing_population.events``.  Bodies are
labelled sites; fuel remains a pooled count and is not assigned extra labels.
The labelled states are audit coordinates, not additional primary entropy.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb, exp

import numpy as np
from scipy.sparse import coo_matrix


@dataclass(frozen=True)
class ReferenceParams:
    capture: float = .04
    capture_benefit: float = 6.
    chemical_potential: float = 4.
    fuel_bath: float = .04
    build: float = .3
    repair: float = .5
    wear: float = .04
    disassembly: float = .08
    assisted_birth: float = .4
    switch: float = .15
    switch_tokens: int = 1
    exchange: float = .4


DEFAULT_PARAMS = ReferenceParams()


def _inventory(inv):
    if type(inv) is int:
        inv = (inv, inv)
    inv = tuple(inv)
    if len(inv) != 2 or any(type(m) is not int or m < 1 for m in inv):
        raise ValueError('inventory must be a positive integer or pair of positive integers')
    return inv


def _weights(policy):
    if policy is None:
        return ((0., 0.),) * 4
    if len(policy) != 4:
        raise ValueError('policy needs four compartment × active-status entries')
    out = []
    for response in policy:
        if isinstance(response, (int, float)):
            p = float(response)
            if not 0 <= p <= 1:
                raise ValueError('scalar response must be in [0,1]')
            pair = (1-p, p)
        else:
            pair = tuple(map(float, response))
            if len(pair) != 2 or min(pair) < 0 or sum(pair) > 1 + 1e-12:
                raise ValueError('response weights must be a valid service/export pair')
        out.append(pair)
    return tuple(out)


def _state_space(inv):
    locals_ = [tuple((body, f, g) for body in product(range(3), repeat=m)
                     for f in range(m+1) for g in range(2)) for m in inv]
    return tuple(product(*locals_))


def _energy(state):
    return sum(sum(site == 1 for site in body) + 2*sum(site == 2 for site in body) + 2*f
               for body, f, g in state)


def _coarse(state, inv):
    return tuple((sum(x == 1 for x in body), sum(x == 2 for x in body), f, g)
                 for (body, f, g) in state)


def assisted_events(state,inv,params=DEFAULT_PARAMS,compartment=None):
    """Actual ordered parent/recipient routes, without persistent ancestry IDs."""
    inv=_inventory(inv);result=[]
    for c in (range(2) if compartment is None else (compartment,)):
        body,f,gate=state[c];m=inv[c]
        if gate!=0:continue
        for parent,ptype in enumerate(body):
            if ptype!=2:continue
            for recipient,rtype in enumerate(body):
                if parent==recipient:continue
                if rtype==0 and f:kind,df,rate=2,-1,params.assisted_birth*f/(m*m)
                elif rtype==2 and f<m:kind,df,rate=0,1,params.assisted_birth*(m-f)/(m*m)
                else:continue
                changed=list(body);changed[recipient]=kind
                target=list(state);target[c]=(tuple(changed),f+df,gate)
                result.append({'source':state,'target':tuple(target),'compartment':c,'parent':parent,
                               'recipient':recipient,'rate':rate})
    return result


def build_reference(inv=1, policy=None, params=DEFAULT_PARAMS, max_states=1000):
    """Return labelled states, row generator, histogram map and event ledger."""
    inv = _inventory(inv)
    expected=np.prod([3**m*(m+1)*2 for m in inv])
    if expected>max_states:raise RuntimeError('Labelled reference cap; law was not truncated')
    weights = _weights(policy)
    states = _state_space(inv)
    index = {s: i for i, s in enumerate(states)}
    rows, cols, data = [], [], []
    ledger = []

    def emit(i, src, dst, family, rate, work=0.):
        if rate <= 0:
            return
        j = index[tuple(dst)]
        rows.append(i); cols.append(j); data.append(float(rate))
        ledger.append({'source': src, 'target': tuple(dst), 'family': family,
                       'rate': float(rate), 'work': float(work),
                       'energy_change': _energy(dst)-_energy(src)})

    for i, state in enumerate(states):
        for c, (body, f, g) in enumerate(state):
            m = inv[c]
            active = body.count(2)
            lam = params.capture*(1+(params.capture_benefit-1)*active/m)
            up_drive = lam*(m-f)*exp((params.chemical_potential-2)/2)
            dn_drive = lam*f*exp(-(params.chemical_potential-2)/2)
            up_bath = params.fuel_bath*(m-f)*exp(-1)
            dn_bath = params.fuel_bath*f*exp(1)
            for family, up, down, work in (
                ('drive_charge', up_drive, dn_drive, params.chemical_potential),
                ('bath_charge', up_bath, dn_bath, 0.),
            ):
                for rate, df, w in ((up, 1, work), (down, -1, -work)):
                    if rate:
                        dst = list(state); dst[c] = (body, f+df, g)
                        emit(i, state, dst, family, rate, w)

            # Native conversion and its separate wear/disassembly pathways.
            for site, kind in enumerate(body):
                transitions = []
                if kind == 0:
                    transitions.append((1, 'disassembly', params.disassembly*exp(-.5), 0.))
                elif kind == 1:
                    transitions += [(0, 'disassembly', params.disassembly*exp(.5), 0.),
                                    (2, 'wear', params.wear*exp(-.5), 0.)]
                else:
                    transitions.append((1, 'wear', params.wear*exp(.5), 0.))
                for new_kind, family, rate, work in transitions:
                    changed = list(body); changed[site] = new_kind
                    dst = list(state); dst[c] = (tuple(changed), f, g)
                    emit(i, state, dst, family, rate, work)

            # Local basal construction and repair; each target site is explicit.
            if g == 0:
                for site, kind in enumerate(body):
                    if kind == 0 and f:
                        changed = list(body); changed[site] = 2
                        dst = list(state); dst[c] = (tuple(changed), f-1, g)
                        emit(i, state, dst, 'basal_build', params.build*f/m)
                    elif kind == 2 and f < m:
                        changed = list(body); changed[site] = 0
                        dst = list(state); dst[c] = (tuple(changed), f+1, g)
                        emit(i, state, dst, 'basal_build', params.build*(m-f)/m)
                    if kind == 1 and f:
                        changed = list(body); changed[site] = 2
                        dst = list(state); dst[c] = (tuple(changed), f-1, g)
                        emit(i, state, dst, 'repair', params.repair*f/m*exp(.5))
                    if kind == 2 and f < m:
                        changed = list(body); changed[site] = 1
                        dst = list(state); dst[c] = (tuple(changed), f+1, g)
                        emit(i, state, dst, 'repair', params.repair*(m-f)/m*exp(-.5))

                for ev in assisted_events(state,inv,params,compartment=c):
                    emit(i,state,ev['target'],'assisted_birth',ev['rate'])

            # Gate switches preserve the body tuple; switch tokens are pooled
            # fuel carriers and use the same policy entry in both directions.
            token = getattr(params, 'switch_tokens', getattr(params, 'token_bill', 1))
            if m >= token:
                service, export = weights[2*c + int(active > 0)]
                for k, weight, family in ((token, service, 'switch_service'),
                                          (token, export, 'switch_export')):
                    if not weight or k > m:
                        continue
                    denom = comb(m, k)
                    source_gate = 1 if family == 'switch_service' else 0
                    if g == source_gate and f >= k:
                        dst = list(state); dst[c] = (body, f-k, 1-g)
                        emit(i, state, dst, family,
                             params.switch*weight*comb(f, k)/denom*exp(k))
                    elif g == 1-source_gate and f+k <= m:
                        dst = list(state); dst[c] = (body, f+k, 1-g)
                        emit(i, state, dst, family,
                             params.switch*weight*comb(m-f, k)/denom*exp(-k))

        # Each open endpoint is a distinct exchange pathway; both directions
        # are emitted under that endpoint's unchanged gate state.
        for c in range(2):
            other = 1-c
            bc, fc, gc = state[c]; bo, fo, go = state[other]
            if not gc:
                continue
            kc, ko = inv[c], inv[other]
            if fc and fo < ko:
                dst = list(state); dst[c] = (bc, fc-1, gc); dst[other] = (bo, fo+1, go)
                emit(i, state, dst, 'exchange', params.exchange*(fc/kc)*((ko-fo)/ko))
            if fo and fc < kc:
                dst = list(state); dst[c] = (bc, fc+1, gc); dst[other] = (bo, fo-1, go)
                emit(i, state, dst, 'exchange', params.exchange*(fo/ko)*((kc-fc)/kc))

    # Aggregate parallel labelled channels, then complete each row diagonal.
    n = len(states)
    q = coo_matrix((np.asarray(data), (np.asarray(rows), np.asarray(cols))), shape=(n, n)).tocsr()
    q.sum_duplicates()
    q.setdiag(0); q.eliminate_zeros()
    q.setdiag(-np.asarray(q.sum(axis=1)).ravel())
    coarse = tuple(_coarse(s, inv) for s in states)
    unique = tuple(dict.fromkeys(coarse))
    hist_index = {s: j for j, s in enumerate(unique)}
    return {'states': states, 'index': index, 'Q': q, 'histograms': unique,
            'histogram_index': hist_index, 'projection': np.asarray([hist_index[x] for x in coarse]),
            'events': tuple(ledger), 'inventory': inv, 'params': params}


def project_to_histogram(reference):
    """Return the indicator matrix R for exact generator test Q_f R = R Q_c."""
    n = len(reference['states']); h = len(reference['histograms'])
    r = coo_matrix((np.ones(n), (np.arange(n), reference['projection'])), shape=(n, h)).tocsr()
    return r
