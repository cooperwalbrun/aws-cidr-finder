from typing import Optional


class VPC:
    """
    This class exists to serve an intermediate representation of VPC information originating from
    AWS itself (Boto). Instances of this class are always destined to be converted into instances of
    the SingleCIDRVPC class.
    """
    def __init__(self, *, id: str, name: Optional[str], cidrs: list[str], subnets: list[str]):
        self.id = id
        self.name = name
        self.cidrs = cidrs
        self.subnets = subnets


class SingleCIDRVPC:
    def __init__(self, *, id: str, name: Optional[str], cidr: str, subnets: list[str]):
        self.id = id
        self.name = name
        self.cidr = cidr
        self.subnets = subnets

    @property
    def readable_name(self) -> str:
        return self.id if self.name is None else self.name

    def __repr__(self) -> str:
        return self.readable_name

    def __str__(self) -> str:
        return self.readable_name

    def __hash__(self) -> int:
        # This class must be hashable because we use it to key dictionaries
        return hash(self.id) + hash(self.cidr)
