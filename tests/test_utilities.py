from typing import Any

from aws_cidr_finder import utilities


def _assert_lists_equal(actual: list[Any], expected: list[Any]) -> None:
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_get_prefix() -> None:
    assert utilities.get_prefix("172.0.0.0/32") == 32
    assert utilities.get_prefix("172.0.0.2/31") == 31
    assert utilities.get_prefix("172.0.16.0/20") == 20
    assert utilities.get_prefix("0.0.0.0/0") == 0


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
        assert utilities.get_last_ip_in_previous_cidr(cidr) == expected


def test_get_first_ip_in_next_cidr() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.0/32", "172.0.0.1"),
        ("172.0.0.0/31", "172.0.0.2"),
        ("172.0.0.0/20", "172.0.16.0")
    ]
    # yapf: enable

    for cidr, expected in test_cases:
        assert utilities.get_first_ip_in_next_cidr(cidr) == expected


def test_get_previous_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.2/32", 31, "172.0.0.0/31"),
        ("172.0.0.2/32", 32, "172.0.0.1/32"),
        ("172.0.32.0/20", 19, "172.0.0.0/19"),
        ("172.0.32.0/20", 21, None)  # Using a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert utilities.get_previous_cidr_with_prefix(cidr, prefix) == expected


def test_get_next_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("172.0.0.2/32", 31, "172.0.0.4/31"),
        ("172.0.0.2/32", 32, "172.0.0.3/32"),
        ("172.0.32.0/20", 19, "172.0.64.0/19"),
        ("172.0.32.0/20", 21, None)  # Using a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert utilities.get_next_cidr_with_prefix(cidr, prefix) == expected


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


def test_break_down_to_desired_prefix() -> None:
    # yapf: disable
    test_cases = [
        ([], 7,
         []),
        (["0.0.0.0/0"], 2,
         ["0.0.0.0/2", "64.0.0.0/2", "128.0.0.0/2", "192.0.0.0/2"])
    ]
    # yapf: enable

    for cidrs, prefix, expected in test_cases:
        actual = utilities.break_down_to_desired_prefix(cidrs, prefix)
        _assert_lists_equal(actual, expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = utilities.break_down_to_desired_prefix(reversed, prefix)
        _assert_lists_equal(actual_reverse, expected)


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
        actual = utilities.find_subnet_holes(vpc_cidr, cidrs)
        _assert_lists_equal(actual, expected)

        reversed = cidrs.copy()
        reversed.reverse()  # To assert that order is irrelevant
        actual_reverse = utilities.find_subnet_holes(vpc_cidr, reversed)
        _assert_lists_equal(actual_reverse, expected)
