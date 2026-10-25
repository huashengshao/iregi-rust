"""Independent paired statistics for a saved, admitted, released timing corpus.

Importing this module does no work. Callers own terminal/hash/cohort admission
and must wait for the root quiet-lease release before calling either summary.
No producer module is imported. Values are already per-call times; pairing is
preserved by index. This module never launches a process or reads a timing file.
"""
from __future__ import annotations

import math
import random
import statistics
from typing import Iterable, Sequence

SEED = 173
RESAMPLES = 10_000
QUARTETS = 48
RELATIVE_WIDTH_MAXIMUM = 0.02


def quantile(values: Sequence[float], fraction: float) -> float:
    """Linear interpolation at fraction*(N-1), matching historical semantics."""
    if not values or not 0 <= fraction <= 1:
        raise ValueError('A quantile requires values and a fraction in[0,1].')
    ordered = sorted(values)
    location = fraction * (len(ordered) - 1)
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - location) + ordered[upper] * (location - lower)


def _bootstrap_medians(values: Sequence[float], *, seed: int = SEED,
                       resamples: int = RESAMPLES) -> list[float]:
    """Resample the paired-ratio observations, resetting seed for each summary."""
    generator = random.Random(seed)
    return [statistics.median(generator.choices(values, k=len(values)))
            for _ in range(resamples)]


def _paired(left: Iterable[float], right: Iterable[float]) -> tuple[list, list]:
    left = list(left); right = list(right)
    if len(left) != len(right):
        raise ValueError('Paired sample counts must agree exactly.')
    for values in (left, right):
        if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0
               for value in values):
            raise ValueError('Every latency must be finite and strictly positive.')
    return left, right


def _historical_gate(median: float, low: float, high: float,
                     admitted: bool) -> tuple[str, float]:
    width = (high - low) / median
    narrow = width <= RELATIVE_WIDTH_MAXIMUM
    if not admitted:
        gate = 'correctness-failed'
    elif narrow and high < 1:
        gate = 'improvement'
    elif narrow and low <= 1 <= high:
        gate = 'parity'
    elif narrow and low > 1:
        gate = 'regression'
    else:
        gate = 'inconclusive-noise'
    return gate, width


def summarize(left: Iterable[float], right: Iterable[float], admitted: bool = True,
              short: bool = False) -> dict | None:
    """Median paired ratios and historical99% bootstrap interval.

    The generic function supports either a48sample family or a24sample order
    stratum. No nonempty input is silently truncated. `historical_gate` is the
    nested historical result; `gate` applies the producer's outer cohort/short
    policy. Every ratio has TIRust latency in the numerator supplied as `left`.
    An empty pair of sequences returns None without invoking the bootstrap.
    """
    if type(admitted) is not bool or type(short) is not bool:
        raise ValueError('Admission and short flags must be boolean.')
    left, right = _paired(left, right)
    if not left:
        return None
    ratios = [numerator / denominator for numerator, denominator in zip(left, right)]
    if not all(math.isfinite(value) and value > 0 for value in ratios):
        raise ValueError('Every paired ratio must remain finite and positive.')
    median = statistics.median(ratios)
    bootstrap = _bootstrap_medians(ratios)
    low = quantile(bootstrap, .005)
    high = quantile(bootstrap, .995)
    historical, width = _historical_gate(median, low, high, admitted and not short)
    gate = (historical if admitted and not short else
            'inconclusive-short-block' if admitted and short else
            'correctness-or-cohort-failed')
    return {'samples': ratios, 'median': median, 'ci99': [low, high],
            'relative_ci_width': width, 'gate': gate,
            'historical_gate': historical,
            'slower_pairs': sum(a > b for a, b in zip(left, right))}


def summarize_stratified(left: Iterable[float], right: Iterable[float],
                         numerator_first: Iterable[bool], admitted: bool = True,
                         short: bool = False) -> dict:
    """Full48paired summary and the24/24process-order strata.

    `numerator_first[i]` must indicate the actual quartet's process order. The
    caller must derive it from saved raw evidence, not sort timings by value.
    Incomplete families remain visible and do not invoke any bootstrap.
    """
    left, right = _paired(left, right)
    flags = list(numerator_first)
    if len(flags) != len(left) or any(type(value) is not bool for value in flags):
        raise ValueError('One boolean process-order indicator is required per pair.')
    if len(left) != QUARTETS:
        return {'samples': [a / b for a, b in zip(left, right)],
                'median': None, 'ci99': None, 'relative_ci_width': None,
                'gate': 'inconclusive-incomplete-family', 'historical_gate': None,
                'slower_pairs': sum(a > b for a, b in zip(left, right)),
                'order_strata': None}
    if sum(flags) != QUARTETS // 2:
        raise ValueError('The complete family must have exactly24/24order strata.')
    result = summarize(left, right, admitted=admitted, short=short)
    result['order_strata'] = {}
    for first, name in [(True, 'numerator_first'), (False, 'denominator_first')]:
        indices = [i for i, flag in enumerate(flags) if flag is first]
        result['order_strata'][name] = summarize([left[i] for i in indices],
                                                [right[i] for i in indices],
                                                admitted=admitted, short=short)
    return result
