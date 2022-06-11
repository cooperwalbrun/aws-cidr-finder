import json
from unittest.mock import call, MagicMock

from pytest_mock import MockerFixture
from tabulate import tabulate

from aws_cidr_finder import __main__
from aws_cidr_finder.custom_types import VPC


def test_main_no_arguments(mocker: MockerFixture) -> None:
    boto_wrapper_mock = MagicMock()
    boto_wrapper_mock.get_vpc_data = lambda ipv6: [
        VPC(id="test", name="test-vpc", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"])
    ]
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper", return_value=boto_wrapper_mock)
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper", return_value=boto_wrapper_mock)
    mocker.patch("aws_cidr_finder.__main__._get_arguments", return_value=[])
    print_mock: MagicMock = mocker.patch("builtins.print")

    __main__.main()

    print_mock.assert_has_calls([
        call((
            "Here are the available CIDR blocks in the 'test-vpc' VPC (VPC CIDR block "
            "'172.31.0.0/19'):"
        )),
        call(tabulate([["172.31.16.0/20", 4096], ["Total", 4096]], headers=["CIDR", "IP Count"]))
    ])


def test_main_json_output(mocker: MockerFixture) -> None:
    boto_wrapper_mock = MagicMock()
    boto_wrapper_mock.get_vpc_data = lambda ipv6: [
        VPC(id="test", name="test-vpc", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"])
    ]
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper", return_value=boto_wrapper_mock)
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper", return_value=boto_wrapper_mock)
    mocker.patch(
        "aws_cidr_finder.__main__._get_arguments", return_value=["--json", "--prefix", "20"]
    )
    print_mock: MagicMock = mocker.patch("builtins.print")

    __main__.main()

    print_mock.assert_has_calls([
        call(
            json.dumps({
                "aws-cidr-finder-messages": [],
                "vpcs": {
                    "test-vpc": {
                        "172.31.0.0/19": ["172.31.16.0/20"]
                    }
                }
            })
        )
    ])
