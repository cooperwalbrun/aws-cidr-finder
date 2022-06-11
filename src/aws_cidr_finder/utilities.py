from aws_cidr_finder.boto_wrapper import VPC
from aws_cidr_finder.custom_types import SingleCIDRVPC
from aws_cidr_finder.engine import CIDREngine


def get_prefix(cidr: str) -> int:
    return int(cidr.split("/")[1])


def split_out_individual_cidrs(vpcs: list[VPC], engine: CIDREngine) -> list[SingleCIDRVPC]:
    ret = []

    for vpc in vpcs:
        for cidr in vpc.cidrs:
            ret.append(
                SingleCIDRVPC(
                    id=vpc.id,
                    name=vpc.name,
                    cidr=cidr,
                    subnets=[s for s in vpc.subnets if engine.is_cidr_inside(cidr, s)]
                )
            )

    return ret
