def get_prefix(cidr: str) -> int:
    return int(cidr.split("/")[1])
