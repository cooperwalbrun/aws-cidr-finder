import os
from typing import Optional

import boto3
from mypy_boto3_ec2 import EC2Client
from mypy_boto3_ec2.type_defs import VpcTypeDef, DescribeSubnetsResultTypeDef, SubnetTypeDef

from aws_cidr_finder import core
from aws_cidr_finder.custom_types import VPC, SingleCIDRVPC


def _get_vpc_name(vpc: VpcTypeDef) -> Optional[str]:
    for key_value_pair in vpc.get("Tags", []):
        if key_value_pair["Key"] == "Name":
            return key_value_pair["Value"]
    return None


def _parse_vpc_cidrs(vpc: VpcTypeDef, *, ipv6: bool) -> list[str]:
    # Note: the structure we are crawling below is documented here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpcs
    if ipv6:
        return [
            association["Ipv6CidrBlock"]
            for association in vpc["Ipv6CidrBlockAssociationSet"]
            if association["Ipv6CidrBlockState"]["State"] in ["associated", "associating"]
        ]
    else:
        return [
            association["CidrBlock"]
            for association in vpc["CidrBlockAssociationSet"]
            if association["CidrBlockState"]["State"] in ["associated", "associating"]
        ]


def _parse_subnet_cidrs(subnets: list[SubnetTypeDef], *, ipv6: bool) -> list[str]:
    # Note: the structure we are crawling below is documented here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_subnets
    if ipv6:
        return [
            association["Ipv6CidrBlock"]
            for subnet in subnets
            for association in subnet["Ipv6CidrBlockAssociationSet"]
            if association["Ipv6CidrBlockState"]["State"] in ["associated", "associating"]
        ]
    else:
        return [subnet["CidrBlock"] for subnet in subnets if "CidrBlock" in subnet]


class BotoWrapper:
    def __init__(self, *, profile_name: Optional[str], region: Optional[str]):  # pragma: no cover
        if profile_name is not None:
            boto = boto3.session.Session(profile_name=profile_name, region_name=region)
        else:
            boto = boto3.session.Session(
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
                region_name=region
            )
        self._client: EC2Client = boto.client("ec2")

    def _get_vpc_data(self, *, ipv6: bool) -> list[VPC]:  # pragma: no cover
        vpcs = self._client.describe_vpcs()["Vpcs"]
        return [
            VPC(
                id=vpc["VpcId"],
                name=_get_vpc_name(vpc),
                cidrs=_parse_vpc_cidrs(vpc, ipv6=ipv6),
                subnets=_parse_subnet_cidrs(
                    self._get_subnet_cidrs(vpc["VpcId"])["Subnets"], ipv6=ipv6
                )
            ) for vpc in vpcs
        ]

    def _get_subnet_cidrs(self, vpc_id: str) -> DescribeSubnetsResultTypeDef:  # pragma: no cover
        return self._client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])

    def get_subnet_cidr_gaps(
        self, *, ipv6: bool, prefix: Optional[int]
    ) -> tuple[dict[SingleCIDRVPC, list[str]], list[str], list[str]]:
        subnet_cidr_gaps: dict[SingleCIDRVPC, list[str]] = {}
        cidrs_not_converted_to_prefix: list[str] = []
        messages: list[str] = []

        for vpc in core.split_out_individual_cidrs(self._get_vpc_data(ipv6=ipv6)):
            # yapf: disable
            subnet_cidr_gaps[vpc] = core.find_subnet_holes(
                vpc.cidr,
                vpc.subnets
            )
            # yapf: enable
            if prefix is not None:
                converted_cidrs, unconverted_cidrs, m = core.break_down_to_desired_prefix(
                    vpc.readable_name, subnet_cidr_gaps[vpc], prefix
                )
                subnet_cidr_gaps[vpc] = converted_cidrs
                cidrs_not_converted_to_prefix += unconverted_cidrs
                messages += m

        return subnet_cidr_gaps, cidrs_not_converted_to_prefix, messages
