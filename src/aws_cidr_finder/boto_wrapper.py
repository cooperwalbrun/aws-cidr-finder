import os
from typing import Any, Optional

import boto3
from botocore.client import BaseClient

from aws_cidr_finder.custom_types import VPC


def _get_vpc_name(tags: list[dict[str, str]]) -> Optional[str]:
    for key_value_pair in tags:
        if key_value_pair["Key"] == "Name":
            return key_value_pair["Value"]
    return None


def _parse_vpc_cidrs(vpc: dict[str, Any], *, ipv6: bool) -> list[str]:
    # Note: the structure we are crawling below is documented here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpcs
    if ipv6:
        return [
            association["Ipv6CidrBlock"]
            for association in vpc.get("Ipv6CidrBlockAssociationSet", [])
            if association["Ipv6CidrBlockState"]["State"] in ["associated", "associating"]
        ]
    else:
        return [
            association["CidrBlock"]
            for association in vpc.get("CidrBlockAssociationSet", [])
            if association["CidrBlockState"]["State"] in ["associated", "associating"]
        ]


def _parse_subnet_cidrs(subnets: list[dict[str, Any]], *, ipv6: bool) -> list[str]:
    # Note: the structure we are crawling below is documented here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_subnets
    if ipv6:
        return [
            association["Ipv6CidrBlock"]
            for subnet in subnets
            for association in subnet.get("Ipv6CidrBlockAssociationSet", [])
            if association["Ipv6CidrBlockState"]["State"] == "associated"
        ]
    else:
        return [subnet["CidrBlock"] for subnet in subnets if "CidrBlock" in subnet]


class BotoWrapper:  # pragma: no cover
    def __init__(self, profile_name: Optional[str], region: Optional[str]):
        if profile_name is not None:
            boto = boto3.session.Session(profile_name=profile_name, region_name=region)
        else:
            boto = boto3.session.Session(
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=region
            )
        self._client: BaseClient = boto.client("ec2")

    def get_vpc_data(self, *, ipv6: bool) -> list[VPC]:
        vpcs = self._client.describe_vpcs()["Vpcs"]
        return [
            VPC(
                id=vpc["VpcId"],
                name=_get_vpc_name(vpc["Tags"]),
                cidrs=_parse_vpc_cidrs(vpc, ipv6=ipv6),
                subnets=_parse_subnet_cidrs(
                    self._get_subnet_cidrs(vpc["VpcId"])["Subnets"], ipv6=ipv6
                )
            ) for vpc in vpcs
        ]

    def _get_subnet_cidrs(self, vpc_id: str) -> dict[str, list[dict[str, Any]]]:
        return self._client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
