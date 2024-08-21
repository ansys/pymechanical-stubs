# CHANGELOG

This document follows the conventions laid out in [Keep a CHANGELOG](https://keepachangelog.com/en/1.0.0).

This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/pymechanical-stubs/tree/main/doc/changelog.d/>.

<!-- towncrier release notes start -->

## [0.1.0](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.0) - 2024-08-21


### Added

- feat: generate pymechanical-stubs & its Sphinx documentation for 23.2 [#16](https://github.com/ansys/pymechanical-stubs/pull/16)
- feat: generate mechanical stubs in setup.py & add 241 docs [#22](https://github.com/ansys/pymechanical-stubs/pull/22)
- docs: generate documentation for 2024 R2 [#30](https://github.com/ansys/pymechanical-stubs/pull/30)
- technical review [#31](https://github.com/ansys/pymechanical-stubs/pull/31)
- feat: migrate to ruff for linting and style [#32](https://github.com/ansys/pymechanical-stubs/pull/32)
- add doc-deploy-changelog to workflow [#44](https://github.com/ansys/pymechanical-stubs/pull/44)


### Changed

- maint: bump dependencies in workflow [#24](https://github.com/ansys/pymechanical-stubs/pull/24)
- Bump actions/upload-artifact from 3 to 4 [#25](https://github.com/ansys/pymechanical-stubs/pull/25)


### Fixed

- fix: update API documentation [#26](https://github.com/ansys/pymechanical-stubs/pull/26)
- fix: wheel files and README.rst [#27](https://github.com/ansys/pymechanical-stubs/pull/27)
- fix: file cleaning scripts [#28](https://github.com/ansys/pymechanical-stubs/pull/28)
- multi-line method descriptions [#39](https://github.com/ansys/pymechanical-stubs/pull/39)
- no need to set the value for TYPE_CHECKING [#41](https://github.com/ansys/pymechanical-stubs/pull/41)
- make `ansys-pythonnet` a build dependency [#42](https://github.com/ansys/pymechanical-stubs/pull/42)
- only run on tags (not on release branch) [#43](https://github.com/ansys/pymechanical-stubs/pull/43)
- add permissions and environment to release job [#46](https://github.com/ansys/pymechanical-stubs/pull/46)


### Maintenance

- bump ansys/actions from 6 to 7 [#38](https://github.com/ansys/pymechanical-stubs/pull/38)
- enable step for public release and use trusted publisher [#40](https://github.com/ansys/pymechanical-stubs/pull/40)

## [Unreleased][]

### Added

- Mechanical stubs to sphinx documentation (#1)
- Create workflow to create & post sphinx documentation (#7)

### Changed

- toctree adjustments (#9)
- Update landing page (#11)

### Fixed

### Dependencies
