from functools import cmp_to_key
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from typing import Optional

from aws_cidr_finder import utilities
from aws_cidr_finder.cidr_finder import CIDRFinder


def _is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
    return IPv4Network(child_cidr).subnet_of(IPv4Network(parent_cidr))


def _get_cidr(network: IPv4Network) -> str:
    return str(network)


def _cidr_overlaps_any(cidr_list: list[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if IPv4Network(cidr_to_check).overlaps(IPv4Network(cidr)):
            return True
    return False


def _cidrs_are_adjacent(cidr1: str, cidr2: str) -> bool:
    a = IPv4Network(cidr1)
    b = IPv4Network(cidr2)
    return (int(a[-1]) + 1 == int(b[0])) or (int(b[-1]) + 1 == int(a[0]))


def _get_first_ip_in_next_cidr(cidr: str) -> str:
    return str(IPv4Address(int(IPv4Network(cidr)[-1]) + 1))


def _get_last_ip_in_previous_cidr(cidr: str) -> str:
    return str(IPv4Address(int(IPv4Network(cidr)[0]) - 1))


def _get_encapsulating_cidr_with_prefix(ip_address: str, desired_prefix: int) -> str:
    return _get_cidr(IPv4Network(ip_address + "/32").supernet(new_prefix=desired_prefix))


def _get_previous_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > utilities.get_prefix(cidr):
        return None
    else:
        try:
            return _get_encapsulating_cidr_with_prefix(
                _get_last_ip_in_previous_cidr(
                    _get_cidr(IPv4Network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


def _get_next_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > utilities.get_prefix(cidr):
        return None
    else:
        try:
            return _get_encapsulating_cidr_with_prefix(
                _get_first_ip_in_next_cidr(
                    _get_cidr(IPv4Network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


class IPv4CIDRFinder(CIDRFinder):
    @staticmethod
    def sort_cidrs(cidrs: list[str]) -> list[str]:
        ret = cidrs.copy()
        ret.sort(key=cmp_to_key(lambda a, b: IPv4Network(a).compare_networks(IPv4Network(b))))
        return ret

    @staticmethod
    def get_ip_count(cidr: str) -> int:
        return IPv4Network(cidr).num_addresses

    @staticmethod
    def find_subnet_holes(vpc_cidr: str, subnet_cidrs: list[str]) -> list[str]:
        if len(subnet_cidrs) == 0:
            return [vpc_cidr]

        ret = []

        for cidr in subnet_cidrs:
            # Check on the left of the current CIDR
            for new_prefix in range(1, utilities.get_prefix(cidr) + 1):
                candidate = _get_previous_cidr_with_prefix(cidr, new_prefix)
                if candidate is not None and \
                        _is_cidr_inside(vpc_cidr, candidate) and \
                        not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                        not _cidr_overlaps_any(ret, candidate):
                    ret.append(candidate)

            # Check on the right of the current CIDR
            for new_prefix in range(1, utilities.get_prefix(cidr) + 1):
                candidate = _get_next_cidr_with_prefix(cidr, new_prefix)
                if candidate is not None and \
                        _is_cidr_inside(vpc_cidr, candidate) and \
                        not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                        not _cidr_overlaps_any(ret, candidate):
                    ret.append(candidate)

        return IPv4CIDRFinder.sort_cidrs(ret)

    @staticmethod
    def break_down_to_desired_prefix(cidrs: list[str], prefix: int, json_output: bool) -> list[str]:
        filtered_cidrs = [cidr for cidr in cidrs if utilities.get_prefix(cidr) <= prefix]

        filtered_count = len(cidrs) - len(filtered_cidrs)

        if filtered_count > 0 and not json_output:
            if filtered_count == 1:
                print((
                    f"Note: skipping {filtered_count} CIDR because its prefix is larger than the "
                    f"requested prefix ({prefix})."
                ))
            else:
                print((
                    f"Note: skipping {filtered_count} CIDRs because their prefixes are larger than "
                    f"the requested prefix ({prefix})."
                ))
            print()

        ret = []
        for cidr in filtered_cidrs:
            for sub in IPv4Network(cidr).subnets(new_prefix=prefix):
                ret.append(_get_cidr(sub))

        return ret
