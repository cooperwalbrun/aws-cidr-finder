import json
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture
from tabulate import tabulate

from aws_cidr_finder import __main__
from aws_cidr_finder.custom_types import VPC


def test_main_no_arguments(mocker: MockerFixture) -> None:
    mocker.patch("aws_cidr_finder.__main__._get_arguments", return_value=[])
    print_mock: MagicMock = mocker.patch("builtins.print")

    with pytest.raises(SystemExit) as wrapped_system_exit:
        __main__.main()

    assert wrapped_system_exit.value.code == 1
    print_mock.assert_has_calls([
        call((
            "You must specify either a profile or an access keypair via the environment variables "
            "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_SESSION_TOKEN (if "
            "authenticating with a session)"
        ))
    ])


def test_main_only_profile_argument(mocker: MockerFixture) -> None:
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper.__init__", return_value=None)
    mocker.patch(
        "aws_cidr_finder.__main__.BotoWrapper._get_vpc_data",
        return_value=[
            VPC(id="test1", name="test-vpc1", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"])
        ]
    )
    mocker.patch("aws_cidr_finder.__main__._get_arguments", return_value=["--profile", "test"])
    print_mock: MagicMock = mocker.patch("builtins.print")

    __main__.main()

    print_mock.assert_has_calls([
        call((
            "Here are the available CIDR blocks in the 'test-vpc1' VPC (VPC CIDR block "
            "'172.31.0.0/19'):"
        )),
        call(tabulate([["172.31.16.0/20", 4096], ["Total", 4096]], headers=["CIDR", "IP Count"]))
    ])


def test_main_json_output(mocker: MockerFixture) -> None:
    mocker.patch("aws_cidr_finder.__main__.BotoWrapper.__init__", return_value=None)
    mocker.patch(
        "aws_cidr_finder.__main__.BotoWrapper._get_vpc_data",
        return_value=[
            VPC(id="test1", name="test-vpc1", cidrs=["172.31.0.0/19"], subnets=["172.31.0.0/20"]),
            VPC(id="test2", name="test-vpc2", cidrs=["172.31.32.0/20"], subnets=["172.31.32.0/21"])
        ]
    )
    mocker.patch(
        "aws_cidr_finder.__main__._get_arguments",
        return_value=["--profile", "test", "--json", "--prefix", "20"]
    )
    print_mock: MagicMock = mocker.patch("builtins.print")

    __main__.main()

    # yapf: disable
    print_mock.assert_has_calls([
        call(
            json.dumps({
                "messages": [(
                    "Note: skipping the CIDR '172.31.40.0/21' in the VPC 'test-vpc2' because its "
                    "prefix (21) is numerically greater than the requested prefix (20)"
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
            })
        )
    ])
    # yapf: enable
