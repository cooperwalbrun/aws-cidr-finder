from typing import Any

from aws_cidr_finder import utilities


def _assert_lists_equal(actual: list[Any], expected: list[Any]) -> None:
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_cidrs_are_adjacent() -> None:
    true_test_cases = [
        ("172.31.224.0/20", "172.31.240.0/20"),
        ("172.31.224.0/20", "172.31.240.0/21"),
        ("172.31.224.0/20", "172.31.240.0/32"),
    ]
    for cidr1, cidr2 in true_test_cases:
        assert utilities.cidrs_are_adjacent(cidr1, cidr2)
        assert utilities.cidrs_are_adjacent(cidr2, cidr1)

    false_test_cases = [
        ("172.31.208.0/20", "172.31.240.0/20"),
        ("172.31.224.0/21", "172.31.240.0/20"),
        ("172.31.224.0/20", "172.31.240.1/32"),
    ]
    for cidr1, cidr2 in false_test_cases:
        assert not utilities.cidrs_are_adjacent(cidr1, cidr2)
        assert not utilities.cidrs_are_adjacent(cidr2, cidr1)


def test_break_down_to_desired_mask() -> None:
    # yapf: disable
    test_cases = [
        ([], 7,
         []),
        (["0.0.0.0/0"], 2,
         ["0.0.0.0/2", "64.0.0.0/2", "128.0.0.0/2", "192.0.0.0/2"])
    ]
    # yapf: enable

    for cidrs, mask, expected in test_cases:
        actual = utilities.break_down_to_desired_mask(cidrs, mask)
        _assert_lists_equal(actual, expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = utilities.break_down_to_desired_mask(reversed, mask)
        _assert_lists_equal(actual_reverse, expected)


def test_merge_adjacent_cidrs() -> None:
    # yapf: disable
    test_cases = [
        (["172.31.0.0/32", "172.31.0.1/32"],
         ["172.31.0.0/31"]),
        (["172.31.0.0/32", "172.31.0.1/32", "172.31.0.2/32"],
         ["172.31.0.0/31", "172.31.0.2/32"]),
        (["172.31.0.0/32", "172.31.0.1/32", "172.31.0.2/32", "172.31.0.3/32"],
         ["172.31.0.0/30"]),
        (["172.31.0.0/32", "172.31.0.1/32", "172.31.0.2/32", "172.31.16.0/20"],
         ["172.31.0.0/31", "172.31.0.2/32", "172.31.16.0/20"]),
        ([],
         []),
        (["0.0.0.0/0"],
         ["0.0.0.0/0"]),
        (["172.31.96.0/20", "172.31.112.0/20", "172.31.128.0/20", "172.31.144.0/20",
          "172.31.160.0/20", "172.31.176.0/20", "172.31.192.0/20", "172.31.208.0/20",
          "172.31.240.0/20", "172.31.224.0/20"],
         ["172.31.96.0/19", "172.31.128.0/17"])
    ]
    # yapf: enable

    for cidrs, expected in test_cases:
        actual = utilities.merge_adjacent_cidrs(cidrs)
        _assert_lists_equal(actual, expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = utilities.merge_adjacent_cidrs(reversed)
        _assert_lists_equal(actual_reverse, expected)


def test_find_subnet_holes() -> None:
    allocated_subnets = [
        "172.31.0.0/20",
        "172.31.16.0/20",
        "172.31.32.0/20",
        "172.31.48.0/20",
        "172.31.64.0/20",
        "172.31.80.0/20"
    ]
    expected = [
        "172.31.96.0/20",
        "172.31.112.0/20",
        "172.31.128.0/20",
        "172.31.144.0/20",
        "172.31.160.0/20",
        "172.31.176.0/20",
        "172.31.192.0/20",
        "172.31.208.0/20",
        "172.31.240.0/20",
        "172.31.224.0/20"
    ]
    actual = utilities.find_subnet_holes("172.31.0.0/16", allocated_subnets)
    _assert_lists_equal(actual, expected)
