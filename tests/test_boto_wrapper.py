from typing import Any

from aws_cidr_finder import boto_wrapper


def _assert_lists_equal(actual: list[Any], expected: list[Any]) -> None:
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_get_vpc_name() -> None:
    assert boto_wrapper._get_vpc_name([]) is None
    assert boto_wrapper._get_vpc_name([{"Key": "Name", "Value": "test"}]) == "test"


def test_parse_vpc_cidrs_ipv4() -> None:
    # yapf: disable
    json = {
        "CidrBlockAssociationSet": [
            {
                "CidrBlock": "172.0.0.0/16",
                "CidrBlockState": {
                    "State": "associated"
                }
            },
            {
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockState": {
                    "State": "disassociated"
                }
            }
        ]
    }
    # yapf: enable
    _assert_lists_equal(boto_wrapper._parse_vpc_cidrs(json, ipv6=False), ["172.0.0.0/16"])


def test_parse_vpc_cidrs_ipv6() -> None:
    # yapf: disable
    json = {
        "Ipv6CidrBlockAssociationSet": [
            {
                "Ipv6CidrBlock": "::/96",
                "Ipv6CidrBlockState": {
                    "State": "associated"
                }
            },
            {
                "Ipv6CidrBlock": "1::/96",
                "Ipv6CidrBlockState": {
                    "State": "disassociated"
                }
            }
        ]
    }
    # yapf: enable
    _assert_lists_equal(boto_wrapper._parse_vpc_cidrs(json, ipv6=True), ["::/96"])
