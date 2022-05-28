import json
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Tuple

from tabulate import tabulate

from aws_cidr_finder.boto_wrapper import BotoWrapper, VPC
from aws_cidr_finder.cidr_finder import CIDRFinder
from aws_cidr_finder.ipv4 import IPv4CIDRFinder
from aws_cidr_finder.ipv6 import IPv6CIDRFinder

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
    help="The AWS region to use when interacting with the AWS API."
)
_parser.add_argument(
    "--prefix",
    type=int,
    metavar="PREFIX",
    dest="prefix",
    help=(
        "The CIDR prefix that you want results to use (note: this will fail if the prefix is "
        "smaller than one or more unused CIDR blocks). Also beware specifying high prefix values "
        "(i.e. 24+) due to the potentially huge command output!"
    )
)
_parser.add_argument(
    "--json", action="store_true", dest="json", help="Outputs results in JSON format."
)
_parser.add_argument(
    "--ipv6",
    action="store_true",
    dest="ipv6",
    help="Perform the functions of this CLI tool based on IPv6 instead of IPv4."
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

    ipv6: bool = arguments["ipv6"]
    engine: CIDRFinder = IPv6CIDRFinder() if ipv6 else IPv4CIDRFinder()

    subnet_cidr_gaps: dict[str, list[str]] = {}

    for vpc in boto.get_vpc_data(ipv6=ipv6):
        # yapf: disable
        subnet_cidr_gaps[vpc.name] = engine.find_subnet_holes(
            vpc.cidr,
            boto.get_subnet_cidrs(vpc.id)
        )
        # yapf: enable
        if arguments.get("prefix") is not None:
            subnet_cidr_gaps[vpc.name] = engine.break_down_to_desired_prefix(
                subnet_cidr_gaps[vpc.name], arguments["prefix"], arguments["json"]
            )

    sorted_data: dict[str, list[str]] = {
        vpc_name: engine.sort_cidrs(subnet_cidrs)
        for vpc_name,
        subnet_cidrs in subnet_cidr_gaps.items()
    }
    if arguments["json"]:
        print(json.dumps(sorted_data))
    else:
        for vpc_name, sorted_cidrs in sorted_data.items():
            print(f"Here are the available CIDR blocks in the '{vpc_name}' VPC:")
            table_data = []
            for cidr in sorted_cidrs:
                table_data.append([cidr, engine.get_ip_count(cidr)])
            table_data.append(["Total", sum([engine.get_ip_count(cidr) for cidr in sorted_cidrs])])
            print(tabulate(table_data, headers=["CIDR", "IP Count"]))


if __name__ == "__main__":
    main()
