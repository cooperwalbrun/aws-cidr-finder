import json
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Tuple

from tabulate import tabulate

from aws_cidr_finder import utilities
from aws_cidr_finder.boto import BotoWrapper

_parser: ArgumentParser = ArgumentParser(
    description="A CLI tool for finding unused CIDR blocks in AWS VPCs."
)
_parser.add_argument(
    "--profile",
    type=str,
    metavar="PROFILE",
    dest="profile",
    help="The profile from your AWS configuration to use to authenticate to the AWS API."
)
_parser.add_argument(
    "--region",
    type=str,
    metavar="REGION",
    dest="region",
    help="The AWS region to use to authenticate to the AWS API."
)
_parser.add_argument(
    "--json", action="store_true", dest="json", help="Outputs command output in JSON format."
)


def _get_arguments() -> list[str]:  # pragma: no cover
    # This logic is extracted into its own method for unit test mocking purposes
    return sys.argv[1:]


def _parse_arguments(arguments: list[str]) -> dict[str, Any]:
    arguments: Namespace = _parser.parse_args(arguments)
    return vars(arguments)


def main() -> None:
    arguments = _parse_arguments(_get_arguments())

    boto = BotoWrapper(arguments.get("PROFILE"), arguments.get("REGION"))

    vpc_data = boto.get_vpc_data()
    subnet_cidrs = boto.get_subnet_cidrs()
    subnet_cidrs_grouped_by_vpc: dict[str, Tuple[str, list[str]]] = {}
    subnet_cidr_gaps: dict[str, list[str]] = {}

    for vpc_name, vpc_cidr in vpc_data:
        subnet_cidrs_grouped_by_vpc[vpc_name] = (vpc_cidr, [])
        subnet_cidr_gaps[vpc_name] = []
        for subnet_cidr in subnet_cidrs:
            if utilities.is_cidr_inside(vpc_cidr, subnet_cidr):
                subnet_cidrs_grouped_by_vpc[vpc_name][1].append(subnet_cidr)

    for vpc_name, data in subnet_cidrs_grouped_by_vpc.items():
        vpc_cidr, subnet_cidrs = data
        subnet_cidr_gaps[vpc_name] = utilities.merge_adjacent_cidrs(
            utilities.find_subnet_holes(vpc_cidr, subnet_cidrs)
        )

    sorted_data = {
        vpc_name: utilities.sort_cidrs(subnet_cidrs)
        for vpc_name,
        subnet_cidrs in subnet_cidr_gaps.items()
    }
    if arguments["json"]:
        print(json.dumps(sorted_data))
    else:
        table_data = [[os.linesep.join(cidrs) for cidrs in sorted_data.values()]]
        print(tabulate(table_data, headers=sorted_data.keys()))


if __name__ == "__main__":
    main()
