"""Finite generator, projection and timed joint-law checks for local fuel."""

from dataclasses import asdict
from math import exp, factorial

import numpy as np
from scipy.sparse import bmat, coo_matrix, csr_matrix, diags
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.lattice_compartment import LocalState
from omega_v2.finite.lattice_history_atlas import canonical_state


def exact_generator(model, initial, max_states=20000):
    initial, _ = canonical_state(initial)
    states, index, channels = [initial], {initial.key(): 0}, []
    rows, columns, rates = [], [], []
    for i, state in enumerate(states):
        outgoing = []
        for e in model.events(state):
            after = state.copy()
            model.apply(after, e)
            after, mapping = canonical_state(after)
            key = after.key()
            if key not in index:
                if len(states) >= max_states:
                    raise RuntimeError("State limit reached: no truncated generator returned")
                index[key] = len(states)
                states.append(after)
            j = index[key]
            rows.append(i)
            columns.append(j)
            rates.append(e.rate)
            outgoing.append({"to": j, "event": asdict(e), "particle_map": mapping,
                             "forward_fuel": e.kind in ("fuel", "catalytic")
                             and e.members not in state.bonds})
        channels.append(outgoing)
    n = len(states)
    off = coo_matrix((rates, (rows, columns)), shape=(n, n)).tocsr()
    q = off-diags(np.asarray(off.sum(axis=1)).ravel())
    g = np.array([model.free_energy(s) for s in states])
    weights = np.exp(g.min()-g)
    pi = weights/weights.sum()
    return {"model": model, "states": states, "index": index, "channels": channels,
            "q": q.tocsr(), "pi": pi}


def diagnostics(exact):
    q, pi = exact["q"], exact["pi"]
    flux = q.multiply(pi[:, None])
    return {"states": len(pi), "channels": sum(map(len, exact["channels"])),
            "row_error": float(np.max(np.abs(np.asarray(q.sum(axis=1))))),
            "balance_error": float(np.max(np.abs((flux-flux.T).data), initial=0)),
            "stationary_error": float(np.max(np.abs(q.T@pi)))}


def lift_matrix(shared, local):
    """Conditional ideal allocation; columns indexed by shared-pool state."""
    model = local["model"]
    probabilities = np.array(model.volumes)/sum(model.volumes)
    rows, cols, weights = [], [], []
    for i, s in enumerate(local["states"]):
        key = s.project().key()
        j = shared["index"][key]
        weight = factorial(s.fuel)*factorial(model.p.capacity-s.fuel)
        for f, w, probability in zip(s.fuels, s.wastes, probabilities, strict=True):
            weight *= probability**(f+w)/(factorial(f)*factorial(w))
        rows.append(i)
        cols.append(j)
        weights.append(weight)
    shape = (len(local["states"]), len(shared["states"]))
    lift = coo_matrix((weights, (rows, cols)), shape=shape).tocsr()
    project = coo_matrix((np.ones(len(rows)), (cols, rows)), shape=shape[::-1]).tocsr()
    return lift, project


def propagate(q, initial, time):
    return expm_multiply(q.T*time, initial, traceA=float(q.diagonal().sum()*time))


def next_two_chemical_bindings(exact, horizon):
    """Next two non-reservoir-hop events bind using fuel, completed by T.

    Hops proceed natively between events; every other chemistry/move/switch
    event fails the query. The suffix after success is unrestricted.
    """
    q, channels = exact["q"], exact["channels"]
    n = q.shape[0]
    hr, hc, hv, fr, fc, fv = [], [], [], [], [], []
    for i, outgoing in enumerate(channels):
        for c in outgoing:
            if c["event"]["kind"] == "hop":
                hr.append(i)
                hc.append(c["to"])
                hv.append(c["event"]["rate"])
            if c["forward_fuel"]:
                fr.append(i)
                fc.append(c["to"])
                fv.append(c["event"]["rate"])
    hops = coo_matrix((hv, (hr, hc)), shape=(n, n)).tocsr()
    forward = coo_matrix((fv, (fr, fc)), shape=(n, n)).tocsr()
    inside = hops+diags(q.diagonal())
    # Backward equation, success value 1; failed flux leaves this subgenerator.
    augmented = bmat([[inside, forward, None],
                      [None, inside, csr_matrix(np.asarray(forward.sum(axis=1)))],
                      [csr_matrix((1, n)), csr_matrix((1, n)), csr_matrix((1, 1))]], format="csr")
    terminal = np.zeros(2*n+1)
    terminal[-1] = 1
    result = expm_multiply(augmented*horizon, terminal,
                          traceA=float(augmented.diagonal().sum()*horizon))
    return result[:n]


def channel_balance_error(exact):
    """Native route-level balance, including inverse transport allocation."""
    worst = 0.
    for i, outgoing in enumerate(exact["channels"]):
        state = exact["states"][i]
        for c in outgoing:
            e, j = c["event"], c["to"]
            mapping = c["particle_map"]
            target = dict(e)
            target["members"] = tuple(sorted(mapping[k] for k in e["members"]))
            target["catalyst"] = tuple(sorted(mapping[k] for k in e["catalyst"]))
            target["direction"] = tuple(-v for v in e["direction"])
            if e["kind"] == "hop":
                target["reservoir"] = e["reservoir"][::-1]
            candidates = [d for d in exact["channels"][j]
                          if d["to"] == i and all(d["event"][k] == v
                                                  for k, v in target.items() if k != "rate")]
            if len(candidates) != 1:
                raise AssertionError((i, e, candidates))
            reverse = candidates[0]["event"]["rate"]
            ratio = exp(exact["model"].free_energy(state)
                        - exact["model"].free_energy(exact["states"][j]))
            worst = max(worst, abs(e["rate"]/reverse/ratio-1))
    return worst


def shared_projection_key(state):
    projected = state.project() if isinstance(state, LocalState) else state
    return canonical_state(projected)[0].key()
