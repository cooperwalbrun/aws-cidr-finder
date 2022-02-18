import os
from typing import Optional, Tuple

import boto3
from botocore.client import BaseClient


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

    def get_vpc_data(self) -> list[Tuple[str, str]]:
        def get_vpc_name(cidr: str, tags: list[dict[str, str]]) -> str:
            for key_value_pair in tags:
                if key_value_pair["Key"] == "Name":
                    return key_value_pair["Value"]
            return cidr

        vpcs = self._client.describe_vpcs()["Vpcs"]
        return [(get_vpc_name(vpc["CidrBlock"], vpc["Tags"]), vpc["CidrBlock"]) for vpc in vpcs]

    def get_subnet_cidrs(self) -> list[str]:
        subnets = self._client.describe_subnets()["Subnets"]
        return [subnet["CidrBlock"] for subnet in subnets]
