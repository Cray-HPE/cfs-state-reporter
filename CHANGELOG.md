# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Changed how RPM release value is determined

## [1.11.0] - 2023-09-29
### Changed
- Update the spire-agent path

## [1.10.1] - 2023-08-22
### Changed
Updated `cfs-state-reporter` spec file to reflect the fact that it should not be installed without `spire-agent` being present.

## [1.10.0] - 2023-08-18
### Added
- Added rotating file handler to capture output for when syslog fails
- Set connect and read timeout values for all connection objects using sessions

### Changed
- Moved to v3 CFS api

## [1.9.4] - 2023-08-10
### Changed
- RPM OS type changed to `noos`. (CASMCMS-8691)
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds

## [1.9.3] - 2023-06-22
### Added
- Support for SLES SP5

## [1.9.2] - 2023-05-11
### Changed
- RPM builds type changed from `x86_64` to `noarch`. (CASMCMS-8516)
- Spelling corrections.
### Removed
- Removed defunct files leftover from previous versioning system

## [1.9.1] - 2022-12-20
### Added
- Add Artifactory authentication to Jenkinsfile

## [1.8.0] - 2022-07-14
### Added
- Support for SLES SP4

### Changed
- Convert to gitflow/gitversion.
