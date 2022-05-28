import abc


# This is an interface to provide an abstraction over common functionality between IPv4 and IPv6
# support in this module
class CIDRFinder(abc.ABC):
    @staticmethod
    def sort_cidrs(cidrs: list[str]) -> list[str]:
        pass

    @staticmethod
    def get_ip_count(cidr: str) -> int:
        pass

    @staticmethod
    def find_subnet_holes(vpc_cidr: str, subnet_cidrs: list[str]) -> list[str]:
        pass

    @staticmethod
    def break_down_to_desired_prefix(cidrs: list[str], prefix: int, json_output: bool) -> list[str]:
        pass
