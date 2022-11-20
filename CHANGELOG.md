# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Nothing currently!

## v0.3.2 - 2022-11-20

### Changed

* The `--prefix` argument no longer converts CIDR blocks which would result in more than 256 CIDRs
  (previously this threshold was 1024) (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.3.1 - 2022-11-20

### Changed

* IPv6 subnets in an `associating` state are now recognized by `aws-cidr-finder` (by
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
