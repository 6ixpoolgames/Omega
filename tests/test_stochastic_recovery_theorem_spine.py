from fractions import Fraction

from omega.adapters.finite_relational import (
    all_deterministic_decoders,
    compose_coarse_decoder_through_fine,
    optimized_worst_case_decoder,
    success_by_source,
    support_exact_recoverable,
    worst_case_success,
)


def _tiny_channels() -> tuple[dict[str, dict[str, Fraction]], ...]:
    rows = (
        {"y0": Fraction(1), "y1": Fraction(0)},
        {"y0": Fraction(1, 2), "y1": Fraction(1, 2)},
        {"y0": Fraction(0), "y1": Fraction(1)},
    )
    return tuple(
        {"x0": left, "x1": right}
        for left in rows
        for right in rows
    )


def test_support_exact_recovery_implies_optimized_worst_case_one() -> None:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    observation = {"y0": "left", "y1": "right"}
    target = {"x0": "false", "x1": "true"}

    for channel in _tiny_channels():
        if support_exact_recoverable(states, outputs, channel, observation, target):
            result = optimized_worst_case_decoder(states, outputs, channel, observation, target)
            assert result.worst_case_success == Fraction(1)


def test_declared_decoder_success_is_bounded_by_optimized_decoder_success() -> None:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    observation = {"y0": "left", "y1": "right"}
    target = {"x0": "false", "x1": "true"}
    decoders = all_deterministic_decoders(("left", "right"), ("false", "true"))

    for channel in _tiny_channels():
        optimized = optimized_worst_case_decoder(states, outputs, channel, observation, target)
        for decoder in decoders:
            declared_success = success_by_source(states, outputs, channel, observation, target, decoder)
            assert worst_case_success(declared_success) <= optimized.worst_case_success


def test_coarse_decoder_can_be_simulated_by_fine_decoder_when_coarse_factors_through_fine() -> None:
    states = ("x0", "x1")
    outputs = ("a0", "a1", "b0", "b1")
    channel = {
        "x0": {
            "a0": Fraction(1, 2),
            "a1": Fraction(1, 2),
            "b0": Fraction(0),
            "b1": Fraction(0),
        },
        "x1": {
            "a0": Fraction(0),
            "a1": Fraction(0),
            "b0": Fraction(1, 2),
            "b1": Fraction(1, 2),
        },
    }
    fine = {"a0": "a0", "a1": "a1", "b0": "b0", "b1": "b1"}
    coarse = {"a0": "a", "a1": "a", "b0": "b", "b1": "b"}
    target = {"x0": "false", "x1": "true"}
    coarse_decoder = {"a": "false", "b": "true"}

    fine_decoder = compose_coarse_decoder_through_fine(
        outputs,
        fine,
        coarse,
        coarse_decoder,
    )

    assert success_by_source(states, outputs, channel, coarse, target, coarse_decoder) == (
        success_by_source(states, outputs, channel, fine, target, fine_decoder)
    )
