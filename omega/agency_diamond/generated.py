"""Generated held-out variants for the agency-diamond hardening pilot."""

from __future__ import annotations

import random
from dataclasses import dataclass, replace

from omega.agency_diamond.examples import MID_SCALE_HORIZONS, canonical_battery
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_system
from omega.agency_diamond.model import ControlledSystem


@dataclass(frozen=True)
class GeneratedVariantResult:
    variant_id: str
    base_system_id: str
    seed: int
    decoy_count: int
    profile_preserved: bool
    base_classifications: tuple[str, ...]
    variant_classifications: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "variant_id": self.variant_id,
            "base_system_id": self.base_system_id,
            "seed": self.seed,
            "decoy_count": self.decoy_count,
            "profile_preserved": self.profile_preserved,
            "base_classifications": list(self.base_classifications),
            "variant_classifications": list(self.variant_classifications),
        }


def generated_variants(*, seeds: tuple[int, ...] = (11, 17, 23)) -> tuple[ControlledSystem, ...]:
    variants = []
    for base in canonical_battery():
        for seed in seeds:
            variants.append(relabel_with_decoys(base, seed=seed))
    return tuple(variants)


def evaluate_generated_variants(
    *,
    seeds: tuple[int, ...] = (11, 17, 23),
) -> dict[str, object]:
    bases = {system.system_id: system for system in canonical_battery()}
    results: list[GeneratedVariantResult] = []
    generated_metrics: list[DiamondMetrics] = []

    for variant in generated_variants(seeds=seeds):
        base_id = variant.system_id.split("__seed", maxsplit=1)[0].removeprefix("generated__")
        base = bases[base_id]
        base_profile = tuple(
            evaluate_system(base, horizon=horizon).classification
            for horizon in MID_SCALE_HORIZONS
        )
        variant_profile = tuple(
            evaluate_system(variant, horizon=horizon).classification
            for horizon in MID_SCALE_HORIZONS
        )
        generated_metrics.extend(
            evaluate_system(
                variant,
                horizon=horizon,
                case_id=f"{variant.system_id}_h{horizon}",
            )
            for horizon in MID_SCALE_HORIZONS
        )
        results.append(
            GeneratedVariantResult(
                variant_id=variant.system_id,
                base_system_id=base.system_id,
                seed=int(variant.system_id.rsplit("__seed", maxsplit=1)[1].split("_", 1)[0]),
                decoy_count=sum(1 for state in variant.states if state.startswith("decoy__")),
                profile_preserved=base_profile == variant_profile,
                base_classifications=base_profile,
                variant_classifications=variant_profile,
            )
        )

    return {
        "variant_count": len(results),
        "case_count": len(generated_metrics),
        "all_profiles_preserved": all(result.profile_preserved for result in results),
        "results": [result.as_dict() for result in results],
    }


def relabel_with_decoys(system: ControlledSystem, *, seed: int) -> ControlledSystem:
    rng = random.Random(seed + sum(ord(ch) for ch in system.system_id))
    states = list(system.states)
    shuffled = states[:]
    rng.shuffle(shuffled)
    state_map = {
        state: f"s{index}__{state}"
        for index, state in enumerate(shuffled)
    }
    observations = list(system.observations)
    shuffled_obs = observations[:]
    rng.shuffle(shuffled_obs)
    obs_map = {
        obs: f"o{index}__{obs}"
        for index, obs in enumerate(shuffled_obs)
    }

    decoy_count = 1 + (seed % 2)
    decoy_states = tuple(f"decoy__{system.system_id}__{seed}__{index}" for index in range(decoy_count))
    decoy_observations = tuple(f"decoy_obs__{system.system_id}__{seed}__{index}" for index in range(decoy_count))

    renamed_states = tuple(state_map[state] for state in system.states) + decoy_states
    renamed_observations = tuple(obs_map[obs] for obs in system.observations) + decoy_observations
    transition = {}
    for scenario, by_state in system.transition.items():
        renamed_by_state = {}
        for state, by_action in by_state.items():
            renamed_by_state[state_map[state]] = {
                action: state_map[target]
                for action, target in by_action.items()
            }
        for decoy in decoy_states:
            renamed_by_state[decoy] = {action: decoy for action in system.actions}
        transition[scenario] = renamed_by_state

    observe = {
        state_map[state]: obs_map[obs]
        for state, obs in system.observe.items()
    }
    observe.update(
        {
            state: decoy_observations[index]
            for index, state in enumerate(decoy_states)
        }
    )
    live_policy = {
        obs_map[obs]: action
        for obs, action in system.live_policy.items()
    }
    live_policy.update({obs: system.actions[0] for obs in decoy_observations})

    return replace(
        system,
        system_id=f"generated__{system.system_id}__seed{seed}_d{decoy_count}",
        description=f"Generated relabel/decoy variant of {system.system_id}.",
        states=renamed_states,
        observations=renamed_observations,
        scenario_starts={
            scenario: state_map[state]
            for scenario, state in system.scenario_starts.items()
        },
        transition=transition,
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset(state_map[state] for state in system.target_states),
        viable_states=frozenset(state_map[state] for state in system.viable_states),
        channel_states=frozenset(state_map[state] for state in system.channel_states),
        joint_safe_states=(
            None
            if system.joint_safe_states is None
            else frozenset(state_map[state] for state in system.joint_safe_states)
        ),
    )
