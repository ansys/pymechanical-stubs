# CHANGELOG

This document follows the conventions laid out in [Keep a CHANGELOG](https://keepachangelog.com/en/1.0.0).

This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/pymechanical-stubs/tree/main/doc/changelog.d/>.

<!-- towncrier release notes start -->

## [2024.1.0](https://github.com/ansys/pymechanical-stubs/releases/tag/v2024.1.0) - 2024-11-08


### Fixed

- Create stubs one version at a time [#84](https://github.com/ansys/pymechanical-stubs/pull/84)


### Maintenance

- update CHANGELOG for v0.1.4 [#83](https://github.com/ansys/pymechanical-stubs/pull/83)

## [0.1.4](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.4) - 2024-10-22


### Fixed

- rework ci_cd and add `import Ansys` to `__init__.py` files [#81](https://github.com/ansys/pymechanical-stubs/pull/81)


### Maintenance

- update CHANGELOG for v0.1.3 [#79](https://github.com/ansys/pymechanical-stubs/pull/79)

## [0.1.3](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.3) - 2024-10-21


### Fixed

- remove index action [#77](https://github.com/ansys/pymechanical-stubs/pull/77)
- remove stubs importer from init file [#78](https://github.com/ansys/pymechanical-stubs/pull/78)


### Maintenance

- update CHANGELOG for v0.1.2 [#76](https://github.com/ansys/pymechanical-stubs/pull/76)

## [0.1.2](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.2) - 2024-10-16


### Fixed

- wheelhouse steps and changelog files [#63](https://github.com/ansys/pymechanical-stubs/pull/63)
- alphabetize documentation and adjust references [#68](https://github.com/ansys/pymechanical-stubs/pull/68)
- remove `ansys.mechanical.stubs.v###` from class name [#72](https://github.com/ansys/pymechanical-stubs/pull/72)
- replace `submodule` and `subpackage` with `module` [#73](https://github.com/ansys/pymechanical-stubs/pull/73)
- Change C# types to Python [#75](https://github.com/ansys/pymechanical-stubs/pull/75)


### Maintenance

- update CHANGELOG for v0.1.1 [#62](https://github.com/ansys/pymechanical-stubs/pull/62)
- update messages for pre-commit.ci [#65](https://github.com/ansys/pymechanical-stubs/pull/65)
- pre-commit automatic update [#66](https://github.com/ansys/pymechanical-stubs/pull/66), [#67](https://github.com/ansys/pymechanical-stubs/pull/67), [#69](https://github.com/ansys/pymechanical-stubs/pull/69), [#70](https://github.com/ansys/pymechanical-stubs/pull/70), [#74](https://github.com/ansys/pymechanical-stubs/pull/74)
- bump ansys/actions from 7 to 8 [#71](https://github.com/ansys/pymechanical-stubs/pull/71)

## [0.1.1](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.1) - 2024-08-21


### Added

- make PDF documentation [#48](https://github.com/ansys/pymechanical-stubs/pull/48)


### Fixed

- add sudo in front of apt install [#55](https://github.com/ansys/pymechanical-stubs/pull/55)

## [0.1.0](https://github.com/ansys/pymechanical-stubs/releases/tag/v0.1.0) - 2024-08-21


### Added

- Mechanical stubs to sphinx documentation (#1)
- Create workflow to create & post sphinx documentation (#7)
- feat: generate pymechanical-stubs & its Sphinx documentation for 23.2 [#16](https://github.com/ansys/pymechanical-stubs/pull/16)
- feat: generate mechanical stubs in setup.py & add 241 docs [#22](https://github.com/ansys/pymechanical-stubs/pull/22)
- docs: generate documentation for 2024 R2 [#30](https://github.com/ansys/pymechanical-stubs/pull/30)
- technical review [#31](https://github.com/ansys/pymechanical-stubs/pull/31)
- feat: migrate to ruff for linting and style [#32](https://github.com/ansys/pymechanical-stubs/pull/32)
- add doc-deploy-changelog to workflow [#44](https://github.com/ansys/pymechanical-stubs/pull/44)


### Changed

- toctree adjustments (#9)
- Update landing page (#11)
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
