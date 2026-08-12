# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- Aligned the executable gate policy with the framework's five documented release outcomes: Release, Release with conditions, Hold, Do not release, and Defer decision.
- Distinguished remediable missing hard-gate evidence (`hold`) from explicit terminal conditions (`do_not_release`).
- Added explicit decision context for critical failures, prohibited conditions, unacceptable residual risk, and owner-requested deferral.
- Reject malformed Boolean evidence, unknown evidence/context fields, and risk inputs outside the documented 1–5 range instead of silently producing a misleading assessment.

### Changed

- CLI `decision` values now use the framework vocabulary (`release`, `release_with_conditions`, `hold`, `do_not_release`, `defer`) instead of the former three-value go/no-go vocabulary. Existing profile input shape remains valid.

### Added

- Automated unit tests for decision semantics, precedence, CLI serialization, and risk-tier thresholds.
- GitHub Actions CI with read-only repository permissions.
- Basic Python project metadata for reproducible runtime expectations.

## [0.1.0] — Foundation release

### Added

- AI release lifecycle framework for staged governance decisions.
- Release gate review template for staging, production rollout, major model update, or retirement decisions.
- Filled generic sample release gate review artifact.
- Documentation clarifying the relationship between `release-governance` and `release-checklist`.
- README positioning that separates lifecycle governance from executable checklist validation.

### Notes

This repository defines release-stage governance expectations and decision artifacts. It should remain distinct from `release-checklist`, which provides executable YAML validation.

### Next

- Add stage-specific examples for pre-development, pre-deployment, deployment, post-deployment, and retirement.
- Add a release-condition tracker template.
- Add more examples of linking checklist reports to release gate decisions.
