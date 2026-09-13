.PHONY: help install uninstall test test-verbose test-coverage clean lint format check dev-install run dry-run

.DEFAULT_GOAL := help

# Self-documenting Makefile pattern
# Add '##' after target to add help text
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install link-skills to ~/scripts (simple copy method)
	@echo "→ Installing link-skills to ~/scripts..."
	@mkdir -p ~/scripts
	@cp link-skills.sh ~/scripts/link-skills
	@cp link_skills.py ~/scripts/
	@cp pyproject.toml ~/scripts/
	@chmod +x ~/scripts/link-skills
	@echo "✓ Installed successfully!"
	@echo ""
	@echo "Add ~/scripts to your PATH if not already there:"
	@echo "  echo 'export PATH=\"\$$HOME/scripts:\$$PATH\"' >> ~/.zshrc"
	@echo "  source ~/.zshrc"
	@echo ""
	@echo "Then run: link-skills"

install-uv: ## Install as Python package with uv (recommended for Python users)
	@echo "→ Installing link-skills as Python package..."
	@uv tool install .
	@echo "✓ Installed successfully!"
	@echo ""
	@echo "Command available globally: link-skills"
	@echo "To uninstall: uv tool uninstall link-skills"

install-pipx: ## Install globally with pipx (isolated environment)
	@echo "→ Installing link-skills with pipx..."
	@pipx install .
	@echo "✓ Installed successfully!"
	@echo ""
	@echo "Command available globally: link-skills"
	@echo "To uninstall: pipx uninstall link-skills"

install-editable: ## Install in editable mode for development
	@echo "→ Installing link-skills in editable mode..."
	@uv pip install -e .
	@echo "✓ Installed in editable mode!"
	@echo ""
	@echo "Changes to source will be reflected immediately."
	@echo "To uninstall: uv pip uninstall link-skills"

install-bin: ## Install link-skills to ~/bin (alternative simple copy)
	@echo "→ Installing link-skills to ~/bin..."
	@mkdir -p ~/bin
	@cp link-skills.sh ~/bin/link-skills
	@cp link_skills.py ~/bin/
	@cp pyproject.toml ~/bin/
	@chmod +x ~/bin/link-skills
	@echo "✓ Installed successfully!"
	@echo ""
	@echo "Add ~/bin to your PATH if not already there:"
	@echo "  echo 'export PATH=\"\$$HOME/bin:\$$PATH\"' >> ~/.zshrc"
	@echo "  source ~/.zshrc"
	@echo ""
	@echo "Then run: link-skills"

install-config: ## Install example config to ~/.config/link-skills/
	@echo "→ Installing example config..."
	@mkdir -p ~/.config/link-skills
	@cp link-skills-config.example.toml ~/.config/link-skills/config.toml
	@echo "✓ Config installed to ~/.config/link-skills/config.toml"
	@echo ""
	@echo "Edit the config file to add your skill repositories:"
	@echo "  $$EDITOR ~/.config/link-skills/config.toml"

uninstall: ## Remove link-skills from ~/scripts
	@echo "✗ Removing link-skills from ~/scripts..."
	@rm -f ~/scripts/link-skills
	@rm -f ~/scripts/link_skills.py
	@rm -f ~/scripts/pyproject.toml
	@echo "✓ Uninstalled successfully!"

uninstall-uv: ## Uninstall Python package installed with uv
	@echo "✗ Uninstalling link-skills..."
	@uv tool uninstall link-skills
	@echo "✓ Uninstalled successfully!"

uninstall-pipx: ## Uninstall package installed with pipx
	@echo "✗ Uninstalling link-skills..."
	@pipx uninstall link-skills
	@echo "✓ Uninstalled successfully!"

##@ Development

venv: ## Create virtual environment (done automatically by uv)
	@if [ -d .venv ]; then \
		echo "✓ Virtual environment already exists at .venv"; \
	else \
		echo "→ Creating virtual environment..."; \
		uv venv; \
		echo "✓ Virtual environment created at .venv"; \
	fi
	@echo ""
	@echo "Virtual environment is managed automatically by uv."
	@echo "Run 'make dev-install' to install dependencies."

dev-install: ## Install development dependencies with uv
	@echo "→ Installing development dependencies..."
	@uv sync --all-extras
	@echo "✓ Development environment ready!"
	@echo ""
	@echo "Virtual environment: .venv"
	@echo "Activated automatically by 'uv run' commands"

##@ Testing

test: ## Run all tests
	@echo "⋯ Running tests..."
	@uv run pytest

test-verbose: ## Run tests with verbose output
	@echo "⋯ Running tests (verbose)..."
	@uv run pytest -v

test-coverage: ## Run tests with coverage report
	@echo "⋯ Running tests with coverage..."
	@uv run pytest --cov=. --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "→ HTML coverage report: htmlcov/index.html"

test-fast: ## Run tests without coverage (fastest)
	@echo "⋯ Running tests (fast)..."
	@uv run pytest -x --tb=short

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "⋯ Running tests in watch mode..."
	@uv run ptw -- -v

##@ Code Quality

lint: ## Run linting checks
	@echo "⋯ Linting code..."
	@uv run ruff check link_skills.py tests/
	@echo "✓ Linting passed!"

format: ## Format code with ruff
	@echo "→ Formatting code..."
	@uv run ruff format link_skills.py tests/
	@echo "✓ Code formatted!"

check: test lint ## Run tests and linting

##@ Running

run: ## Run link-skills from source
	@./link-skills.sh

dry-run: ## Run link-skills in dry-run mode
	@./link-skills.sh --dry-run

verbose: ## Run link-skills with verbose output
	@./link-skills.sh --verbose

dry-verbose: ## Run link-skills in dry-run mode with verbose output
	@./link-skills.sh --dry-run --verbose

##@ Cleanup

clean: ## Remove build artifacts and cache files
	@echo "⋯ Cleaning up..."
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned!"

clean-all: ## Remove everything including virtual environment
	@echo "⋯ Cleaning everything (including .venv)..."
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@rm -rf .venv
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Everything cleaned! (including virtual environment)"

clean-test: ## Remove test artifacts only
	@echo "⋯ Cleaning test artifacts..."
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@echo "✓ Test artifacts cleaned!"

##@ Documentation

docs: ## Open documentation in browser
	@echo "→ Opening documentation..."
	@if [ -f "README.md" ]; then \
		open README.md || xdg-open README.md || echo "→ See README.md"; \
	fi

docs-testing: ## Open testing documentation
	@echo "→ Opening testing documentation..."
	@if [ -f "TESTING.md" ]; then \
		open TESTING.md || xdg-open TESTING.md || echo "→ See TESTING.md"; \
	fi

##@ Utilities

show-config: ## Show where config file would be loaded from
	@echo "⚙ Config file locations (first found wins):"
	@echo "  1. ~/.config/link-skills/config.toml"
	@echo "  2. ~/scripts/link-skills-config.toml"
	@echo "  3. ./link-skills-config.toml"
	@echo ""
	@echo "Checking for config files..."
	@if [ -f ~/.config/link-skills/config.toml ]; then \
		echo "  ✓ Found: ~/.config/link-skills/config.toml"; \
	else \
		echo "  ✗ Not found: ~/.config/link-skills/config.toml"; \
	fi
	@if [ -f ~/scripts/link-skills-config.toml ]; then \
		echo "  ✓ Found: ~/scripts/link-skills-config.toml"; \
	else \
		echo "  ✗ Not found: ~/scripts/link-skills-config.toml"; \
	fi
	@if [ -f ./link-skills-config.toml ]; then \
		echo "  ✓ Found: ./link-skills-config.toml"; \
	else \
		echo "  ✗ Not found: ./link-skills-config.toml"; \
	fi

version: ## Show version information
	@echo "link-skills version information:"
	@echo "  Version: 2.0.0"
	@echo "  Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "  UV: $$(uv --version 2>/dev/null || echo 'Not installed')"
	@echo "  Pytest: $$(uv run pytest --version 2>/dev/null | head -1 || echo 'Not installed')"

##@ Quick Start

quickstart: install install-config ## Install everything and setup config (simple method)
	@echo ""
	@echo "✓ Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit config: $$EDITOR ~/.config/link-skills/config.toml"
	@echo "  2. Add your skill repositories to the config"
	@echo "  3. Run: link-skills --dry-run (to preview)"
	@echo "  4. Run: link-skills (to actually link)"

quickstart-uv: install-uv install-config ## Install with uv tool (recommended for Python users)
	@echo ""
	@echo "✓ Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit config: $$EDITOR ~/.config/link-skills/config.toml"
	@echo "  2. Add your skill repositories to the config"
	@echo "  3. Run: link-skills --dry-run (to preview)"
	@echo "  4. Run: link-skills (to actually link)"
