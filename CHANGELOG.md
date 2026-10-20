# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-20

### Changed

- Kept the legacy `fields` API and `rules` payload available for existing consumers.
- Standardized the visible add action as “Add criteria”.

### Added

- Added the public `Criterion` definition and `QueryBuilderWidget(criteria=...)` API.
- Added built-in text, number, date, select, and boolean value inputs.
- Added a custom scalar input renderer registry for application-defined input types.
- Added a flat `{"criteria": [...]}` payload and evaluator support with AND semantics.

## [1.2.2] - 2026-10-13

### Added

- Added `test_evaluation_empty` test.
- Added CI checks for testing.

### Fixed

- Fixed evaluation failing when given an empty dictionary.

## [1.2.1] - 2026-09-14

### Added

- Added `test_evaluation_ignorable_and` and `test_evaluation_ignorable_or` tests.

### Fixed

- Fixed evaluation failing when given a query group with empty rules and an `OR` condition.

## [1.2.0] - 2026-09-12

### Added

- Added a `use_operator` function for field handling.

## [1.1.0] - 2026-09-12

### Added

- Added `evaluate()` for checking conditions against data, returning whether the check passed and, if not, a list of reasons why (e.g. `"Ball completion < 70"`).
- Added `QueryRule` and `QueryGroup` types.
- Added tests.

## [1.0.1] - 2026-09-12

### Changed

- Lowered Python version requirement to >=3.13.

### Removed

- Removed `test.py` file.

## [1.0.0] - 2026-09-12

- Initial release.
