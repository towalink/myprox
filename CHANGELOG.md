# Changelog

All notable changes to this project are documented in this file.


## [Unreleased]

### Added

### Changed

### Fixed


## [0.5.0] - 2022-11-01

### Added

- Support opening Proxmox' VNC console


## [0.4.2] - 2022-10-29

### Changed

- Better memrange wording

### Fixed

- Check node online status only on cluster queries


## [0.4.1] - 2022-10-29

### Fixed

- Only set session cookie secure flag if https is used


## [0.4.0] - 2022-10-29

### Added

- Enhance API with option to provide "full" qemu data
- Also support "false" and "true" for Boolean values in config file

### Changed

- Only query nodes that are online
- Add session security headers
- Use "memrange" attribute in VM list

### Fixed

- Remove redundant line in index template


## [0.3.0] - 2022-09-15

### Added

- Possibility to start a machine from the machine list

### Changed

- Change default to listen also on IPv6
- Change button hover color to better fit color scheme


## [0.2.0] - 2022-09-10

### Added

- Support for dropping privileges after binding to listen port

### Changed

- Improved logging/output on startup

### Fixed

- Disable debug output


## [0.1.0] - 2022-09-09

### Added

- First public release to Github
