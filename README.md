# aws-cidr-finder ![master](https://github.com/cooperwalbrun/aws-cidr-finder/workflows/master/badge.svg) ![PyPI](https://img.shields.io/pypi/v/aws-cidr-finder)

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage-cli)
5. [Contributing](#contributing)

## Overview

`aws-cidr-finder` is a Python CLI tool which finds unused CIDR blocks (IPv4 only currently) in your
AWS VPCs and outputs them to STDOUT. It is very simple, but can be quite useful for users who manage
many subnets across one or more VPCs.

## Installation

If you have Python >=3.10 and <4.0 installed, `aws-cidr-finder` can be installed from PyPI using
something like

```bash
pip install aws-cidr-finder
```

## Configuration

All that needs to be configured in order to use this CLI is an AWS profile or keypair. The former
may be specified using the `--profile` argument on the CLI, while the keypair must be specified in
environment variables. If both are available simultaneously, `aws-cidr-finder` will prefer the AWS
profile.

The environment variables for the keypair approach are `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` respectively.

## Usage

TODO

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for developer-oriented information.
