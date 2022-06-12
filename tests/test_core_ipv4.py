from typing import Any

from aws_cidr_finder import core


def _assert_lists_equal(actual: list[Any], expected: list[Any]) -> None:
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_get_first_ip_in_next_cidr() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.0/32", "172.0.0.1"),
        ("172.0.0.0/31", "172.0.0.2"),
        ("172.0.0.0/20", "172.0.16.0")
    ]
    # yapf: enable

    for cidr, expected in test_cases:
        assert core._get_first_ip_in_next_cidr(cidr) == expected


def test_get_last_ip_in_previous_cidr() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.0/32", "171.255.255.255"),
        ("172.0.0.1/32", "172.0.0.0"),
        ("172.0.0.0/31", "171.255.255.255"),
        ("172.0.0.0/20", "171.255.255.255")
    ]
    # yapf: enable

    for cidr, expected in test_cases:
        assert core._get_last_ip_in_previous_cidr(cidr) == expected


def test_get_previous_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.2/32", 31, "172.0.0.0/31"),
        ("172.0.0.2/32", 32, "172.0.0.1/32"),
        ("172.0.32.0/20", 19, "172.0.0.0/19"),
        ("172.0.32.0/20", 21, None)  # Requesting a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert core._get_previous_cidr_with_prefix(cidr, prefix) == expected


def test_get_next_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.2/32", 31, "172.0.0.4/31"),
        ("172.0.0.2/32", 32, "172.0.0.3/32"),
        ("172.0.32.0/20", 19, "172.0.64.0/19"),
        ("172.0.32.0/20", 21, None)  # Requesting a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert core._get_next_cidr_with_prefix(cidr, prefix) == expected


def test_cidrs_are_adjacent() -> None:
    true_test_cases = [
        ("172.31.224.0/20", "172.31.240.0/20"),
        ("172.31.224.0/20", "172.31.240.0/21"),
        ("172.31.224.0/20", "172.31.240.0/32"),
    ]
    for cidr1, cidr2 in true_test_cases:
        assert core._cidrs_are_adjacent(cidr1, cidr2)
        assert core._cidrs_are_adjacent(cidr2, cidr1)

    false_test_cases = [
        ("172.31.208.0/20", "172.31.240.0/20"),
        ("172.31.224.0/21", "172.31.240.0/20"),
        ("172.31.224.0/20", "172.31.240.1/32"),
    ]
    for cidr1, cidr2 in false_test_cases:
        assert not core._cidrs_are_adjacent(cidr1, cidr2)
        assert not core._cidrs_are_adjacent(cidr2, cidr1)


def test_break_down_to_desired_prefix() -> None:
    # yapf: disable
    test_cases = [
        # Test 1
        ([], 7,
         []),
        # Test 2
        (["0.0.0.0/0"], 2,
         ["0.0.0.0/2", "64.0.0.0/2", "128.0.0.0/2", "192.0.0.0/2"]),
        # Test 3
        (["172.31.96.0/19", "172.31.128.0/17"], 17,
         ["172.31.128.0/17"]),
        # Test 4 - tests requesting a prefix that would result in too many CIDRs
        (["172.31.96.0/16"], 32,
         []),
        # Test 5
        (["172.31.96.0/19", "172.31.128.0/17"], 12,
         [])
    ]
    # yapf: enable

    for cidrs, prefix, expected in test_cases:
        actual = core.break_down_to_desired_prefix(cidrs, prefix)
        _assert_lists_equal(actual[0], expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = core.break_down_to_desired_prefix(reversed, prefix)
        _assert_lists_equal(actual_reverse[0], expected)


def test_find_subnet_holes() -> None:
    # yapf: disable
    test_cases = [
        # Test 1
        ("172.31.0.0/16", [], ["172.31.0.0/16"]),
        # Test 2
        ("0.0.0.0/0", ["128.0.0.0/1"], ["0.0.0.0/1"]),
        # Test 3
        ("172.31.0.0/16", ["172.31.0.0/20", "172.31.16.0/20", "172.31.32.0/20", "172.31.48.0/20",
                           "172.31.64.0/20", "172.31.80.0/20"],
         ["172.31.96.0/19", "172.31.128.0/17"]),
        # Test 4
        ("172.31.0.0/16", ["172.31.0.0/20", "172.31.16.0/32", "172.31.32.0/20", "172.31.48.0/20",
                           "172.31.64.0/20", "172.31.80.0/20"],
         ["172.31.16.1/32", "172.31.16.2/31", "172.31.16.4/30", "172.31.16.8/29", "172.31.16.16/28",
          "172.31.16.32/27", "172.31.16.64/26", "172.31.16.128/25", "172.31.17.0/24",
          "172.31.18.0/23", "172.31.20.0/22", "172.31.24.0/21", "172.31.96.0/19",
          "172.31.128.0/17"])
    ]
    # yapf: enable

    for vpc_cidr, cidrs, expected in test_cases:
        actual = core.find_subnet_holes(vpc_cidr, cidrs)
        _assert_lists_equal(actual, expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = core.find_subnet_holes(vpc_cidr, reversed)
        _assert_lists_equal(actual_reverse, expected)
