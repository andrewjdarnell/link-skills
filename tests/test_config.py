"""Tests for configuration loading and parsing."""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from link_skills import (
    Config, Repository, Destination, Settings,
    load_config, parse_config_file, expand_path, get_default_config
)


class TestExpandPath:
    """Test path expansion."""
    
    def test_expand_tilde(self):
        """Test that ~ expands to home directory."""
        result = expand_path("~/test")
        assert result == Path.home() / "test"
    
    def test_expand_absolute_path(self):
        """Test that absolute paths are resolved."""
        result = expand_path("/tmp/test")
        # Use resolve() to handle macOS symlinks like /tmp -> /private/tmp
        expected = Path("/tmp/test").resolve(strict=False)
        assert result == expected
    
    def test_expand_relative_path(self):
        """Test that relative paths are resolved."""
        result = expand_path("./test")
        assert result.is_absolute()


class TestDefaultConfig:
    """Test default configuration."""
    
    def test_default_config_has_repositories(self):
        """Test that default config includes at least one repository."""
        config = get_default_config()
        assert len(config.repositories) > 0
    
    def test_default_config_has_destinations(self):
        """Test that default config includes standard destinations."""
        config = get_default_config()
        assert len(config.destinations) == 3
        
        paths = [str(d.path) for d in config.destinations]
        assert any(".claude" in p for p in paths)
        assert any(".agents" in p for p in paths)
        assert any(".kiro" in p for p in paths)
    
    def test_default_settings(self):
        """Test that default settings are sensible."""
        config = get_default_config()
        assert config.settings.duplicate_strategy == "warn"
        assert config.settings.require_skill_md is True
        assert "deprecated" in config.settings.global_exclude_dirs


class TestConfigParsing:
    """Test TOML config file parsing."""
    
    def test_parse_valid_config(self, sample_config_file):
        """Test parsing a valid config file."""
        config = parse_config_file(sample_config_file)
        
        assert len(config.repositories) == 1
        assert config.repositories[0].name == "test-skills"
        assert len(config.destinations) == 1
        assert config.settings.duplicate_strategy == "warn"
    
    def test_parse_config_repositories(self, sample_config_file):
        """Test that repositories are parsed correctly."""
        config = parse_config_file(sample_config_file)
        repo = config.repositories[0]
        
        assert repo.name == "test-skills"
        assert repo.enabled is True
        assert "deprecated" in repo.exclude_dirs
        assert "misc" in repo.exclude_dirs
    
    def test_parse_config_destinations(self, sample_config_file):
        """Test that destinations are parsed correctly."""
        config = parse_config_file(sample_config_file)
        dest = config.destinations[0]
        
        assert dest.enabled is True
        assert dest.path.is_absolute()
    
    def test_parse_config_settings(self, sample_config_file):
        """Test that settings are parsed correctly."""
        config = parse_config_file(sample_config_file)
        settings = config.settings
        
        assert settings.duplicate_strategy == "warn"
        assert settings.require_skill_md is True
        assert "deprecated" in settings.global_exclude_dirs
        assert "node_modules" in settings.global_exclude_dirs
    
    def test_parse_missing_file(self, temp_dir):
        """Test that parsing a missing file raises an error."""
        with pytest.raises(FileNotFoundError):
            parse_config_file(temp_dir / "nonexistent.toml")


class TestConfigLoading:
    """Test configuration loading from multiple sources."""
    
    def test_load_specific_config(self, sample_config_file):
        """Test loading a specific config file."""
        config = load_config(sample_config_file, verbose=False)
        assert len(config.repositories) == 1
    
    def test_load_missing_config_uses_defaults(self, temp_dir):
        """Test that missing config falls back to defaults."""
        nonexistent = temp_dir / "nonexistent.toml"
        
        # This should not raise an error when config_file is None
        config = load_config(config_file=None, verbose=False)
        assert len(config.repositories) > 0
        assert len(config.destinations) > 0
    
    def test_disabled_repository_not_loaded(self, temp_dir, sample_skill_repo):
        """Test that disabled repositories are not loaded."""
        config_content = f"""
[[repositories]]
name = "disabled-repo"
path = "{sample_skill_repo}"
enabled = false

[[destinations]]
path = "{temp_dir / 'dest'}"
enabled = true
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)
        
        config = parse_config_file(config_file)
        assert len(config.repositories) == 0
    
    def test_disabled_destination_not_loaded(self, temp_dir, sample_skill_repo):
        """Test that disabled destinations are not loaded."""
        config_content = f"""
[[repositories]]
name = "test-repo"
path = "{sample_skill_repo}"
enabled = true

[[destinations]]
path = "{temp_dir / 'dest'}"
enabled = false
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)
        
        config = parse_config_file(config_file)
        assert len(config.destinations) == 0
