"""Integration tests for full workflow."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from link_skills import (
    load_config, discover_skills, link_skills
)


class TestFullWorkflow:
    """Test complete workflow from config to linking."""
    
    def test_full_workflow_single_repo(self, sample_config_file, temp_dir):
        """Test complete workflow with single repository."""
        # Load config
        config = load_config(sample_config_file, verbose=False)
        
        assert len(config.repositories) == 1
        assert len(config.destinations) == 1
        
        # Discover skills
        all_skills = []
        for repo in config.repositories:
            skills = discover_skills(repo, config.settings, verbose=False)
            all_skills.extend(skills)
        
        assert len(all_skills) == 3
        
        # Link skills
        linked, warnings = link_skills(
            all_skills,
            config.destinations,
            config.repositories,
            config.settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 3
        assert warnings == 0
        
        # Verify links exist
        dest = config.destinations[0].path
        assert (dest / "python-expert").is_symlink()
        assert (dest / "code-reviewer").is_symlink()
        assert (dest / "test-writer").is_symlink()
    
    def test_full_workflow_multi_repo(self, temp_dir, multi_repo_setup):
        """Test complete workflow with multiple repositories."""
        dest_dir = temp_dir / "dest"
        
        # Create config
        config_content = f"""
[[repositories]]
name = "repo1"
path = "{multi_repo_setup['repo1']}"
enabled = true

[[repositories]]
name = "repo2"
path = "{multi_repo_setup['repo2']}"
enabled = true

[[destinations]]
path = "{dest_dir}"
enabled = true

[settings]
global_exclude_dirs = []
duplicate_strategy = "warn"
require_skill_md = true
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)
        
        # Load config
        config = load_config(config_file, verbose=False)
        
        # Discover skills
        all_skills = []
        for repo in config.repositories:
            skills = discover_skills(repo, config.settings, verbose=False)
            all_skills.extend(skills)
        
        # Should have: skill-a, skill-b, common-skill (from repo1),
        #              skill-c, skill-d, common-skill (from repo2)
        assert len(all_skills) == 6
        
        # Link skills
        linked, warnings = link_skills(
            all_skills,
            config.destinations,
            config.repositories,
            config.settings,
            dry_run=False,
            verbose=False
        )
        
        # 5 unique skills linked (common-skill counted once), 1 warning
        assert linked == 5
        assert warnings == 1
        
        # Verify unique skills
        dest = config.destinations[0].path
        assert (dest / "skill-a").is_symlink()
        assert (dest / "skill-b").is_symlink()
        assert (dest / "skill-c").is_symlink()
        assert (dest / "skill-d").is_symlink()
        assert (dest / "common-skill").is_symlink()
    
    def test_workflow_with_dry_run(self, sample_config_file):
        """Test workflow with dry run doesn't make changes."""
        # Load config
        config = load_config(sample_config_file, verbose=False)
        
        # Discover skills
        all_skills = []
        for repo in config.repositories:
            skills = discover_skills(repo, config.settings, verbose=False)
            all_skills.extend(skills)
        
        # Link skills in dry run mode
        linked, warnings = link_skills(
            all_skills,
            config.destinations,
            config.repositories,
            config.settings,
            dry_run=True,
            verbose=False
        )
        
        # Counts are returned but no actual links created
        assert linked > 0
        
        # Verify no links were created
        dest = config.destinations[0].path
        if dest.exists():
            assert not (dest / "python-expert").exists()
    
    def test_workflow_empty_repository(self, temp_dir):
        """Test workflow with empty repository."""
        empty_repo = temp_dir / "empty"
        empty_repo.mkdir()
        
        dest_dir = temp_dir / "dest"
        
        config_content = f"""
[[repositories]]
name = "empty"
path = "{empty_repo}"
enabled = true

[[destinations]]
path = "{dest_dir}"
enabled = true

[settings]
require_skill_md = true
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)
        
        # Load config
        config = load_config(config_file, verbose=False)
        
        # Discover skills
        all_skills = []
        for repo in config.repositories:
            skills = discover_skills(repo, config.settings, verbose=False)
            all_skills.extend(skills)
        
        assert len(all_skills) == 0
        
        # Link skills (should handle empty list gracefully)
        linked, warnings = link_skills(
            all_skills,
            config.destinations,
            config.repositories,
            config.settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 0
        assert warnings == 0
    
    def test_workflow_disabled_repository(self, temp_dir, sample_skill_repo):
        """Test that disabled repositories are not processed."""
        dest_dir = temp_dir / "dest"
        
        config_content = f"""
[[repositories]]
name = "disabled"
path = "{sample_skill_repo}"
enabled = false

[[destinations]]
path = "{dest_dir}"
enabled = true

[settings]
require_skill_md = true
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)
        
        # Load config
        config = load_config(config_file, verbose=False)
        
        # No repositories should be loaded
        assert len(config.repositories) == 0
        
        # Discover skills
        all_skills = []
        for repo in config.repositories:
            skills = discover_skills(repo, config.settings, verbose=False)
            all_skills.extend(skills)
        
        assert len(all_skills) == 0
