from functools import cmp_to_key
from ipaddress import IPv4Network, ip_network


def is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
    return ip_network(child_cidr).subnet_of(ip_network(parent_cidr))


def get_cidr(network: IPv4Network) -> str:
    return str(network)


def sort_cidrs(cidrs: list[str]) -> list[str]:
    cidrs.sort(key=cmp_to_key(lambda a, b: ip_network(a).compare_networks(ip_network(b))))
    return cidrs


def cidr_overlaps_any(cidr_list: set[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if ip_network(cidr_to_check).overlaps(ip_network(cidr)):
            return True
    return False


def merge_adjacent_cidrs(cidrs: set[str]) -> set[str]:
    # TODO - merge subnets which are adjacent and equally-sized
    pass


def find_subnet_holes(vpc_cidr: str, subnet_cidrs: set[str]) -> set[str]:
    """
    The approach taken by this function is to iterate over the given subnet CIDRs, computing its
    immediate "parent" CIDR and checking if that "parent" CIDR overlaps with any other subnet CIDRs.
    If it does, we know that there are no free CIDRs adjacent to that subnet CIDR. If it does NOT,
    then we know that the "parent" CIDR contains at least one CIDR that is considered a "hole" in
    the VPC.
    """

    ret = set()
    for current_subnet_cidr in subnet_cidrs:
        subnet_cidr_mask = int(current_subnet_cidr.split("/")[1])
        for current_prefixlen_diff in range(1, subnet_cidr_mask):
            parent = ip_network(current_subnet_cidr).supernet(prefixlen_diff=current_prefixlen_diff)
            if is_cidr_inside(vpc_cidr, get_cidr(parent)):
                ret = ret.union(
                    set([
                        get_cidr(net)
                        for net in parent.subnets(new_prefix=subnet_cidr_mask)
                        if get_cidr(net) != current_subnet_cidr
                        and not cidr_overlaps_any(subnet_cidrs, get_cidr(net))
                    ])
                )
            else:
                return ret

        return ret
