# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Build, install, and deployment infrastructure
- Software entitlements and licensing documentation
- CI/CD workflows for automated testing and publishing
- Documentation site with MkDocs
- Package configuration for PyPI distribution

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [0.1.0] - 2026-08-14

### Added
- Project initialization
- Apache 2.0 licensing
- GitHub Actions workflows
- Setup.py for Python packaging
- Requirements and dependencies
- Makefile for build automation
- ENTITLEMENTS.md for compliance
- DEPLOYMENT.md for installation guide

---

## Release Notes

### Versioning Scheme
- **MAJOR**: Breaking changes, significant features
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, documentation updates

### Release Process
1. Update CHANGELOG.md with changes
2. Bump version in setup.py
3. Create git tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions automatically publishes to PyPI and creates Release

### Installation
```bash
# Install latest release
pip install heliodoro

# Install specific version
pip install heliodoro==0.1.0

# Install from source
pip install git+https://github.com/heliodorof44/Heliodoro-repo.git@v0.1.0
```

### Support & Feedback
- GitHub Issues: https://github.com/heliodorof44/Heliodoro-repo/issues
- Discussions: https://github.com/heliodorof44/Heliodoro-repo/discussions
