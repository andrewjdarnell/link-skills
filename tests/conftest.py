"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_skill_repo(temp_dir):
    """Create a sample skill repository structure."""
    repo = temp_dir / "test-skills"
    repo.mkdir()
    
    # Create some valid skills
    for skill_name in ["python-expert", "code-reviewer", "test-writer"]:
        skill_dir = repo / skill_name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n\nA test skill.")
    
    # Create a deprecated skill (should be excluded)
    deprecated = repo / "deprecated" / "old-skill"
    deprecated.mkdir(parents=True)
    (deprecated / "SKILL.md").write_text("# old-skill\n\nDeprecated.")
    
    # Create a misc skill (should be excluded)
    misc = repo / "misc" / "experimental"
    misc.mkdir(parents=True)
    (misc / "SKILL.md").write_text("# experimental\n\nMisc skill.")
    
    # Create a directory without SKILL.md (should be skipped)
    no_skill = repo / "not-a-skill"
    no_skill.mkdir()
    (no_skill / "README.md").write_text("# Not a skill")
    
    return repo


@pytest.fixture
def sample_config_dict(sample_skill_repo, temp_dir):
    """Return a sample configuration dictionary."""
    dest_dir = temp_dir / "destinations" / ".test-ai" / "skills"
    
    return {
        "repositories": [
            {
                "name": "test-skills",
                "path": str(sample_skill_repo),
                "enabled": True,
                "exclude_dirs": ["deprecated", "misc"]
            }
        ],
        "destinations": [
            {
                "path": str(dest_dir),
                "enabled": True
            }
        ],
        "settings": {
            "global_exclude_dirs": ["deprecated", "misc", "node_modules"],
            "duplicate_strategy": "warn",
            "require_skill_md": True,
            "verbose": False
        }
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_skill_repo):
    """Create a sample TOML config file."""
    dest_dir = temp_dir / "destinations" / ".test-ai" / "skills"
    
    config_content = f"""
[[repositories]]
name = "test-skills"
path = "{sample_skill_repo}"
enabled = true
exclude_dirs = ["deprecated", "misc"]

[[destinations]]
path = "{dest_dir}"
enabled = true

[settings]
global_exclude_dirs = ["deprecated", "misc", "node_modules"]
duplicate_strategy = "warn"
require_skill_md = true
verbose = false
"""
    
    config_file = temp_dir / "test-config.toml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def multi_repo_setup(temp_dir):
    """Create multiple skill repositories with overlapping skills."""
    repo1 = temp_dir / "repo1"
    repo1.mkdir()
    
    # Repo 1 skills
    for skill_name in ["skill-a", "skill-b", "common-skill"]:
        skill_dir = repo1 / skill_name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {skill_name} from repo1")
    
    repo2 = temp_dir / "repo2"
    repo2.mkdir()
    
    # Repo 2 skills (with duplicate "common-skill")
    for skill_name in ["skill-c", "skill-d", "common-skill"]:
        skill_dir = repo2 / skill_name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {skill_name} from repo2")
    
    return {"repo1": repo1, "repo2": repo2}
