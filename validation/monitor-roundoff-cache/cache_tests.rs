// Spliced into the candidate stability.rs tests module by the experiment builder.
// These tests use the original uncached implementation as the numerical oracle.

fn cache_repeated_monitor() -> StabilityPlan {
    let mut monitor = synthetic(0, false);
    let mut repeated = monitor.checks[0].clone();
    repeated.label = "repeated contribution check".into();
    monitor.checks.push(repeated);
    monitor
}

fn cache_assert_same_estimate<T: NativeFloat>(actual: &T, expected: &T) {
    assert!(
        actual == expected,
        "cached estimate changed the represented value"
    );
    assert_eq!(actual.get_precision(), expected.get_precision());
    assert_eq!(actual.negative_sign(), expected.negative_sign());
}

fn cache_assert_roundoff_lane<T: NativeFloat>(
    cache: &mut MonitorEstimateCache<T>,
    prototype: &T,
    value: &Complex<T>,
) {
    cache.begin_lane();
    let expected = OperandRoundoff::new(prototype).complex(value);
    let mut roundoff = OperandRoundoff::new(prototype);
    for _ in 0..2 {
        match (&expected, cache.estimate(1, 0, &mut roundoff, value)) {
            (Ok(expected), Ok(actual)) => cache_assert_same_estimate(&actual, expected),
            (Err(expected), Err(actual)) => {
                assert_eq!(actual, *expected);
                let slot = cache.slots[1] * cache.components;
                assert_ne!(cache.generations[slot], cache.generation);
            }
            _ => panic!("cached and uncached roundoff success/failure differ"),
        }
    }
}

#[test]
fn monitor_estimate_cache_hits_preserve_float_precision_and_return_independent_values() {
    let monitor = cache_repeated_monitor();
    let prototype = Float::new(256);
    let value = Complex::new(Float::with_val(80, 3), Float::with_val(53, 4));
    let expected = OperandRoundoff::new(&prototype).complex(&value).unwrap();
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    let mut roundoff = OperandRoundoff::new(&prototype);
    cache.begin_lane();

    let mut first = cache.estimate(1, 0, &mut roundoff, &value).unwrap();
    cache_assert_same_estimate(&first, &expected);
    first.set_prec(32);
    first *= Float::with_val(32, 2);
    assert!(first != expected);
    let mut hit = cache.estimate(1, 0, &mut roundoff, &value).unwrap();
    cache_assert_same_estimate(&hit, &expected);
    hit.set_prec(12);
    hit *= Float::with_val(12, 4);
    let later_hit = cache.estimate(1, 0, &mut roundoff, &value).unwrap();
    cache_assert_same_estimate(&later_hit, &expected);
}

#[test]
fn monitor_estimate_cache_preserves_mixed_and_low_precision_roundoff_paths() {
    let monitor = cache_repeated_monitor();
    let prototype = Float::new(256);
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    let mut tiny_low_precision = Float::with_val(256, 2).pow(200).inv();
    tiny_low_precision.set_prec(1);
    let values = [
        Complex::new(Float::with_val(256, 1), Float::new(1)),
        Complex::new(
            Float::with_val(256, 1),
            Float::with_val(80, 2).pow(300).inv(),
        ),
        complex(tiny_low_precision),
        complex(Float::with_val(1, 1)),
        Complex::new(Float::new(1), Float::new(1)),
        Complex::new(Float::with_val(80, f64::INFINITY), Float::new(1)),
    ];
    for value in &values {
        cache_assert_roundoff_lane(&mut cache, &prototype, value);
    }
}

#[test]
fn monitor_estimate_cache_preserves_subnormal_signed_zero_and_error_paths() {
    let monitor = cache_repeated_monitor();
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    for value in [
        complex(f64::from_bits(1)),
        Complex::new(-f64::from_bits(1), f64::from_bits(2)),
        Complex::new(-0.0, 0.0),
        Complex::new(0.0, -0.0),
        Complex::new(f64::MAX, f64::MAX),
        Complex::new(f64::NAN, 0.0),
        Complex::new(0.0, f64::INFINITY),
    ] {
        cache_assert_roundoff_lane(&mut cache, &0.0, &value);
    }

    // A normal high limb does not give DoubleFloat's low limb enough exponent
    // range for its nominal precision; preserve the existing fallback result.
    let prototype = iregi_masters::DoubleFloat::from(0.0);
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    for value in [
        complex(iregi_masters::DoubleFloat::from(f64::MIN_POSITIVE)),
        complex(iregi_masters::DoubleFloat::from(f64::from_bits(1))),
    ] {
        cache_assert_roundoff_lane(&mut cache, &prototype, &value);
    }
}

#[test]
fn monitor_estimate_cache_invalidates_when_next_lane_has_equal_values_at_lower_precision() {
    let monitor = cache_repeated_monitor();
    let prototype = Float::new(256);
    let input = [complex(Float::with_val(256, 1))];
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    for (bits, accuracy, should_fail) in [
        (256, 128, false),
        (80, 128, true),
        (80, 53, false),
        (256, 128, false),
    ] {
        // All four lanes have identical represented values. Their retained
        // precision and requested accuracy must still affect the status.
        let values = [
            complex(Float::with_val(256, 1)),
            complex(Float::with_val(bits, 1)),
            complex(Float::new(1)),
        ];
        let expected = monitor.inspect_lane_with_accuracy(&values, &input, 1, &prototype, accuracy);
        assert_eq!(expected.is_some(), should_fail);
        let actual =
            monitor.inspect_lane_cached(&values, &input, 1, &prototype, accuracy, &mut cache);
        assert_eq!(actual, expected);
    }
}

#[test]
fn monitor_estimate_cache_keeps_expression_and_taylor_component_axes_independent() {
    let monitor = cache_repeated_monitor();
    let mut cache = MonitorEstimateCache::new(&monitor, 3).unwrap();
    let mut roundoff = OperandRoundoff::new(&0.0);
    let values = [[1.0, 2.0, 4.0], [8.0, 16.0, 32.0]];
    cache.begin_lane();
    for order in [
        [(2, 2), (1, 0), (2, 0), (1, 2), (1, 1), (2, 1)],
        [(1, 1), (2, 0), (1, 2), (2, 2), (2, 1), (1, 0)],
    ] {
        for (index, component) in order {
            let value = complex(values[index - 1][component]);
            let expected = OperandRoundoff::new(&0.0).complex(&value).unwrap();
            let actual = cache
                .estimate(index, component, &mut roundoff, &value)
                .unwrap();
            assert_eq!(actual.to_bits(), expected.to_bits());
        }
    }
}

#[test]
fn monitor_estimate_cache_epoch_wrap_invalidates_old_generation_one_entries() {
    let monitor = cache_repeated_monitor();
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    let mut roundoff = OperandRoundoff::new(&0.0);
    cache.begin_lane();
    assert_eq!(cache.generation, 1);
    for (index, value) in [(1, 1.0), (2, 8.0)] {
        cache
            .estimate(index, 0, &mut roundoff, &complex(value))
            .unwrap();
    }
    cache.generation = u64::MAX;
    cache.begin_lane();
    assert_eq!(cache.generation, 1);
    assert!(cache.generations.iter().all(|&generation| generation == 0));
    for (index, value) in [(1, 64.0), (2, 128.0)] {
        let value = complex(value);
        let expected = OperandRoundoff::new(&0.0).complex(&value).unwrap();
        let actual = cache.estimate(index, 0, &mut roundoff, &value).unwrap();
        assert_eq!(actual.to_bits(), expected.to_bits());
    }
}

#[test]
fn monitor_estimate_cache_retains_first_diagnostic_after_shared_contributions_are_warm() {
    let mut monitor = cache_repeated_monitor();
    monitor.checks[0].label = "successful warmup".into();
    monitor.checks[1].label = "first failing check".into();
    monitor.checks[1].operations = 1_000_000;
    let mut later = monitor.checks[1].clone();
    later.label = "later failing check".into();
    monitor.checks.push(later);
    let values = [complex(3.0), complex(1.0), complex(2.0)];
    let input = [complex(1.0)];

    for first_label in ["first failing check", "later failing check"] {
        let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
        let expected = monitor.inspect_lane_with_accuracy(&values, &input, 1, &0.0, 53);
        assert!(expected.as_ref().unwrap().contains(first_label));
        assert!(expected.as_ref().unwrap().contains("Taylor component 0"));
        assert_eq!(
            monitor.inspect_lane_cached(&values, &input, 1, &0.0, 53, &mut cache),
            expected,
        );
        monitor.checks.swap(1, 2);
    }

    // A later nonfinite contribution must retain its own label when preceding
    // checks pass; it must not be inspected eagerly during cache preparation.
    monitor.expressions.push(Atom::new());
    monitor.checks[1].operations = 3;
    monitor.checks[1].terms = vec![3, 1];
    monitor.checks[1].label = "nonfinite contribution check".into();
    let values = [complex(3.0), complex(1.0), complex(2.0), complex(f64::NAN)];
    let mut cache = MonitorEstimateCache::new(&monitor, 1).unwrap();
    let expected = monitor.inspect_lane_with_accuracy(&values, &input, 1, &0.0, 53);
    assert_eq!(
        expected.as_deref(),
        Some("nonfinite stability contribution for nonfinite contribution check")
    );
    assert_eq!(
        monitor.inspect_lane_cached(&values, &input, 1, &0.0, 53, &mut cache),
        expected,
    );
}

#[test]
fn monitor_estimate_cache_preserves_primal_only_denominator_checks_and_zero_precedence() {
    let mut monitor = cache_repeated_monitor();
    for check in &mut monitor.checks {
        check.denominator = true;
    }
    let input = [complex(1.0), complex(0.0), complex(0.0)];
    let mut values = [
        complex(1.0),
        complex(f64::NAN),
        complex(f64::INFINITY),
        complex(2.0),
        complex(f64::NAN),
        complex(f64::NAN),
        complex(-1.0),
        complex(f64::NAN),
        complex(f64::NAN),
    ];
    let mut cache = MonitorEstimateCache::new(&monitor, 3).unwrap();
    assert!(
        monitor
            .inspect_lane_with_accuracy(&values, &input, 3, &0.0, 53)
            .is_none()
    );
    assert!(
        monitor
            .inspect_lane_cached(&values, &input, 3, &0.0, 53, &mut cache)
            .is_none()
    );

    values[0] = complex(0.0);
    values[3] = complex(f64::NAN);
    let expected = monitor.inspect_lane_with_accuracy(&values, &input, 3, &0.0, 53);
    assert_eq!(
        expected.as_deref(),
        Some("zero recurrence denominator: synthetic cancellation")
    );
    assert_eq!(
        monitor.inspect_lane_cached(&values, &input, 3, &0.0, 53, &mut cache),
        expected,
    );
}
