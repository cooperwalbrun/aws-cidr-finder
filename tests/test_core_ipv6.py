from typing import Any

from aws_cidr_finder import core


def _assert_lists_equal(expected: list[Any], actual: list[Any]) -> None:
    assert len(expected) == len(actual)
    assert set(expected) == set(actual)


def test_get_first_ip_in_next_cidr() -> None:
    # yapf: disable
    test_cases = [
        ("::/128", "::1"),
        ("::/127", "::2"),
        ("::/64", "0:0:0:1::"),
    ]
    # yapf: enable

    for cidr, expected in test_cases:
        assert core._get_first_ip_in_next_cidr(cidr) == expected


def test_get_last_ip_in_previous_cidr() -> None:
    # yapf: disable
    test_cases = [
        ("1::/128", "0:ffff:ffff:ffff:ffff:ffff:ffff:ffff"),
        ("::1/128", "::"),
        ("1::/127", "0:ffff:ffff:ffff:ffff:ffff:ffff:ffff"),
        ("1::/64", "0:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
    ]
    # yapf: enable

    for cidr, expected in test_cases:
        assert core._get_last_ip_in_previous_cidr(cidr) == expected


def test_get_previous_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("::2/128", 127, "::/127"),
        ("::2/128", 128, "::1/128"),
        ("0:0:0:1::/128", 64, "::/64"),
        ("::/55", 56, None)  # Requesting a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert core._get_previous_cidr_with_prefix(cidr, prefix) == expected


def test_get_next_cidr_with_prefix() -> None:
    # yapf: disable
    test_cases = [
        ("::2/128", 127, "::4/127"),
        ("::2/128", 128, "::3/128"),
        ("::/64", 63, "0:0:0:2::/63"),
        ("::/55", 56, None)  # Requesting a prefix that is higher than the given one
    ]
    # yapf: enable

    for cidr, prefix, expected in test_cases:
        assert core._get_next_cidr_with_prefix(cidr, prefix) == expected


def test_cidrs_are_adjacent() -> None:
    true_test_cases = [
        ("::/64", "0:0:0:1::/64"),
        ("::/64", "0:0:0:1::/65"),
        ("::/64", "0:0:0:1::/128"),
    ]
    for cidr1, cidr2 in true_test_cases:
        assert core._cidrs_are_adjacent(cidr1, cidr2)
        assert core._cidrs_are_adjacent(cidr2, cidr1)

    false_test_cases = [
        ("::/64", "0:0:0:2::/64"),
        ("::/63", "0:0:0:1::/64"),
        ("::/64", "0:0:0:1::1/128"),
    ]
    for cidr1, cidr2 in false_test_cases:
        assert not core._cidrs_are_adjacent(cidr1, cidr2)
        assert not core._cidrs_are_adjacent(cidr2, cidr1)


def test_break_down_to_desired_prefix() -> None:
    # yapf: disable
    test_cases = [
        # Test 1
        ([], 7,
         [], []),
        # Test 2
        (["::/0"], 2,
         ["::/2", "4000::/2", "8000::/2", "c000::/2"], []),
        # Test 3
        (["::/96", "0:0:0:1::/90"], 91,
         ["0:0:0:1::/91", "::1:0:20:0:0/91"], [
             "Note: skipping the CIDR '::/96' in the VPC 'test' because its prefix (96) is numerically greater than the requested prefix (91)"
         ]),
        # Test 4 - requesting a prefix that would result in too many CIDRs
        (["::/32"], 64,
         [], [
             "Warning: skipping the CIDR '::/32' in the VPC 'test' because its prefix is only 32 and converting it to a list of CIDRs whose prefixes are 64 will result in a list containing 4294967296 CIDRs!"
         ]),
        # # Test 5
        (["::/64", "0:0:0:1::/65"], 47,
         [], [
             "Note: skipping the CIDR '::/64' in the VPC 'test' because its prefix (64) is numerically greater than the requested prefix (47)",
             "Note: skipping the CIDR '0:0:0:1::/65' in the VPC 'test' because its prefix (65) is numerically greater than the requested prefix (47)"
         ])
    ]
    # yapf: enable

    for input_cidrs, prefix, expected_cidrs, expected_messages in test_cases:
        actual_cidrs, actual_unconverted_cidrs, actual_messages = core.break_down_to_desired_prefix(
            "test", input_cidrs, prefix
        )
        _assert_lists_equal(expected_cidrs, actual_cidrs)
        _assert_lists_equal(expected_messages, actual_messages)


def test_find_subnet_holes() -> None:
    # yapf: disable
    test_cases = [
        # Test 1
        ("::/16", [], ["::/16"]),
        # Test 2
        ("::/0", ["8000::/1"], ["::/1"]),
        # Test 3
        ("::/16", ["::/20", "0:1000::/20", "0:2000::/20", "0:3000::/20", "0:4000::/20",
                   "0:5000::/20"],
         ["0:6000::/19", "0:8000::/17"]),
        # Test 4
        ("::/16", ["::/20", "0:1000::/32", "0:2000::/20", "0:3000::/20", "0:4000::/20",
                   "0:5000::/20"],
         ["0:1001::/32", "0:1002::/31", "0:1004::/30", "0:1008::/29", "0:1010::/28", "0:1020::/27",
          "0:1040::/26", "0:1080::/25", "0:1100::/24", "0:1200::/23", "0:1400::/22", "0:1800::/21",
          "0:6000::/19", "0:8000::/17"]),
    ]
    # yapf: enable

    for vpc_cidr, input_cidrs, expected_cidrs in test_cases:
        actual_cidrs = core.find_subnet_holes(vpc_cidr, input_cidrs)
        _assert_lists_equal(expected_cidrs, actual_cidrs)
