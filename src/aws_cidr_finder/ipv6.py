from aws_cidr_finder.cidr_finder import CIDRFinder

# TODO


class IPv6CIDRFinder(CIDRFinder):
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
