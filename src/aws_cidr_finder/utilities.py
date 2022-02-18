import sys
from functools import cmp_to_key
from ipaddress import IPv4Network, ip_network


def is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
    return ip_network(child_cidr).subnet_of(ip_network(parent_cidr))


def get_cidr(network: IPv4Network) -> str:
    return str(network)


def sort_cidrs(cidrs: list[str]) -> list[str]:
    ret = cidrs.copy()
    ret.sort(key=cmp_to_key(lambda a, b: ip_network(a).compare_networks(ip_network(b))))
    return ret


def cidr_overlaps_any(cidr_list: list[str], cidr: str) -> bool:
    for cidr_to_check in cidr_list:
        if ip_network(cidr_to_check).overlaps(ip_network(cidr)):
            return True
    return False


def cidrs_are_adjacent(cidr1: str, cidr2: str) -> bool:
    a = ip_network(cidr1)
    b = ip_network(cidr2)
    return (int(a[-1]) + 1 == int(b[0])) or (int(b[-1]) + 1 == int(a[0]))


def get_mask(cidr: str) -> int:
    return int(cidr.split("/")[1])


def get_ip_count(cidr: str) -> int:
    return ip_network(cidr).num_addresses


def break_down_to_desired_mask(cidrs: list[str], mask: int) -> list[str]:
    for cidr in cidrs:
        if get_mask(cidr) > mask:
            messages = [
                f"Desired mask ({mask}) is incompatible with the available CIDR blocks! ",
                (
                    f"Encountered a CIDR whose mask is {get_mask(cidr)}, which is higher than  "
                    f"{mask}. Offending CIDR: {cidr}"
                ),
                "Run the command again without the --masks argument to see the full list."
            ]
            for message in messages:
                print(message, file=sys.stderr)
            exit(1)

    ret = []
    for cidr in cidrs:
        for sub in ip_network(cidr).subnets(new_prefix=mask):
            ret.append(get_cidr(sub))

    return ret


def merge_adjacent_cidrs(cidrs: list[str]) -> list[str]:
    if len(cidrs) > 1:
        sorted_cidrs = sort_cidrs(cidrs)
        merged_cidrs = []
        recurse = False

        for i in range(len(cidrs) - 1):
            cidr = sorted_cidrs[i]
            next_cidr = sorted_cidrs[i + 1]

            def append() -> None:
                if not cidr_overlaps_any(merged_cidrs, cidr):
                    merged_cidrs.append(cidr)
                if i == len(cidrs) - 2 and not cidr_overlaps_any(merged_cidrs, next_cidr):
                    # We are at the end of the list, and since we only iterate until len(cidrs) - 1,
                    # we have ot add the last CIDR now
                    merged_cidrs.append(next_cidr)

            if cidrs_are_adjacent(cidr, next_cidr) and \
                    1 <= get_mask(cidr) == get_mask(next_cidr) <= 32:
                merged = ip_network(cidr).supernet(prefixlen_diff=1)
                if merged[0] == ip_network(cidr)[0] and merged[-1] == ip_network(next_cidr)[-1]:
                    if not cidr_overlaps_any(merged_cidrs, get_cidr(merged)):
                        merged_cidrs.append(get_cidr(merged))
                        i += 1
                        recurse = True
                else:
                    append()
            else:
                append()

        if recurse:
            return merge_adjacent_cidrs(merged_cidrs)
        else:
            return merged_cidrs
    else:
        return cidrs


def find_subnet_holes(vpc_cidr: str, subnet_cidrs: list[str]) -> list[str]:
    """
    The approach taken by this function is to iterate over the given subnet CIDRs, computing its
    immediate "parent" CIDR and checking if that "parent" CIDR overlaps with any other subnet CIDRs.
    If it does, we know that there are no free CIDRs adjacent to that subnet CIDR. If it does NOT,
    then we know that the "parent" CIDR contains at least one CIDR that is considered a "hole" in
    the VPC.
    """

    ret = []
    for current_subnet_cidr in subnet_cidrs:
        subnet_cidr_mask = get_mask(current_subnet_cidr)
        for current_prefixlen_diff in range(1, subnet_cidr_mask):
            parent = ip_network(current_subnet_cidr).supernet(prefixlen_diff=current_prefixlen_diff)
            if is_cidr_inside(vpc_cidr, get_cidr(parent)):
                for net in parent.subnets(new_prefix=subnet_cidr_mask):
                    net_cidr = get_cidr(net)
                    if not cidr_overlaps_any(subnet_cidrs, net_cidr) and net_cidr not in ret:
                        ret.append(net_cidr)
            else:
                return ret

        return ret
