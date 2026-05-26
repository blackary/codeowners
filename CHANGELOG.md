# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-26

### Added

- `codeowners-cli` entry point, installable via `uvx codeowners-cli`
- `--only-owners` flag to filter files without owners
- `--output` flag supporting `text`, `csv`, `tsv`, and `json` formats
- `--no-header` flag to omit the header row
- Auto-detection of `CODEOWNERS`, `.github/CODEOWNERS`, and `docs/CODEOWNERS`
