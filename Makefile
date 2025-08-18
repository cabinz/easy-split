# Makefile for EasySplit
# A bill splitting tool for group trips

# Variables
PYTHON := python3
UV := uv
PIP := pip
PACKAGE_NAME := easy-split
MODULE_NAME := easysplit

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Check if uv is available
HAS_UV := $(shell command -v uv 2> /dev/null)

# Check if we're in a virtual environment
VENV_ACTIVE := $(VIRTUAL_ENV)

# === Installation Commands ===

## install: Build and install package to current Python environment
.PHONY: install
install:
	@echo "$(BLUE)Building and installing $(PACKAGE_NAME)...$(NC)"
ifdef HAS_UV
	@echo "$(GREEN)Using uv for installation$(NC)"
	@uv build
	@uv pip install --system dist/*.whl
else
	@echo "$(YELLOW)uv not found, using pip$(NC)"
	@$(PYTHON) -m build 2>/dev/null || $(PIP) install build && $(PYTHON) -m build
	@$(PIP) install dist/*.whl
endif
	@echo "$(GREEN)✓ $(PACKAGE_NAME) installed successfully!$(NC)"
	@echo "$(GREEN)✓ Command 'splitbill' is now available$(NC)"

## install-dev: Setup complete development environment
.PHONY: install-dev
install-dev:
	@echo "$(BLUE)Setting up development environment...$(NC)"
ifndef HAS_UV
	@echo "$(RED)Error: uv is required for development setup$(NC)"
	@echo "$(YELLOW)Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)"
	@exit 1
endif
	@echo "$(GREEN)Step 1/3: Creating virtual environment...$(NC)"
	@test -d .venv || uv venv
	@echo "$(GREEN)Step 2/3: Installing dependencies...$(NC)"
	@uv sync
	@echo "$(GREEN)Step 3/3: Installing package in editable mode...$(NC)"
	@uv pip install -e .
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo "$(YELLOW)Activate with: source .venv/bin/activate$(NC)"

## uninstall: Uninstall the package
.PHONY: uninstall
uninstall:
	@echo "$(BLUE)Uninstalling $(PACKAGE_NAME)...$(NC)"
ifdef HAS_UV
	@uv pip uninstall $(PACKAGE_NAME) -y 2>/dev/null || true
else
	@$(PIP) uninstall $(PACKAGE_NAME) -y 2>/dev/null || true
endif
	@echo "$(GREEN)✓ $(PACKAGE_NAME) uninstalled$(NC)"

# === Development Commands ===

## test: Run all tests
.PHONY: test
test:
	@echo "$(BLUE)Running tests...$(NC)"
ifdef HAS_UV
	@uv run pytest $(TEST_ARGS)
else
	@echo "$(YELLOW)uv not found, using pytest directly$(NC)"
	@pytest $(TEST_ARGS)
endif

# === Build Commands ===

## build: Build distribution packages (wheel and sdist)
.PHONY: build
build: clean
	@echo "$(BLUE)Building distribution packages...$(NC)"
ifdef HAS_UV
	@uv build
else
	@$(PYTHON) -m build 2>/dev/null || ($(PIP) install build && $(PYTHON) -m build)
endif
	@echo "$(GREEN)✓ Built packages in dist/$(NC)"
	@ls -lh dist/

## clean: Remove build artifacts and cache files
.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf dist/ build/ *.egg-info src/*.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf .pytest_cache/
	@rm -rf .ruff_cache/
	@echo "$(GREEN)✓ Cleaned$(NC)"

## publish: Publish package to PyPI
.PHONY: publish
publish: build
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
ifdef HAS_UV
	@uv publish
else
	@echo "$(YELLOW)Installing twine...$(NC)"
	@$(PIP) install twine
	@twine upload dist/*
endif
	@echo "$(GREEN)✓ Published to PyPI$(NC)"

# === Helper Commands ===

## help: Show this help message
.PHONY: help
help:
	@echo "$(BLUE)EasySplit Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ": "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' | sed 's/## //'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install         # Install for users"
	@echo "  make install-dev     # Setup development environment"
	@echo "  make test           # Run all tests"
	@echo "  make test TEST_ARGS='-v tests/test_auto_detect.py'  # Run specific test"
	@echo ""
ifdef HAS_UV
	@echo "$(GREEN)✓ uv detected$(NC)"
else
	@echo "$(YELLOW)⚠ uv not found - some features limited$(NC)"
endif
ifdef VENV_ACTIVE
	@echo "$(GREEN)✓ Virtual environment active$(NC)"
endif

# Declare all targets as phony to ensure they always run
.PHONY: install install-dev uninstall test build clean publish help