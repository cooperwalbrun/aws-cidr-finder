from aws_cidr_finder import utilities


def test_find_subnet_holes() -> None:
    vpc_cidr = "172.0.0.0/16"
    allocated_subnet_cidrs = {
        "172.31.0.0/20",
        "172.31.16.0/20",
        "172.31.32.0/20",
        "172.31.48.0/20",
        "172.31.64.0/20",
        "172.31.80.0/20"
    }
    expected_subnet_holes = {
        "172.31.192.0/20",
        "172.31.144.0/20",
        "172.31.176.0/20",
        "172.31.96.0/20",
        "172.31.160.0/20",
        "172.31.208.0/20",
        "172.31.128.0/20",
        "172.31.240.0/20",
        "172.31.112.0/20",
        "172.31.224.0/20"
    }
    assert utilities.find_subnet_holes(vpc_cidr, allocated_subnet_cidrs) == expected_subnet_holes
