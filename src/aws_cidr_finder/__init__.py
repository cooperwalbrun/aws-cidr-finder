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


def find_available_cidrs(
    *,
    profile_name: Optional[str] = None,
    region: Optional[str] = None,
    ipv6: bool = False,
    desired_prefix: Optional[int] = None
) -> JSONOutput:
    """
    Finds the available CIDR blocks in all VPCs within the target AWS account and region, where the
    target AWS account is determined either via an AWS profile or via environment variables
    containing AWS IAM credentials.

    :param profile_name: The name of the AWS profile to use to authenticate to AWS.
    :param region: The region to target when gathering VPC and subnet CIDR block data. If you omit
                   this argument, this function will target whatever region is configured in the AWS
                   authentication being used to access the AWS API (see above).
    :param ipv6: Whether to gather and output IPv6 CIDR block data (as opposed to IPv4 CIDR block
                 data).
    :param desired_prefix: The desired prefix to which all discovered available CIDR blocks should
                           be converted. Any CIDR block encountered by this function that cannot
                           reasonably be converted to a CIDR block with this desired_prefix will be
                           written to the cidrs_not_converted_to_prefix field of the returned JSON.
    :return: A JSON structure containing informational messages, unconverted CIDR blocks, and VPC
             data (which internally contains the available CIDR blocks of each corresponding VPC).
    """

    boto = BotoWrapper(profile_name=profile_name, region=region)
    subnet_cidr_gaps, cidrs_not_converted_to_prefix, messages = boto.get_subnet_cidr_gaps(
        ipv6=ipv6, prefix=desired_prefix
    )
    return convert_to_json_format(subnet_cidr_gaps, cidrs_not_converted_to_prefix, messages)
