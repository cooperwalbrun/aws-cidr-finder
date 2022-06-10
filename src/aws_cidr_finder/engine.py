import abc


# This is an interface to provide an abstraction over common functionality between IPv4 and IPv6
# support in this application
class CIDREngine(abc.ABC):
    @staticmethod
    def is_cidr_inside(parent_cidr: str, child_cidr: str) -> bool:
        pass

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
    def break_down_to_desired_prefix(cidrs: list[str], prefix: int) -> tuple[list[str], list[str]]:
        pass
