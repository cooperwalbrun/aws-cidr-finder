from functools import cmp_to_key
from ipaddress import IPv6Network, AddressValueError, IPv6Address
from typing import Optional

from aws_cidr_finder import utilities
from aws_cidr_finder.engine import CIDREngine


def _get_cidr(network: IPv6Network) -> str:
    return str(network)


def _cidr_overlaps_any(cidr_list: list[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if IPv6Network(cidr_to_check).overlaps(IPv6Network(cidr)):
            return True
    return False


def _cidrs_are_adjacent(cidr1: str, cidr2: str) -> bool:
    a = IPv6Network(cidr1)
    b = IPv6Network(cidr2)
    return (int(a[-1]) + 1 == int(b[0])) or (int(b[-1]) + 1 == int(a[0]))


def _get_first_ip_in_next_cidr(cidr: str) -> str:
    return IPv6Address(int(IPv6Network(cidr)[-1]) + 1).compressed


def _get_last_ip_in_previous_cidr(cidr: str) -> str:
    return IPv6Address(int(IPv6Network(cidr)[0]) - 1).compressed


def _get_encapsulating_cidr_with_prefix(ip_address: str, desired_prefix: int) -> str:
    return _get_cidr(IPv6Network(ip_address + "/128").supernet(new_prefix=desired_prefix))


def _get_previous_cidr_with_prefix(cidr: str, desired_prefix: int) -> Optional[str]:
    if desired_prefix > utilities.get_prefix(cidr):
        return None
    else:
        try:
            return _get_encapsulating_cidr_with_prefix(
                _get_last_ip_in_previous_cidr(
                    _get_cidr(IPv6Network(cidr).supernet(new_prefix=desired_prefix))
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
                    _get_cidr(IPv6Network(cidr).supernet(new_prefix=desired_prefix))
                ),
                desired_prefix
            )
        except AddressValueError:
            return None


class IPv6CIDREngine(CIDREngine):
    @staticmethod
    def is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
        return IPv6Network(child_cidr).subnet_of(IPv6Network(parent_cidr))

    @staticmethod
    def sort_cidrs(cidrs: list[str]) -> list[str]:
        ret = cidrs.copy()
        ret.sort(key=cmp_to_key(lambda a, b: IPv6Network(a).compare_networks(IPv6Network(b))))
        return ret

    @staticmethod
    def get_ip_count(cidr: str) -> int:
        return IPv6Network(cidr).num_addresses

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
                        IPv6CIDREngine.is_cidr_inside(vpc_cidr, candidate) and \
                        not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                        not _cidr_overlaps_any(ret, candidate):
                    ret.append(candidate)

            # Check on the right of the current CIDR
            for new_prefix in range(1, utilities.get_prefix(cidr) + 1):
                candidate = _get_next_cidr_with_prefix(cidr, new_prefix)
                if candidate is not None and \
                        IPv6CIDREngine.is_cidr_inside(vpc_cidr, candidate) and \
                        not _cidr_overlaps_any(subnet_cidrs, candidate) and \
                        not _cidr_overlaps_any(ret, candidate):
                    ret.append(candidate)

        return IPv6CIDREngine.sort_cidrs(ret)

    @staticmethod
    def break_down_to_desired_prefix(cidrs: list[str], prefix: int) -> tuple[list[str], list[str]]:
        ret = []
        messages = []
        for cidr in cidrs:
            old_prefix = utilities.get_prefix(cidr)
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

            for sub in IPv6Network(cidr).subnets(new_prefix=prefix):
                ret.append(_get_cidr(sub))

        return ret, messages
