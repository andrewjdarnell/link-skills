"""Tests for skill discovery."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from link_skills import (
    Repository, Settings, discover_skills
)


class TestSkillDiscovery:
    """Test skill discovery in repositories."""
    
    def test_discover_basic_skills(self, sample_skill_repo):
        """Test discovering skills with SKILL.md files."""
        repo = Repository(
            name="test",
            path=sample_skill_repo,
            exclude_dirs=["deprecated", "misc"]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        
        # Should find python-expert, code-reviewer, test-writer
        # Should NOT find deprecated/old-skill, misc/experimental, not-a-skill
        assert len(skills) == 3
        skill_names = {s.name for s in skills}
        assert "python-expert" in skill_names
        assert "code-reviewer" in skill_names
        assert "test-writer" in skill_names
        assert "old-skill" not in skill_names
        assert "experimental" not in skill_names
        assert "not-a-skill" not in skill_names
    
    def test_discover_without_skill_md_requirement(self, sample_skill_repo):
        """Test discovering skills without requiring SKILL.md."""
        repo = Repository(
            name="test",
            path=sample_skill_repo,
            exclude_dirs=["deprecated", "misc"]
        )
        settings = Settings(require_skill_md=False)
        
        skills = discover_skills(repo, settings, verbose=False)
        
        # Should find more directories including not-a-skill
        skill_names = {s.name for s in skills}
        assert "not-a-skill" in skill_names
    
    def test_exclude_deprecated_directory(self, sample_skill_repo):
        """Test that deprecated directory is excluded."""
        repo = Repository(
            name="test",
            path=sample_skill_repo,
            exclude_dirs=["deprecated"]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        skill_names = {s.name for s in skills}
        
        assert "old-skill" not in skill_names
    
    def test_exclude_misc_directory(self, sample_skill_repo):
        """Test that misc directory is excluded."""
        repo = Repository(
            name="test",
            path=sample_skill_repo,
            exclude_dirs=["misc"]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        skill_names = {s.name for s in skills}
        
        assert "experimental" not in skill_names
    
    def test_global_exclude_dirs(self, sample_skill_repo):
        """Test that global exclude dirs are respected."""
        repo = Repository(
            name="test",
            path=sample_skill_repo,
            exclude_dirs=[]  # No repo-specific excludes
        )
        settings = Settings(
            global_exclude_dirs=["deprecated", "misc"],
            require_skill_md=True
        )
        
        skills = discover_skills(repo, settings, verbose=False)
        skill_names = {s.name for s in skills}
        
        assert "old-skill" not in skill_names
        assert "experimental" not in skill_names
    
    def test_nonexistent_repository(self, temp_dir):
        """Test discovering skills in nonexistent repository."""
        repo = Repository(
            name="nonexistent",
            path=temp_dir / "does-not-exist",
            exclude_dirs=[]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        assert len(skills) == 0
    
    def test_empty_repository(self, temp_dir):
        """Test discovering skills in empty repository."""
        empty_repo = temp_dir / "empty"
        empty_repo.mkdir()
        
        repo = Repository(
            name="empty",
            path=empty_repo,
            exclude_dirs=[]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        assert len(skills) == 0
    
    def test_skill_attributes(self, sample_skill_repo):
        """Test that discovered skills have correct attributes."""
        repo = Repository(
            name="test-repo",
            path=sample_skill_repo,
            exclude_dirs=["deprecated", "misc"]
        )
        settings = Settings(require_skill_md=True)
        
        skills = discover_skills(repo, settings, verbose=False)
        skill = next(s for s in skills if s.name == "python-expert")
        
        assert skill.name == "python-expert"
        assert skill.repository == "test-repo"
        assert skill.source_path == sample_skill_repo / "python-expert"
        assert skill.source_path.exists()
