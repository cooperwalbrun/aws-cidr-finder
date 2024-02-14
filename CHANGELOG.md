# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Nothing currently!

## v0.6.2 - 2024-02-13

### Fixed

* VPCs with no tags will no longer induce the `KeyError: 'Tags'` error from Boto (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.6.1 - 2024-01-18

### Added

* Added Python-level API documentation to the `find_available_cidrs` function (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.6.0 - 2024-01-18

### Added

* The `find_available_cidrs` function now includes a `cidrs_not_converted_to_prefix` key which
  contains a list of CIDRs that were skipped during the prefix conversion process (note: this is
  only applicable if passing `desired_prefix` to `find_available_cidrs`) (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))
* Python 3.12 is now an official build target with corresponding pipeline assurances (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

### Changed

* The `find_cidrs` function has been renamed to `find_available_cidrs` (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.5.0 - 2024-01-17

### Added

* Added a Python-based API for using `aws-cidr-finder` in a programmatic fashion (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

### Changed

* The JSON format of `aws-cidr-finder`'s output is now simpler: the `aws-cidr-finder-messages` key
  has been changed to `messages`, `vpcs` has been changed to `data`, and the structure of `data` is
  now a flat list of "VPC" `dict`s where each `dict` has the following keys: `id`, `name`, `cidr`,
  and `available_cidr_blocks` (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.4.1 - 2023-10-18

### Changed

* Messages relating to omitted prefixes during the handling of the `--prefix` argument will now
  indicate the VPC to which the omission corresponds (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.4.0 - 2023-10-18

### Added

* Support for an optional `AWS_SESSION_TOKEN` environment variable is now implemented (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

### Fixed

* The `--profile` and `--region` CLI arguments now function as expected (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))
* All CIDRs for VPCs which were omitted during the handling of the `--prefix` flag are now logged
  as expected (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.3.2 - 2022-11-20

### Changed

* The `--prefix` argument no longer converts CIDR blocks which would result in more than 256 CIDRs
  (previously this threshold was 1024) (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.3.1 - 2022-11-20

### Changed

* IPv6 subnet CIDR blocks in an `associating` state are now recognized by `aws-cidr-finder` (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.3.0 - 2022-11-16

### Added

* Added project configuration for using `mypy` to statically type-check code during development and
  in the GitHub Actions pipeline (by [@cooperwalbrun](https://github.com/cooperwalbrun))
* Implemented proper typing throughout the source code and added a `py.typed` file per PEP 561 (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.2.4 - 2022-11-08

### Added

* Added support for Python 3.11 to the pipeline and project configuration (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.2.3 - 2022-10-12

### Changed

* The author email address in the wheel's metadata is now set to a real email address (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.2.2 - 2022-06-13

### Changed

* CIDR blocks that are in an `associating` state (instead of just the `associated` state) will now
  be considered in this CLI's functionality (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.2.1 - 2022-06-11

### Changed

* Refactored the code to reduce code duplication between the IPv4 and IPv6 functionalities (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.2.0 - 2022-06-11

### Added

* Implemented support for IPv6 VPCs via the `--ipv6` CLI flag (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

### Changed

* The structure of the JSON output when specifying the `--json` CLI flag now includes VPC names, VPC
  CIDRs, and informational messages (by [@cooperwalbrun](https://github.com/cooperwalbrun))

### Fixed

* Gracefully handle situations where the requested `--prefix` causes a huge number of CIDRs to be
  returned (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.2 - 2022-05-08

### Changed

* Enabled querying by a prefix which is lower than at least one prefix in the returned CIDR list (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.1 - 2022-02-20

### Fixed

* Fixed `find_subnet_holes` slowness and incorrectness issues (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.0 - 2022-02-17

### Added

* Created the project (by [@cooperwalbrun](https://github.com/cooperwalbrun))
* Implemented the initial functionality of finding subnet "holes" in IPv4 VPCs (by
  [@cooperwalbrun](https://github.com/cooperwalbrun))
