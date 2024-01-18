from pytest_mock import MockerFixture

from aws_cidr_finder import find_available_cidrs
from aws_cidr_finder.custom_types import VPC


def test_find_available_cidrs_no_arguments(mocker: MockerFixture) -> None:
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper.__init__", return_value=None)
    mocker.patch(
        "aws_cidr_finder.__main__.BotoWrapper._get_vpc_data",
        return_value=[
            VPC(id="test1", name="test-vpc1", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"]),
            VPC(id="test2", name="test-vpc2", cidrs=["172.31.32.0/20"], subnets=["172.31.32.0/21"])
        ]
    )

    data = find_available_cidrs()

    # yapf: disable
    assert data == {
        "messages": [],
        "cidrs_not_converted_to_prefix": [],
        "data": [
            {
                "id": "test1",
                "name": "test-vpc1",
                "cidr": "172.31.0.0/19",
                "available_cidr_blocks": ["172.31.16.0/20"]
            },
            {
                "id": "test2",
                "name": "test-vpc2",
                "cidr": "172.31.32.0/20",
                "available_cidr_blocks": ["172.31.40.0/21"]
            }
        ]
    }
    # yapf: enable


def test_find_available_cidrs_with_prefix(mocker: MockerFixture) -> None:
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper.__init__", return_value=None)
    mocker.patch(
        "aws_cidr_finder.__main__.BotoWrapper._get_vpc_data",
        return_value=[
            VPC(id="test1", name="test-vpc1", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"]),
            VPC(id="test2", name="test-vpc2", cidrs=["172.31.32.0/20"], subnets=["172.31.32.0/21"])
        ]
    )

    data = find_available_cidrs(desired_prefix=20)

    # yapf: disable
    assert data == {
        "messages": [(
            "Note: skipping the CIDR '172.31.40.0/21' in the VPC 'test-vpc2' because its prefix "
            "(21) is numerically greater than the requested prefix (20)"
        )],
        "cidrs_not_converted_to_prefix": [
            "172.31.40.0/21"
        ],
        "data": [
            {
                "id": "test1",
                "name": "test-vpc1",
                "cidr": "172.31.0.0/19",
                "available_cidr_blocks": ["172.31.16.0/20"]
            },
            {
                "id": "test2",
                "name": "test-vpc2",
                "cidr": "172.31.32.0/20",
                "available_cidr_blocks": []
            }
        ]
    }
    # yapf: enable
