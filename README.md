# Heliodoro-repo

**A comprehensive software entitlements, build, and deployment platform for creating, installing, and publishing applications.**

Link sync, merge, build program integrated—fill, establish, publish.

---

## 🚀 Quick Start

### Installation (Development)
```bash
git clone https://github.com/heliodorof44/Heliodoro-repo.git
cd Heliodoro-repo
make install-dev
```

### Installation (Production)
```bash
pip install heliodoro
```

### Build & Test
```bash
# Run tests
make test

# Build distribution packages
make build

# View all commands
make help
```

---

## 📋 Features

✅ **Software Entitlements** — Apache 2.0 licensing with full compliance documentation  
✅ **Automated Build System** — Python setuptools integration with version management  
✅ **Installation Framework** — Development, production, and containerized deployment  
✅ **CI/CD Pipelines** — GitHub Actions for testing, building, and publishing  
✅ **PyPI Publishing** — Automated distribution to Python Package Index  
✅ **Documentation** — MkDocs integration with automatic GitHub Pages deployment  
✅ **Package Management** — Requirements.txt with core, dev, and docs dependencies  

---

## 📁 Repository Structure

```
Heliodoro-repo/
├── README.md                          # This file
├── LICENSE                            # Apache 2.0 License
├── ENTITLEMENTS.md                    # Software entitlements & compliance
├── DEPLOYMENT.md                      # Installation & deployment guide
├── CHANGELOG.md                       # Version history & release notes
├── setup.py                           # Python package configuration
├── requirements.txt                   # Python dependencies
├── Makefile                           # Build automation targets
│
├── src/
│   └── heliodoro/                     # Main package (create this)
│       ├── __init__.py
│       └── cli.py
│
├── tests/                             # Test suite (create this)
│   └── test_basic.py
│
├── docs/                              # Documentation (create this)
│   ├── index.md
│   └── getting-started.md
│
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── support.md                 # Support request template
    └── workflows/
        └── build-and-publish.yml      # CI/CD pipeline
```

---

## 📦 Installation Methods

### 1. From PyPI (Recommended for Users)
```bash
pip install heliodoro
```

### 2. From GitHub (Latest Development)
```bash
pip install git+https://github.com/heliodorof44/Heliodoro-repo.git
```

### 3. From Source (Development)
```bash
git clone https://github.com/heliodorof44/Heliodoro-repo.git
cd Heliodoro-repo
pip install -e ".[dev,docs]"
```

### 4. Docker Container
```bash
docker build -t heliodoro:latest .
docker run heliodoro:latest
```

---

## 🔨 Build & Deployment

### Development Workflow
```bash
# Install with development tools
make install-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

### Building Packages
```bash
# Build source distribution and wheel
make build

# Output:
# dist/heliodoro-0.1.0.tar.gz        (source distribution)
# dist/heliodoro-0.1.0-py3-none-any.whl  (wheel)
```

### Publishing to PyPI
```bash
# Automatic: Push a git tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
# GitHub Actions automatically publishes!

# Manual: Requires PyPI auth
make publish
```

### Documentation
```bash
# Build and serve docs locally
make docs

# Available at http://localhost:8000
```

---

## 📜 Software Entitlements

**License**: Apache License 2.0

**Your rights**:
- ✅ Use for any purpose
- ✅ Modify the source code
- ✅ Distribute original or modified versions
- ✅ Sublicense to others

**Requirements**:
- Include the LICENSE file
- Document all modifications
- Include copyright notices
- Use the same Apache 2.0 license for derivatives

See **ENTITLEMENTS.md** for complete compliance details.

---

## 🔄 CI/CD Workflows

### Automated on Every Push
- Multi-version Python testing (3.9, 3.10, 3.11)
- Linting with flake8
- Code formatting check with black
- Test suite execution
- Code coverage reporting

### Automated on Git Tags
- Build distribution packages
- Publish to PyPI
- Create GitHub Release with artifacts
- Deploy documentation to GitHub Pages

### Automated on Merge to Main
- Run full test suite
- Build documentation
- Update GitHub Pages

---

## 🛠 Configuration

### Environment Variables
Create `.env` file:
```bash
APP_VERSION=0.1.0
APP_ENV=production
DEBUG=false
```

### GitHub Secrets (for Publishing)
1. Go to: Settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN`: Get from https://pypi.org/account/
3. GitHub auto-creates `GITHUB_TOKEN` (no action needed)

---

## 📚 Documentation

- **ENTITLEMENTS.md** — Software licensing, permissions, and compliance
- **DEPLOYMENT.md** — Installation, configuration, and troubleshooting guide
- **CHANGELOG.md** — Version history, release notes, and updates
- **Makefile** — Build targets and automation commands

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_basic.py -v

# Run with markers
pytest -m "integration" tests/
```

---

## 🐛 Troubleshooting

### "No module named 'setuptools'"
```bash
pip install --upgrade setuptools wheel
```

### "PyPI authentication failed"
- Verify `PYPI_API_TOKEN` in GitHub Secrets
- Token should start with `pypi-`
- Check for token expiration at https://pypi.org/account/

### "GitHub Pages not deploying"
- Check Settings → Pages → Deploy from `gh-pages` branch
- Verify workflow has write permissions

See **DEPLOYMENT.md** for more troubleshooting steps.

---

## 📞 Support

- **Issues**: https://github.com/heliodorof44/Heliodoro-repo/issues
- **Discussions**: https://github.com/heliodorof44/Heliodoro-repo/discussions
- **Support Template**: Use the Support/Question issue template

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see LICENSE file for details.

---

## 🎯 Next Steps

1. **Create source structure**: `mkdir -p src/heliodoro tests docs`
2. **Add PyPI token**: Go to Settings → Secrets → Add `PYPI_API_TOKEN`
3. **Configure entitlements**: Review and customize ENTITLEMENTS.md
4. **Push to trigger workflows**: `git push` to run CI/CD pipeline
5. **Create GitHub Release**: Tag and push a version for automated publishing

---

**Built with ❤️ for seamless software distribution and deployment**
