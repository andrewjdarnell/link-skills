# Testing Documentation

## Overview

This project has comprehensive test coverage using pytest, covering configuration, discovery, linking, and full integration workflows.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and test utilities
├── test_config.py        # Configuration loading and parsing tests
├── test_discovery.py     # Skill discovery tests
├── test_linking.py       # Symlink creation and duplicate handling tests
└── test_integration.py   # End-to-end workflow tests
```

## Running Tests

### Basic Usage

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test class
uv run pytest tests/test_linking.py::TestDuplicateHandling

# Run specific test method
uv run pytest tests/test_linking.py::TestDuplicateHandling::test_duplicate_warn_strategy
```

### Coverage Reports

```bash
# Generate coverage report (terminal)
uv run pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Generate multiple report formats
uv run pytest --cov=. --cov-report=term --cov-report=html --cov-report=xml
```

### Useful Options

```bash
# Show local variables in tracebacks
uv run pytest -l

# Stop on first failure
uv run pytest -x

# Run last failed tests
uv run pytest --lf

# Show test durations
uv run pytest --durations=10

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto
```

## Test Categories

### Configuration Tests (`test_config.py`)

Tests for loading and parsing TOML configuration files:

- **Path expansion**: Tilde expansion, absolute/relative paths
- **Default config**: Sensible defaults when no config file exists
- **TOML parsing**: Repositories, destinations, settings
- **Config loading**: Multiple config locations, disabled entries

**Key test cases:**
- `test_expand_tilde`: Home directory expansion
- `test_parse_valid_config`: TOML parsing correctness
- `test_disabled_repository_not_loaded`: Disabled entries are skipped

### Discovery Tests (`test_discovery.py`)

Tests for finding skills in repositories:

- **Basic discovery**: Finding skills with SKILL.md files
- **Exclusion patterns**: Global and per-repo excludes
- **SKILL.md requirement**: Optional vs required
- **Edge cases**: Empty repos, nonexistent paths

**Key test cases:**
- `test_discover_basic_skills`: Find all valid skills
- `test_exclude_deprecated_directory`: Exclusion patterns work
- `test_skill_attributes`: Discovered skills have correct metadata

### Linking Tests (`test_linking.py`)

Tests for creating symlinks and handling edge cases:

- **Basic linking**: Single and multiple skills
- **Duplicate handling**: Warn, skip, overwrite, error strategies
- **Circular symlinks**: Detection and prevention
- **Existing files**: Replacing non-symlink files
- **Multiple destinations**: Linking to multiple target directories
- **Dry run**: Preview mode without changes

**Key test cases:**
- `test_link_single_skill`: Basic symlink creation
- `test_duplicate_warn_strategy`: Duplicate detection works
- `test_detect_circular_symlink`: Prevent circular links
- `test_dry_run_no_changes`: Dry run doesn't modify filesystem

### Integration Tests (`test_integration.py`)

End-to-end workflow tests:

- **Full workflow**: Config → discovery → linking
- **Multi-repository**: Multiple repos with duplicates
- **Edge cases**: Empty repos, disabled repos
- **Dry run**: Preview full workflow

**Key test cases:**
- `test_full_workflow_single_repo`: Complete workflow works
- `test_full_workflow_multi_repo`: Handle multiple repos correctly
- `test_workflow_with_dry_run`: Dry run mode in full workflow

## Fixtures

### `temp_dir`
Creates a temporary directory that's automatically cleaned up after each test.

### `sample_skill_repo`
Creates a realistic skill repository structure with:
- Valid skills: `python-expert`, `code-reviewer`, `test-writer`
- Deprecated skill: `deprecated/old-skill`
- Misc skill: `misc/experimental`
- Directory without SKILL.md: `not-a-skill`

### `sample_config_file`
Creates a valid TOML config file pointing to `sample_skill_repo`.

### `multi_repo_setup`
Creates two repositories with overlapping skills for testing duplicate handling.

## Writing New Tests

### Example Test

```python
def test_new_feature(temp_dir, sample_skill_repo):
    """Test description here."""
    # Arrange
    config = Config(...)
    
    # Act
    result = do_something(config)
    
    # Assert
    assert result == expected_value
```

### Best Practices

1. **Use fixtures**: Leverage existing fixtures for common setup
2. **Test one thing**: Each test should verify one behavior
3. **Descriptive names**: Test names should clearly describe what's tested
4. **Docstrings**: Add docstring explaining the test purpose
5. **Arrange-Act-Assert**: Structure tests clearly
6. **Clean up**: Use fixtures that auto-cleanup (like `temp_dir`)

### macOS Path Considerations

macOS symlinks `/tmp` to `/private/tmp`. When comparing paths with symlinks:

```python
# ❌ May fail on macOS
assert path.resolve() == expected_path

# ✅ Works on macOS
assert path.resolve(strict=False) == expected_path.resolve(strict=False)
```

## Continuous Integration

To set up CI testing:

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv run pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Test Performance

Current test suite runs in ~0.3 seconds:
- 40 tests total
- All tests create temporary filesystems
- No external dependencies or network calls
- Fast feedback loop for development

## Coverage Goals

Target coverage: **90%+**

Current coverage areas:
- ✅ Configuration loading and parsing
- ✅ Skill discovery and filtering
- ✅ Symlink creation and management
- ✅ Duplicate detection and handling
- ✅ Full integration workflows
- ✅ Edge cases and error conditions

## Debugging Tests

### Print Debug Info

```python
def test_something(temp_dir, capsys):
    """Test with debug output."""
    print(f"Temp dir: {temp_dir}")
    result = do_something()
    
    captured = capsys.readouterr()
    print(f"Captured output: {captured.out}")
```

### Interactive Debugging

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Drop into debugger at start of test
uv run pytest --trace
```

### Inspect Temp Directories

```python
def test_with_inspection(temp_dir):
    """Keep temp dir for inspection."""
    # ... test code ...
    
    # Add breakpoint to inspect temp_dir
    import pdb; pdb.set_trace()
```

## Common Issues

### Issue: Tests fail with permission errors
**Solution**: Ensure test creates files in `temp_dir`, not system directories

### Issue: Tests fail inconsistently
**Solution**: Check for test order dependencies, use isolated fixtures

### Issue: Path comparison fails on macOS
**Solution**: Use `.resolve(strict=False)` on both sides of comparison

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass: `uv run pytest`
3. Check coverage: `uv run pytest --cov=.`
4. Update test documentation if needed
