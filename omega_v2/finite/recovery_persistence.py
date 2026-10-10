"""Permanent membership in a declared safe set of a finite fixed-policy chain."""

from omega_v2.finite.recovery_dynamics import Chain, hitting_analysis


def permanent_membership(chain: Chain, safe: frozenset):
    """Find the greatest closed safe set and its eventual hitting probability.

    In a finite chain, eventual perpetual safety agrees almost surely with
    hitting this set. It need not agree with being safe now or hitting once.
    """
    if not safe <= set(chain.states):
        raise ValueError("unknown safe state")
    closed = set(safe)
    removed_layers = []
    while True:
        removed = {s for s in closed if any(t not in closed for t in chain.transition(s).support)}
        if not removed:
            break
        removed_layers.append(frozenset(removed))
        closed.difference_update(removed)
    target = frozenset(closed)
    return {"safe": safe, "closed_safe": target, "removed_layers": tuple(removed_layers),
            "hitting": hitting_analysis(chain, target)}
