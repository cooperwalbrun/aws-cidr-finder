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
