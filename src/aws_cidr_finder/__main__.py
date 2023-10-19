import json
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Any

from tabulate import tabulate

from aws_cidr_finder import core
from aws_cidr_finder.boto_wrapper import BotoWrapper
from aws_cidr_finder.custom_types import SingleCIDRVPC, JSONOutput

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
    help="The CIDR prefix that you want results to use."
)
_parser.add_argument(
    "--json", action="store_true", dest="json", help="Output results in JSON format."
)
_parser.add_argument(
    "--ipv6",
    action="store_true",
    dest="ipv6",
    help="Perform all functions based on IPv6 instead of IPv4."
)


def _get_arguments() -> list[str]:  # pragma: no cover
    # This logic is extracted into its own method for unit test mocking purposes
    return sys.argv[1:]


def _parse_arguments(arguments: list[str]) -> dict[str, Any]:
    ret: Namespace = _parser.parse_args(arguments)
    return vars(ret)


def main() -> None:
    arguments = _parse_arguments(_get_arguments())

    if arguments.get("profile") is None and (os.environ.get("AWS_ACCESS_KEY_ID") is None
                                             or os.environ.get("AWS_SECRET_ACCESS_KEY")):
        print((
            "You must specify either a profile or an access keypair via the environment variables "
            "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_SESSION_TOKEN (if "
            "authenticating with a session)"
        ))
        exit(1)

    boto = BotoWrapper(profile_name=arguments.get("profile"), region=arguments.get("region"))

    ipv6: bool = arguments["ipv6"]

    subnet_cidr_gaps: dict[SingleCIDRVPC, list[str]] = {}
    messages: list[str] = []

    for vpc in core.split_out_individual_cidrs(boto.get_vpc_data(ipv6=ipv6)):
        # yapf: disable
        subnet_cidr_gaps[vpc] = core.find_subnet_holes(
            vpc.cidr,
            vpc.subnets
        )
        # yapf: enable
        if arguments.get("prefix") is not None:
            converted_cidrs, m = core.break_down_to_desired_prefix(
                subnet_cidr_gaps[vpc], arguments["prefix"]
            )
            subnet_cidr_gaps[vpc] = converted_cidrs
            messages += m

    if arguments["json"]:
        output: JSONOutput = {"aws-cidr-finder-messages": messages, "vpcs": {}}
        for vpc, subnet_cidrs in subnet_cidr_gaps.items():
            if vpc.readable_name not in output["vpcs"]:
                output["vpcs"][vpc.readable_name] = {}
            output["vpcs"][vpc.readable_name][vpc.cidr] = core.sort_cidrs(subnet_cidrs)
        print(json.dumps(output))
    else:
        if len(subnet_cidr_gaps) == 0:
            print(f"No available {'IPv6' if ipv6 else 'IPv4'} CIDR blocks were found in any VPC.")
        else:
            for msg in messages:
                print(msg)
            if len(messages) > 0:
                print()

            for vpc, subnet_cidrs in subnet_cidr_gaps.items():
                sorted_cidrs = core.sort_cidrs(subnet_cidrs)
                print((
                    f"Here are the available CIDR blocks in the '{vpc.readable_name}' VPC (VPC "
                    f"CIDR block '{vpc.cidr}'):"
                ))
                table_data = []
                for cidr in sorted_cidrs:
                    table_data.append([cidr, core.get_ip_count(cidr)])
                table_data.append([
                    "Total", sum([core.get_ip_count(cidr) for cidr in sorted_cidrs])
                ])
                print(tabulate(table_data, headers=["CIDR", "IP Count"]))


if __name__ == "__main__":
    main()
