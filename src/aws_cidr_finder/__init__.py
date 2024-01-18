from typing import Optional

from importlib_metadata import PackageNotFoundError, version

from aws_cidr_finder import custom_types
from aws_cidr_finder.boto_wrapper import BotoWrapper
from aws_cidr_finder.core import convert_to_json_format

try:
    # We hard-code the name rather than using __name__ because the package name has an underscore
    # instead of a hyphen
    dist_name = "aws-cidr-finder"
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

JSONOutput = custom_types.JSONOutput


def find_cidrs(
    *,
    profile_name: Optional[str] = None,
    region: Optional[str] = None,
    ipv6: bool = False,
    desired_prefix: Optional[int] = None
) -> JSONOutput:
    boto = BotoWrapper(profile_name=profile_name, region=region)
    subnet_cidr_gaps, messages = boto.get_subnet_cidr_gaps(ipv6=ipv6, prefix=desired_prefix)
    return convert_to_json_format(subnet_cidr_gaps, messages)
