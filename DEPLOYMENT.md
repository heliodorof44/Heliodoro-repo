# Deployment & Configuration Guide

## Prerequisites
- Python 3.9+
- pip and setuptools
- Git
- (Optional) PyPI account for publishing

## 1. Local Installation

### Development Installation
```bash
# Clone repository
git clone https://github.com/heliodorof44/Heliodoro-repo.git
cd Heliodoro-repo

# Install in editable mode with dev dependencies
make install-dev

# Or manually:
pip install -r requirements.txt
pip install -e ".[dev,docs]"
```

### Production Installation
```bash
# Install from PyPI (once published)
pip install heliodoro

# Or from source
make install
```

## 2. Build Process

### Build Distribution Packages
```bash
# Using make
make build

# Or manually
python setup.py sdist bdist_wheel
```

This creates:
- `dist/heliodoro-0.1.0.tar.gz` — Source distribution
- `dist/heliodoro-0.1.0-py3-none-any.whl` — Wheel (binary distribution)

## 3. Configuration

### Environment Variables
Create a `.env` file in the project root:
```bash
# Application configuration
APP_VERSION=0.1.0
APP_ENV=production
DEBUG=false

# PyPI configuration (for publishing)
TWINE_USERNAME=__token__
TWINE_PASSWORD=your-pypi-token-here
```

### Package Configuration
Edit `setup.py` to customize:
- Package name and version
- Author and contact information
- Dependencies and extras
- Entry points and command-line tools

## 4. Testing

### Run Test Suite
```bash
# Using make
make test

# Or manually
pytest tests/ -v --cov=src
```

### Linting & Formatting
```bash
# Check code style
make lint

# Auto-format code
make format
```

## 5. Documentation

### Build Docs Locally
```bash
# Using make
make docs

# Or manually
mkdocs serve
```

Documentation will be available at `http://localhost:8000`

## 6. Publishing

### Publish to PyPI

#### Step 1: Get PyPI API Token
1. Go to https://pypi.org/account/
2. Create API token under "Account settings"
3. Add token to GitHub Secrets as `PYPI_API_TOKEN`

#### Step 2: Create a Git Tag (triggers automated publish)
```bash
# Tag a release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Automated workflow will:
# 1. Build distribution packages
# 2. Publish to PyPI
# 3. Create GitHub Release
# 4. Attach built artifacts
```

#### Step 3: Manual Publishing (if needed)
```bash
# Using make
make publish

# Or manually
pip install twine
twine upload dist/*
```

## 7. Deployment Targets

### As Python Package (PyPI)
- Users can install with: `pip install heliodoro`
- Automatic dependency resolution
- Version management via pip

### As Git Repository
- Users can install directly: `pip install git+https://github.com/heliodorof44/Heliodoro-repo.git`
- Direct access to latest source code
- Easy contribution workflow

### As Docker Container
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python setup.py install
CMD ["heliodoro"]
```

Build and push:
```bash
docker build -t heliodoro:0.1.0 .
docker tag heliodoro:0.1.0 heliodorof44/heliodoro:latest
docker push heliodorof44/heliodoro:latest
```

## 8. GitHub Actions Workflows

### Build Workflow
- Runs on every push and PR
- Tests against Python 3.9, 3.10, 3.11
- Runs linting and tests
- Uploads build artifacts

### Publish Workflow
- Triggered on git tags (`v*`)
- Publishes to PyPI
- Creates GitHub Release
- Attaches distribution files

### Documentation Workflow
- Builds MkDocs on every push to main
- Deploys to GitHub Pages
- Available at `https://heliodorof44.github.io/Heliodoro-repo/`

## 9. Entitlements & Compliance

See `ENTITLEMENTS.md` for:
- License information (Apache 2.0)
- Permissions and conditions
- Compliance checklist
- Distribution requirements

## 10. Quick Start Commands

```bash
# Install and develop locally
make install-dev

# Run tests
make test

# Build and publish locally (requires PyPI auth)
make publish

# Clean all build artifacts
make clean

# View all available commands
make help
```

## Troubleshooting

### "No module named 'setuptools'"
```bash
pip install --upgrade setuptools wheel
```

### "twine: command not found"
```bash
pip install twine
```

### PyPI token authentication failed
- Verify `PYPI_API_TOKEN` secret is set in GitHub
- Token should start with `pypi-`
- Check PyPI account for token expiration

### GitHub Pages not deploying
- Verify `GITHUB_TOKEN` secret exists (auto-created)
- Check "Settings > Pages" is set to deploy from `gh-pages` branch

---

**For detailed help**: See README.md or run `make help`
