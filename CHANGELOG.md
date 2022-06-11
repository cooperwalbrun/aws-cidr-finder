# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Nothing currently!

## v0.2.0 - 2022-06-11

### Added

* Implemented support for IPv6 VPCs via the `--ipv6` CLI flag (by [@cooperwalbrun](https://github.com/cooperwalbrun))

### Changed

* The structure of the JSON output when specifying the `--json` CLI flag now includes VPC names, VPC CIDRs, and informational messages (by [@cooperwalbrun](https://github.com/cooperwalbrun))

### Fixed

* Gracefully handle situations where the requested `--prefix` causes a huge number of CIDRs to be returned (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.2 - 2022-05-08

### Changed

* Enabled querying by a prefix which is lower than at least one prefix in the returned CIDR list (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.1 - 2022-02-20

### Fixed

* Fixed `find_subnet_holes` slowness and incorrectness issues (by [@cooperwalbrun](https://github.com/cooperwalbrun))

## v0.1.0 - 2022-02-17

### Added

* Created the project (by [@cooperwalbrun](https://github.com/cooperwalbrun))
* Implemented the initial functionality of finding subnet "holes" in IPv4 VPCs (by [@cooperwalbrun](https://github.com/cooperwalbrun))
