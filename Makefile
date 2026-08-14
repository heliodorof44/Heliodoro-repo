.PHONY: help install install-dev build test lint format publish docs clean

help:
	@echo "Heliodoro-repo Build & Deployment Targets"
	@echo "=========================================="
	@echo "make install       - Install package in production mode"
	@echo "make install-dev   - Install package with development dependencies"
	@echo "make build         - Build distribution packages (sdist, wheel)"
	@echo "make test          - Run test suite"
	@echo "make lint          - Run linting (flake8)"
	@echo "make format        - Format code with black"
	@echo "make publish       - Publish to PyPI (requires auth)"
	@echo "make docs          - Build and serve documentation locally"
	@echo "make clean         - Remove build artifacts"

install:
	pip install -r requirements.txt
	pip install .

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev,docs]"

build:
	python setup.py sdist bdist_wheel
	@echo "✓ Build complete. Artifacts in dist/"

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ tests/
	black --check src/ tests/

format:
	black src/ tests/

publish: build
	twine upload dist/*

docs:
	mkdocs serve

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
