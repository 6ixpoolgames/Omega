"""Physical-history diagnostics of construction and subsequent use.

Bond episodes and pair IDs track material events, not preferred kinds of value.
Counters do not change the chemistry. None is a lushness extent.
"""

from omega_v2.finite.lattice_damage import event_from_record, state_from_record


def history_profile(model, trajectory, cuts):
    state = state_from_record(trajectory["initial"])
    # Each currently present episode: catalytically created? has served already?
    episodes = {pair: [False, False] for pair in state.bonds}
    seen_pairs = set(state.bonds)
    productive_pairs = set()
    reused_pairs = set()
    counts = {k: 0 for k in ("productive_products", "productive_initial_or_thermal",
                             "productive_products_later_lost", "reformations",
                             "new_material_pairs", "catalytic_formations")}
    area = {k: 0.0 for k in ("bond_time", "template_opportunity_time", "fuel_time")}
    cursor, time, output = 0, 0.0, []

    def advance(until):
        nonlocal time
        dt = until-time
        snap = model.snapshot(state)
        for key, prop in (("bond_time", "bonds"),
                          ("template_opportunity_time", "template_opportunities"),
                          ("fuel_time", "fuel")):
            area[key] += dt*snap[prop]
        time = until

    for cut in cuts:
        while cursor < len(trajectory["events"]) and trajectory["events"][cursor][0] <= cut:
            record = trajectory["events"][cursor]
            advance(record[0])
            event = event_from_record(record)
            if event.kind in ("thermal", "fuel", "catalytic"):
                pair = event.members
                if pair in state.bonds:
                    created, used = episodes.pop(pair)
                    counts["productive_products_later_lost"] += int(created and used)
                else:
                    counts["reformations"] += int(pair in seen_pairs)
                    counts["new_material_pairs"] += int(pair not in seen_pairs)
                    seen_pairs.add(pair)
                    if event.catalyst:
                        counts["catalytic_formations"] += 1
                        ancestor = episodes[event.catalyst]
                        productive_pairs.add(event.catalyst)
                        if ancestor[0]:
                            reused_pairs.add(event.catalyst)
                        if not ancestor[1]:
                            counts["productive_products" if ancestor[0]
                                   else "productive_initial_or_thermal"] += 1
                            ancestor[1] = True
                    episodes[pair] = [bool(event.catalyst), False]
            model.apply(state, event)
            cursor += 1
        advance(cut)
        events = model.events(state)
        formation_rates = {kind: sum(e.rate for e in events if e.kind == kind
                                     and e.members not in state.bonds)
                           for kind in ("thermal", "fuel", "catalytic")}
        output.append({"time": cut, **counts, **area,
                       "distinct_productive_pairs": len(productive_pairs),
                       "distinct_reused_product_pairs": len(reused_pairs),
                       "ever_product_reused": int(bool(reused_pairs)),
                       "live_productive_products": sum(a and b for a, b in episodes.values()),
                       **{k+"_formation_hazard": v for k, v in formation_rates.items()}})
    return output
