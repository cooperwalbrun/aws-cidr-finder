import os
from typing import Any, Optional, Tuple

import boto3
from botocore.client import BaseClient


def _get_all_cidrs(vpc: dict[str, Any]) -> list[str]:
    # TODO - is this method needed?
    pass


class VPC:
    def __init__(self, *, id: str, name: str, cidr: str):
        self.id = id
        self.name = name
        self.cidr = cidr  # TODO - does this need to be a list for IPv6 support?


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
        def get_vpc_name(cidr: str, tags: list[dict[str, str]]) -> str:
            for key_value_pair in tags:
                if key_value_pair["Key"] == "Name":
                    return key_value_pair["Value"]
            return cidr

        vpcs = self._client.describe_vpcs()["Vpcs"]
        return [
            VPC(
                id=vpc["VpcId"],
                name=get_vpc_name(vpc["CidrBlock"], vpc["Tags"]),
                cidr=vpc["CidrBlock"]  # TODO - use the ipv6 argument
            ) for vpc in vpcs
        ]

    def get_subnet_cidrs(self, vpc_id: str) -> list[str]:
        subnets = self._client.describe_subnets(Filters=[{
            "Name": "vpc-id", "Values": [vpc_id]
        }])["Subnets"]
        return [subnet["CidrBlock"] for subnet in subnets]
