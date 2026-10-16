"""Frozen functional instantiation and W1/W2 verdicts; no objective repair."""
from math import isfinite

from ..analysis.observed_history import interval_comparison


def qualify(readouts, registration):
    mi = readouts['tracking_counterfactual_breadth_drop_mi_bits']
    drop = readouts['counterfactual_drop_probability_by_signal']
    shift = readouts['escape_disposition_shift']
    signal_time = readouts['signal_occupancy_time']
    fraction = readouts['signal_fraction_of_live_time']
    t = registration['tracking']
    disposition = (shift is not None and shift > registration['disposition_threshold']
                   and signal_time >= registration['minimum_signal_time']
                   and fraction is not None and fraction >= registration['minimum_signal_fraction'])
    direction = (all(value is not None for value in drop)
                 and drop[1] > drop[0]+t['direction_tolerance'])
    return {'tracking': bool(mi is not None and mi > t['mi_threshold_bits'] and direction),
            'nontracking': bool(mi is not None and mi <= t['mi_threshold_bits']/10),
            'disposition': bool(disposition), 'directional_tracking': bool(direction),
            'obstructed': bool(readouts['operational_obstructed_suffering_index']
                               >= registration['minimum_obstructed_index']),
            'tracking_mi_bits': mi}


def compare_intervals(worse, better, tolerance):
    """Compare all arms to a max comparator without choosing it post hoc."""
    if not better:
        raise ValueError('Comparator arms required')
    max_better = {'lower_bits': max(x['lower_bits'] for x in better),
                  'upper_bits': max(x['upper_bits'] for x in better)}
    return interval_comparison(worse, max_better, tolerance)


def local_verdict(comparison, instantiates):
    if not instantiates:
        return 'not_instantiated'
    if comparison['verdict'] == 'strict_positive':
        return 'adapter_relative_ranking_counterexample'
    if comparison['verdict'] == 'compression_within_tolerance':
        return 'compression_failure'
    if comparison['verdict'] == 'strict_negative':
        return 'adversary_loses'
    return 'unresolved'


def limiting_order(worse, better, rate_tolerance, offset_tolerance):
    """Asymptotic diagnostic, never substituted for finite lushness."""
    if not all(isfinite(x) for row in [worse, *better] for x in row):
        raise ValueError('Finite rates and offsets required')
    highest_rate = max(x[0] for x in better)
    rate_difference = worse[0]-highest_rate
    if rate_difference > rate_tolerance:
        return 'strict_positive'
    if rate_difference < -rate_tolerance:
        return 'strict_negative'
    compatible = [x[1] for x in better if abs(x[0]-highest_rate) <= rate_tolerance]
    offset_difference = worse[1]-max(compatible)
    if offset_difference > offset_tolerance:
        return 'strict_positive'
    if offset_difference < -offset_tolerance:
        return 'strict_negative'
    return 'compression_within_tolerance'
