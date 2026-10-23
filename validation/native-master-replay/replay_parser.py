"""Strict admission of the complete captured master replay, including all timings."""
import math
import random

FIRST_VARIANTS = [0] * 11 + [1] * 10
random.Random(173).shuffle(FIRST_VARIANTS)


def integer(value, minimum=0, maximum=None):
    assert type(value) is int and value >= minimum, "expected bounded integer"
    assert maximum is None or value <= maximum, "integer exceeds bound"
    return value


def finite_number(value, minimum=0, maximum=None):
    assert type(value) in (int, float) and math.isfinite(value), "expected finite number"
    assert value >= minimum and (maximum is None or value <= maximum), "number out of bounds"
    return value


def validate_group(group, expected):
    assert group["family"] == expected["family"]
    assert integer(group["rows"], 1) == expected["rows"]
    assert integer(group["complex_outputs"], 1) == 6 * expected["rows"]
    assert group["symbolica_matches_public_capture_exactly"] is True
    finite_number(group["max_normalized_error"], 0, 1e-10)
    differences = integer(group["represented_component_differences"], 0, 12 * expected["rows"])
    integer(group["signed_zero_differences"], 0, differences)
    integer(group["native_cells"])


def validate_rows(rows, capture, benchmark):
    assert type(rows) is list and len(rows) == 8 and len(capture["rows"]) == 8, "missing case rows"
    coordinates = set()
    for row, original in zip(rows, capture["rows"]):
        outer_batch = integer(row["outer_batch"], 1)
        coordinate = (row["id"], outer_batch)
        assert coordinate == (original["id"], original["outer_batch"]), "case order changed"
        assert coordinate not in coordinates, "duplicate case coordinate"
        coordinates.add(coordinate)
        assert row["status"] == "passed", row.get("error", "failed row")
        assert row["mode"] == ("timing" if benchmark else "qualification")
        integer(row["native_context_preparation_ns"])
        actual = row["result"]
        integer(actual["preparation_ns"])
        groups = original["capture"]["master_captures"]
        assert len(actual["groups"]) == len(groups) == len(actual["represented_outputs"])
        for group, expected, outputs in zip(actual["groups"], groups, actual["represented_outputs"]):
            validate_group(group, expected)
            assert len(outputs) == 2 and all(len(values) == 6 * expected["rows"] for values in outputs)
            for values in outputs:
                for value in values:
                    assert len(value) == 2
                    for bits in value:
                        integer(bits, 0, 2**64 - 1)
                        assert (bits >> 52) & 0x7ff != 0x7ff, "nonfinite represented output"
        timing = actual["timing"]
        assert (timing is not None) == benchmark
        if benchmark:
            assert timing["protocol"] == "actual-master-replay-fixed-loop-v1"
            assert integer(timing["pilot_target_ns"], 1) == 2_000_000
            assert integer(timing["block_target_ns"], 1) == 30_000_000
            assert integer(timing["pair_order_seed"]) == 173
            assert timing["pair_order_algorithm"] == "Python random.Random(seed).shuffle([0]*11+[1]*10)"
            pilots = timing["pilots"]
            assert len(pilots) == 2
            for pilot in pilots:
                assert len(pilot) == 2
                count = integer(pilot[0], 8, 1 << 26)
                elapsed = integer(pilot[1], 1)
                assert count & (count - 1) == 0, "pilot count is not a power of two"
                assert elapsed >= timing["pilot_target_ns"] or count == 1 << 26, "premature pilot stop"
            numerator = 2 * timing["block_target_ns"] * pilots[0][0] * pilots[1][0]
            denominator = pilots[0][1] * pilots[1][0] + pilots[1][1] * pilots[0][0]
            shared = min(1 << 26, max(1, (numerator + denominator - 1) // denominator))
            assert integer(timing["iterations"], 1, 1 << 26) == shared
            assert len(timing["blocks"]) == 21
            for index, block in enumerate(timing["blocks"]):
                assert integer(block["block"], 0, 20) == index
                assert len(block["order"]) == 2
                for variant in block["order"]:
                    integer(variant, 0, 1)
                assert block["order"] == [FIRST_VARIANTS[index], 1 - FIRST_VARIANTS[index]]
                assert integer(block["iterations"], 1, 1 << 26) == shared
                assert len(block["elapsed_ns"]) == 2
                for elapsed in block["elapsed_ns"]:
                    integer(elapsed, 1)
            assert len(timing["postcheck"]) == len(groups)
            for group, expected in zip(timing["postcheck"], groups):
                validate_group(group, expected)
            assert timing["postcheck"] == actual["groups"], "posttiming numerical check changed"
    assert coordinates == {(f"n{n}-r{rank}-massive", width) for n in [2, 3] for rank in [0, 1] for width in [1, 32]}
