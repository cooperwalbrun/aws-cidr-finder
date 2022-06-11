from aws_cidr_finder import boto_wrapper


def test_get_vpc_name() -> None:
    assert boto_wrapper._get_vpc_name([]) is None
    assert boto_wrapper._get_vpc_name([{"Key": "Name", "Value": "test"}]) == "test"
