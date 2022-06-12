from functools import cmp_to_key
from ipaddress import AddressValueError, ip_address, ip_network, IPv4Network, IPv6Network, \
    IPv4Address, IPv6Address
from typing import Optional, Union

from aws_cidr_finder.custom_types import VPC, SingleCIDRVPC


def _get_cidr(network: Union[IPv4Network, IPv6Network]) -> str:
    return str(network)


def _cidrs_are_adjacent(cidr1: str, cidr2: str) -> bool:
    a = ip_network(cidr1)
    b = ip_network(cidr2)
    return (int(a[-1]) + 1 == int(b[0])) or (int(b[-1]) + 1 == int(a[0]))


def _get_first_ip_in_next_cidr(cidr: str) -> str:
    # Python needs a little "help" inferring which type of IP address an integer value represents,
    # thus we have the manual check below
    network = ip_network(cidr)
    if isinstance(network, IPv4Network):
        return IPv4Address(int(network[-1]) + 1).compressed
    else:
        return IPv6Address(int(network[-1]) + 1).compressed


def _get_last_ip_in_previous_cidr(cidr: str) -> str:
    # Python needs a little "help" inferring which type of IP address an integer value represents,
    # thus we have the manual check below
    network = ip_network(cidr)
    if isinstance(network, IPv4Network):
        return IPv4Address(int(network[0]) - 1).compressed
    else:
        return IPv6Address(int(network[0]) - 1).compressed


def _get_encapsulating_cidr_with_prefix(ip: str, desired_prefix: int) -> str:
    prefix = "/32" if isinstance(ip_address(ip), IPv4Address) else "/128"
    return _get_cidr(ip_network(ip + prefix).supernet(new_prefix=desired_prefix))


def _cidr_overlaps_any(cidr_list: list[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if ip_network(cidr_to_check).overlaps(ip_network(cidr)):
            return True
    return False


def _get_previous_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > get_prefix(cidr):
        return None
    else:
        try:
            return _get_encapsulating_cidr_with_prefix(
                _get_last_ip_in_previous_cidr(
                    _get_cidr(ip_network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


def _get_next_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > get_prefix(cidr):
        return None
    else:
        try:
            return _get_encapsulating_cidr_with_prefix(
                _get_first_ip_in_next_cidr(
                    _get_cidr(ip_network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


def _is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
    return ip_network(child_cidr).subnet_of(ip_network(parent_cidr))


def sort_cidrs(cidrs: list[str]) -> list[str]:
    ret = cidrs.copy()
    ret.sort(key=cmp_to_key(lambda a, b: ip_network(a).compare_networks(ip_network(b))))
    return ret


def get_ip_count(cidr: str) -> int:
    return ip_network(cidr).num_addresses


def get_prefix(cidr: str) -> int:
    return int(cidr.split("/")[1])


def split_out_individual_cidrs(vpcs: list[VPC]) -> list[SingleCIDRVPC]:
    ret = []

    for vpc in vpcs:
        for cidr in vpc.cidrs:
            ret.append(
                SingleCIDRVPC(
                    id=vpc.id,
                    name=vpc.name,
                    cidr=cidr,
                    subnets=[s for s in vpc.subnets if _is_cidr_inside(cidr, s)]
                )
            )

    return ret


def find_subnet_holes(vpc_cidr: str, subnet_cidrs: list[str]) -> list[str]:
    if len(subnet_cidrs) == 0:
        return [vpc_cidr]

    ret = []

    for cidr in subnet_cidrs:
        # Check on the left of the current CIDR
        for new_prefix in range(1, get_prefix(cidr) + 1):
            candidate = _get_previous_cidr_with_prefix(cidr, new_prefix)
            if candidate is not None and \
                    _is_cidr_inside(vpc_cidr, candidate) and \
                    not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                    not _cidr_overlaps_any(ret, candidate):
                ret.append(candidate)

        # Check on the right of the current CIDR
        for new_prefix in range(1, get_prefix(cidr) + 1):
            candidate = _get_next_cidr_with_prefix(cidr, new_prefix)
            if candidate is not None and \
                    _is_cidr_inside(vpc_cidr, candidate) and \
                    not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                    not _cidr_overlaps_any(ret, candidate):
                ret.append(candidate)

    return sort_cidrs(ret)


def break_down_to_desired_prefix(cidrs: list[str], prefix: int) -> tuple[list[str], list[str]]:
    ret = []
    messages = []
    for cidr in cidrs:
        old_prefix = get_prefix(cidr)
        if old_prefix > prefix:
            messages.append((
                f"Note: skipping the CIDR '{cidr}' because its prefix ({old_prefix}) is larger "
                f"than the requested prefix ({prefix})"
            ))
            continue
        elif prefix - old_prefix > 9:
            messages.append((
                f"Warning: skipping the CIDR '{cidr}' because its prefix is only {old_prefix} "
                f"and converting it to a list of CIDRs with a prefix of {prefix} will result "
                f"in a list containing {2**(prefix-old_prefix)} CIDRs!"
            ))
            continue

        for sub in ip_network(cidr).subnets(new_prefix=prefix):
            ret.append(_get_cidr(sub))

    return ret, messages
