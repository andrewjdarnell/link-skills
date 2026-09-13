"""Tests for skill linking."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from link_skills import (
    Repository, Destination, Settings, Skill,
    link_skills, check_circular_symlink
)


class TestCircularSymlink:
    """Test circular symlink detection."""
    
    def test_detect_circular_symlink(self, temp_dir):
        """Test that circular symlinks are detected."""
        repo_path = temp_dir / "repo"
        repo_path.mkdir()
        
        dest_path = temp_dir / "dest"
        dest_path.symlink_to(repo_path)
        
        repos = [Repository(name="test", path=repo_path)]
        
        assert check_circular_symlink(dest_path, repos) is True
    
    def test_regular_directory_not_circular(self, temp_dir):
        """Test that regular directories are not flagged as circular."""
        repo_path = temp_dir / "repo"
        repo_path.mkdir()
        
        dest_path = temp_dir / "dest"
        dest_path.mkdir()
        
        repos = [Repository(name="test", path=repo_path)]
        
        assert check_circular_symlink(dest_path, repos) is False


class TestBasicLinking:
    """Test basic skill linking."""
    
    def test_link_single_skill(self, temp_dir, sample_skill_repo):
        """Test linking a single skill."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skill = Skill(
            name="python-expert",
            source_path=sample_skill_repo / "python-expert",
            repository="test"
        )
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings()
        
        linked, warnings = link_skills(
            [skill],
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 1
        assert warnings == 0
        assert (dest_dir / "python-expert").is_symlink()
        # Use resolve() on both sides to handle macOS symlinks
        assert (dest_dir / "python-expert").resolve(strict=False) == skill.source_path.resolve(strict=False)
    
    def test_link_multiple_skills(self, temp_dir, sample_skill_repo):
        """Test linking multiple skills."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skills = [
            Skill("python-expert", sample_skill_repo / "python-expert", "test"),
            Skill("code-reviewer", sample_skill_repo / "code-reviewer", "test"),
            Skill("test-writer", sample_skill_repo / "test-writer", "test"),
        ]
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings()
        
        linked, warnings = link_skills(
            skills,
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 3
        assert warnings == 0
        assert (dest_dir / "python-expert").is_symlink()
        assert (dest_dir / "code-reviewer").is_symlink()
        assert (dest_dir / "test-writer").is_symlink()
    
    def test_dry_run_no_changes(self, temp_dir, sample_skill_repo):
        """Test that dry run doesn't create symlinks."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skill = Skill(
            name="python-expert",
            source_path=sample_skill_repo / "python-expert",
            repository="test"
        )
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings()
        
        linked, warnings = link_skills(
            [skill],
            destinations,
            [],
            settings,
            dry_run=True,
            verbose=False
        )
        
        assert linked == 1  # Counted as would-be-linked
        assert not (dest_dir / "python-expert").exists()


class TestDuplicateHandling:
    """Test duplicate skill name handling."""
    
    def test_duplicate_warn_strategy(self, temp_dir, multi_repo_setup):
        """Test warn strategy with duplicate skills."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skills = [
            Skill("common-skill", multi_repo_setup["repo1"] / "common-skill", "repo1"),
            Skill("common-skill", multi_repo_setup["repo2"] / "common-skill", "repo2"),
        ]
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings(duplicate_strategy="warn")
        
        linked, warnings = link_skills(
            skills,
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        # First one linked, second warned
        assert linked == 1
        assert warnings == 1
        assert (dest_dir / "common-skill").is_symlink()
        # Should link to first one (repo1) - use resolve() to handle symlinks
        assert (dest_dir / "common-skill").resolve(strict=False) == multi_repo_setup["repo1"].resolve(strict=False) / "common-skill"
    
    def test_duplicate_skip_strategy(self, temp_dir, multi_repo_setup):
        """Test skip strategy with duplicate skills."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skills = [
            Skill("common-skill", multi_repo_setup["repo1"] / "common-skill", "repo1"),
            Skill("common-skill", multi_repo_setup["repo2"] / "common-skill", "repo2"),
        ]
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings(duplicate_strategy="skip")
        
        linked, warnings = link_skills(
            skills,
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        # First one linked, second skipped silently
        assert linked == 1
        assert warnings == 0
    
    def test_duplicate_overwrite_strategy(self, temp_dir, multi_repo_setup):
        """Test overwrite strategy with duplicate skills."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skills = [
            Skill("common-skill", multi_repo_setup["repo1"] / "common-skill", "repo1"),
            Skill("common-skill", multi_repo_setup["repo2"] / "common-skill", "repo2"),
        ]
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings(duplicate_strategy="overwrite")
        
        linked, warnings = link_skills(
            skills,
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        # Both counted as linked (second overwrites first)
        assert linked == 2
        assert warnings == 0
        assert (dest_dir / "common-skill").is_symlink()
        # Should link to second one (repo2) - use resolve() to handle symlinks
        assert (dest_dir / "common-skill").resolve(strict=False) == multi_repo_setup["repo2"].resolve(strict=False) / "common-skill"
    
    def test_duplicate_error_strategy(self, temp_dir, multi_repo_setup):
        """Test error strategy with duplicate skills."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        skills = [
            Skill("common-skill", multi_repo_setup["repo1"] / "common-skill", "repo1"),
            Skill("common-skill", multi_repo_setup["repo2"] / "common-skill", "repo2"),
        ]
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings(duplicate_strategy="error")
        
        with pytest.raises(SystemExit):
            link_skills(
                skills,
                destinations,
                [],
                settings,
                dry_run=False,
                verbose=False
            )


class TestExistingFiles:
    """Test handling of existing files at target locations."""
    
    def test_replace_existing_file(self, temp_dir, sample_skill_repo):
        """Test that existing non-symlink files are replaced."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        # Create an existing file
        existing_file = dest_dir / "python-expert"
        existing_file.write_text("This should be replaced")
        
        skill = Skill(
            name="python-expert",
            source_path=sample_skill_repo / "python-expert",
            repository="test"
        )
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings()
        
        linked, warnings = link_skills(
            [skill],
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 1
        assert (dest_dir / "python-expert").is_symlink()
    
    def test_replace_existing_directory(self, temp_dir, sample_skill_repo):
        """Test that existing directories are replaced."""
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir(parents=True)
        
        # Create an existing directory
        existing_dir = dest_dir / "python-expert"
        existing_dir.mkdir()
        (existing_dir / "file.txt").write_text("content")
        
        skill = Skill(
            name="python-expert",
            source_path=sample_skill_repo / "python-expert",
            repository="test"
        )
        
        destinations = [Destination(path=dest_dir)]
        settings = Settings()
        
        linked, warnings = link_skills(
            [skill],
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 1
        assert (dest_dir / "python-expert").is_symlink()


class TestMultipleDestinations:
    """Test linking to multiple destinations."""
    
    def test_link_to_multiple_destinations(self, temp_dir, sample_skill_repo):
        """Test linking skills to multiple destination directories."""
        dest1 = temp_dir / "dest1"
        dest2 = temp_dir / "dest2"
        dest1.mkdir(parents=True)
        dest2.mkdir(parents=True)
        
        skill = Skill(
            name="python-expert",
            source_path=sample_skill_repo / "python-expert",
            repository="test"
        )
        
        destinations = [
            Destination(path=dest1),
            Destination(path=dest2),
        ]
        settings = Settings()
        
        linked, warnings = link_skills(
            [skill],
            destinations,
            [],
            settings,
            dry_run=False,
            verbose=False
        )
        
        assert linked == 2  # Linked to 2 destinations
        assert (dest1 / "python-expert").is_symlink()
        assert (dest2 / "python-expert").is_symlink()
        # Use resolve() to handle macOS symlinks
        assert (dest1 / "python-expert").resolve(strict=False) == skill.source_path.resolve(strict=False)
        assert (dest2 / "python-expert").resolve(strict=False) == skill.source_path.resolve(strict=False)
