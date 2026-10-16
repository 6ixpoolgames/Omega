"""Public development controls, generated workshops, and visible evaluations."""

from dataclasses import replace
from fractions import Fraction
from random import Random

from omega_v2.finite.joint_requirements import Action, World, digest, world_data

F = Fraction
PROTOCOL = "docs/research_notes/omega_v2/lushness_decision_protocol_v0.md"


def workshop(name, seed=0, budget=(4, 3, 3), permissions=(1, 1, 1), history=(1, 1, 0),
             costs=((1, 1, 1), (1, 1, 1), (1, 1, 1)), prerequisites=(0, 0, 1), menu=None):
    rng = Random(seed)
    sampled = tuple(tuple(sorted(rng.sample((1, 2, 4), 2))) for _a in range(2))
    actions = (
        Action("idle", (1, 0, 0), permissions),
        Action("work", (1, 1, 1), permissions, F(1)),
        Action("workshop", (1, 1, 1), (7, 7, 7), F(1, 2)),
        Action("decoration", (1, 1, 1), permissions, F(1, 2), display=True),
        Action("seize", (1, 0, 0), (7, 0, 0), F(1), source="selected", records=True, consenting=(0,)),
        Action("rewrite", (1, 0, 0), (permissions[0], 0, permissions[2]), F(1),
               source="external", revisions=((1, 0),)),
        Action("commit", (1, 0, 0), (permissions[0], 1, permissions[2]), F(1, 2),
               source="selected", records=True, consenting=(1,), revisions=((1, 1),)),
        Action("capture", (1, 0, 0), (permissions[0], 1, permissions[2]), F(1, 2),
               source="external", revisions=((1, 1),)),
        Action("unstable_work", (1, 1, 1), permissions, F(3, 2), correction=(F(1), F(0), F(1), F(0))),
        Action("hazardous_work", (1, 1, 1), permissions, F(3, 2), correction=(F(1), F(0), F(1), F(1, 4))),
    )
    if menu:
        actions = tuple(a for a in actions if a.name in menu)
    return World(name, budget, costs, prerequisites, permissions, history, sampled, seed, actions)


def public_worlds():
    worlds = [
        workshop("workshop", menu=("idle", "work", "workshop", "decoration")),
        workshop("domination", permissions=(1, 7, 7), menu=("idle", "work", "workshop", "seize")),
        workshop("corridor", permissions=(7, 7, 7), menu=("idle", "work", "unstable_work", "hazardous_work")),
        workshop("rewrite", budget=(3, 1, 3), permissions=(1, 3, 1), history=(1, 2, 0),
                 menu=("idle", "work", "rewrite")),
        workshop("commitment", permissions=(1, 7, 7), history=(1, 2, 0), menu=("idle", "commit", "capture")),
        workshop("scarcity", budget=(3, 1, 2), menu=("idle", "work")),
    ]
    commitment = worlds[4]
    selected = commitment.action("commit")
    worlds[4] = replace(commitment, actions=commitment.actions + (
        replace(selected, name="selected_without_records", records=False),
        replace(selected, name="selected_under_coercion", coerced=True),
    ))
    for seed in range(12):
        rng = Random(seed + 20260929)
        worlds.append(workshop(f"generated_{seed:02d}", seed=seed,
            budget=(rng.randint(3, 5), rng.randint(1, 4), rng.randint(2, 5)),
            permissions=tuple(rng.randint(1, 7) for _a in range(3)),
            costs=tuple((1, rng.randint(1, 2), rng.randint(0, 1)) for _p in range(3)),
            prerequisites=(0, rng.choice((0, 1)), rng.choice((0, 1, 2)))))
    return tuple(worlds)


def public_evaluation(worlds):
    """Visible author-designed probes, never labelled an independent holdout."""
    criteria = {str(a): ["unconsented_loss", "external_rewrite", "irreversible_harm",
                         "permanent_failure", "race_failure"] for a in range(3)}
    result = {}
    for world in worlds:
        requests = (("history", "incumbent", world.history, "history"),
                    ("revision", "revised", (2, 4, 0), "new"),
                    ("arrival", "newcomer", (0, 1, 2), "new"),
                    ("conflict", "scarce_bundle", (5, 6, 0), "new"))
        result[world.name] = {"world_digest": digest(world_data(world)), "harm_criteria": criteria,
            "bundles": [{"id": name, "stratum": stratum, "request": list(request), "weight": "1/4", "frame": frame}
                        for name, stratum, request, frame in requests]}
    return {"schema": "joint-evaluation-v0", "status": "public_development", "worlds": result}
