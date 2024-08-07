# aws-cidr-finder [![master](https://github.com/cooperwalbrun/aws-cidr-finder/actions/workflows/master.yml/badge.svg)](https://github.com/cooperwalbrun/aws-cidr-finder/actions/workflows/master.yml) [![PyPI](https://img.shields.io/pypi/v/aws-cidr-finder)](https://pypi.org/project/aws-cidr-finder) [![codecov](https://codecov.io/gh/cooperwalbrun/aws-cidr-finder/branch/master/graph/badge.svg?token=DRVM149OYQ)](https://codecov.io/gh/cooperwalbrun/aws-cidr-finder)

1. [Overview](#overview)
   1. [An Example](#an-example)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
   1. [CLI](#cli)
   2. [Python](#python)
5. [Contributing](#contributing)

## Overview

`aws-cidr-finder` is a Python CLI tool and library that finds unused CIDR blocks (either IPv4 or
IPv6) in AWS VPCs. It is a very simple tool, but it can be of great help to users who manage many
subnets across one or more VPCs and do not want to spend the money required to use a solution like
[AWS IPAM](https://docs.aws.amazon.com/vpc/latest/ipam/what-it-is-ipam.html).

### An Example

It is easiest to see the value of this tool through an example. Imagine that we have the following
setup in AWS:

* A VPC whose CIDR is `172.31.0.0/16`, with a `Name` tag of `Hello World`
* Six subnets inside that VPC whose CIDRs are:
  * `172.31.0.0/20`
  * `172.31.16.0/20`
  * `172.31.32.0/20`
  * `172.31.48.0/20`
  * `172.31.64.0/20`
  * `172.31.80.0/20`
* An [AWS CLI profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)
  named `myprofile`

`aws-cidr-finder` allows you to quickly compute the CIDRs that you still have available in the VPC
without having to do a lot of annoying/tedious octet math. If we issue this command:

```bash
aws-cidr-finder --profile myprofile
```

We should see this output:

```
Here are the available CIDR blocks in the 'Hello World' VPC (VPC CIDR block '172.31.0.0/16'):
CIDR               IP Count
---------------  ----------
172.31.96.0/19         8192
172.31.128.0/17       32768
Total                 40960
```

You should notice that, by default, `aws-cidr-finder` will automatically "simplify" the CIDRs
by merging adjacent free CIDR blocks so that the resulting table shows the maximum contiguous space
per CIDR (in other words, the resulting table has the fewest number of rows possible). This is why
the result of the command displayed only two CIDRs: a `/19` and a `/17`.

>Note that the first CIDR is `/19` instead of, for example, `/18`, because the `/18` CIDR would 
>mathematically have to begin at IP address `172.31.64.0`, and that IP address is already taken by a
>subnet!

However, we can change this "simplification" behavior by specifying the `--prefix` CLI flag:

```bash
aws-cidr-finder --profile myprofile --prefix 20
```

Now, the expected output should look something like this:

```
Here are the available CIDR blocks in the 'Hello World' VPC (VPC CIDR block '172.31.0.0/16'):
CIDR               IP Count
---------------  ----------
172.31.96.0/20         4096
172.31.112.0/20        4096
172.31.128.0/20        4096
172.31.144.0/20        4096
172.31.160.0/20        4096
172.31.176.0/20        4096
172.31.192.0/20        4096
172.31.208.0/20        4096
172.31.224.0/20        4096
172.31.240.0/20        4096
Total                 40960
```

With the `--prefix` argument, we can now query our available network space to our desired level of
detail. Note that if we specify a `--prefix` with a value lower than any of the prefixes in the
available CIDRs list, those CIDRs will be skipped. For example, if we run the following:

```bash
aws-cidr-finder --profile myprofile --prefix 18
```

We should see this output:

```
Note: skipping CIDR '172.31.96.0/19' because its prefix (19) is numerically greater than the requested prefix (18)

Here are the available CIDR blocks in the 'Hello World' VPC (VPC CIDR block '172.31.0.0/16'):
CIDR               IP Count
---------------  ----------
172.31.128.0/18       16384
172.31.192.0/18       16384
Total                 32768
```

The CIDR that was skipped was the `172.31.96.0/19` CIDR because it is impossible to convert a `/19`
CIDR into one or more `/18` CIDRs.

## Installation

If you have Python >=3.10 and <4.0 installed, `aws-cidr-finder` can be installed from PyPI using
something like this:

```bash
pip install aws-cidr-finder
```

## Configuration

All that needs to be configured in order to use this CLI is an
[AWS CLI profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) or
a keypair. The former may be specified using the `--profile` argument on the CLI, while the keypair
must be specified in environment variables. If both are available at the same time,
`aws-cidr-finder` will prefer the profile.

The environment variables for the keypair approach are `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, and optionally `AWS_SESSION_TOKEN` (if authenticating with a session).
These are the same environment variables that Boto uses.

You should also ensure that the profile/keypair you are using has the AWS IAM access needed to make
the underlying API calls via Boto. Here is a minimal IAM policy document that fills this
requirement:

```json
{
  "Effect": "Allow",
  "Action": [
    "ec2:DescribeVpcs",
    "ec2:DescribeSubnets"
  ],
  "Resource": "*"
}
```

Read more about the actions shown above
[here](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonec2.html).

## Usage

### CLI

See [An Example](#an-example) above for a detailed demonstration of the CLI interface of this tool.
You can also use `aws-cidr-finder --help` to see command line options.

### Python

Setup:

```python
from aws_cidr_finder import JSONOutput, find_available_cidrs

# All arguments
output: JSONOutput = find_available_cidrs(profile_name="", region="", ipv6=False, desired_prefix=20)

# Minimal arguments (profile-based authentication)
output: JSONOutput = find_available_cidrs(profile_name="")

# Minimal arguments (environment variable-based authentication)
output: JSONOutput = find_available_cidrs()

# Other miscellaneous combinations
output: JSONOutput = find_available_cidrs(profile_name="", ipv6=True)
output: JSONOutput = find_available_cidrs(profile_name="", desired_prefix=16)
output: JSONOutput = find_available_cidrs(region="")
# ...and so on
```

Accessing the CIDR data:

```python
output: JSONOutput = find_available_cidrs(...)  # See above

for message in output["messages"]:
    # Print the messages that would have been written to STDOUT when using the CLI
    print(message)

for cidr in output["cidrs_not_converted_to_prefix"]:
    # If aws-cidr-finder could not convert a given available CIDR block into one or more CIDR blocks
    # with the requested desired_prefix, it will be returned in this list
    # Note: this list is only populated if you passed desired_prefix to find_available_cidrs
    print(f"aws-cidr-finder did not convert the following CIDR block to the desired prefix: {cidr}")
    
for vpc in output["data"]:
    # Print all the information that is available in the VPC dict
    print(f'VPC ID: {vpc["id"]}')
    print(f'VPC Name: {vpc["name"]}')
    print(f'VPC CIDR: {vpc["cidr"]}')
    for cidr in vpc["available_cidr_blocks"]:
        print(f"Available CIDR block: {cidr}")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for developer-oriented information.
