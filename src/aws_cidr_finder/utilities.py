import sys
from functools import cmp_to_key
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from typing import Optional


def is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
    return IPv4Network(child_cidr).subnet_of(IPv4Network(parent_cidr))


def get_cidr(network: IPv4Network) -> str:
    return str(network)


def sort_cidrs(cidrs: list[str]) -> list[str]:
    ret = cidrs.copy()
    ret.sort(key=cmp_to_key(lambda a, b: IPv4Network(a).compare_networks(IPv4Network(b))))
    return ret


def cidr_overlaps_any(cidr_list: list[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if IPv4Network(cidr_to_check).overlaps(IPv4Network(cidr)):
            return True
    return False


def cidrs_are_adjacent(cidr1: str, cidr2: str) -> bool:
    a = IPv4Network(cidr1)
    b = IPv4Network(cidr2)
    return (int(a[-1]) + 1 == int(b[0])) or (int(b[-1]) + 1 == int(a[0]))


def get_prefix(cidr: str) -> int:
    return int(cidr.split("/")[1])


def get_ip_count(cidr: str) -> int:
    return IPv4Network(cidr).num_addresses


def get_last_ip_in_previous_cidr(cidr: str) -> str:
    return str(IPv4Address(int(IPv4Network(cidr)[0]) - 1))


def get_first_ip_in_next_cidr(cidr: str) -> str:
    return str(IPv4Address(int(IPv4Network(cidr)[-1]) + 1))


def break_down_to_desired_prefix(cidrs: list[str], prefix: int) -> list[str]:
    for cidr in cidrs:
        if get_prefix(cidr) > prefix:
            messages = [
                f"Desired prefix ({prefix}) is incompatible with the available CIDR blocks! ",
                (
                    f"Encountered a CIDR whose prefix is {get_prefix(cidr)}, which is higher than  "
                    f"{prefix}. Offending CIDR: {cidr}"
                ),
                "Run the command again without the --prefix argument to see the full list."
            ]
            for message in messages:
                print(message, file=sys.stderr)
            exit(1)

    ret = []
    for cidr in cidrs:
        for sub in IPv4Network(cidr).subnets(new_prefix=prefix):
            ret.append(get_cidr(sub))

    return ret


def get_encapsulating_cidr_with_prefix(ip_address: str, desired_prefix: int) -> str:
    return get_cidr(IPv4Network(ip_address + "/32").supernet(new_prefix=desired_prefix))


def get_previous_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > get_prefix(cidr):
        return None
    else:
        try:
            return get_encapsulating_cidr_with_prefix(
                get_last_ip_in_previous_cidr(
                    get_cidr(IPv4Network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


def get_next_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > get_prefix(cidr):
        return None
    else:
        try:
            return get_encapsulating_cidr_with_prefix(
                get_first_ip_in_next_cidr(
                    get_cidr(IPv4Network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


def find_subnet_holes(vpc_cidr: str, subnet_cidrs: list[str]) -> list[str]:
    if len(subnet_cidrs) == 0:
        return [vpc_cidr]

    ret = []

    for cidr in subnet_cidrs:
        # Check on the left of the current CIDR
        for new_prefix in range(1, get_prefix(cidr) + 1):
            candidate = get_previous_cidr_with_prefix(cidr, new_prefix)
            if candidate is not None and is_cidr_inside(vpc_cidr, candidate) and \
                    not cidr_overlaps_any(subnet_cidrs, candidate) and \
                    not cidr_overlaps_any(ret, candidate):
                ret.append(candidate)

        # Check on the right of the current CIDR
        for new_prefix in range(1, get_prefix(cidr) + 1):
            candidate = get_next_cidr_with_prefix(cidr, new_prefix)
            if candidate is not None and is_cidr_inside(vpc_cidr, candidate) and \
                    not cidr_overlaps_any(subnet_cidrs, candidate) and \
                    not cidr_overlaps_any(ret, candidate):
                ret.append(candidate)

    return sort_cidrs(ret)
