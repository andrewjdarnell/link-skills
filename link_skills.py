#!/usr/bin/env python3
"""
Link-Skills: Multi-repository skill linker for AI coding tools

Links skills from multiple configured repositories into AI tool skill directories.
Supports: Claude, Kiro, Agent Skills, and custom destinations.

Original concept: mattpocock/skills/scripts/link-skills.sh
Enhanced by: Andrew Darnell
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

# Try tomllib (Python 3.11+), fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("✗ Error: TOML parser not found.", file=sys.stderr)
        print("Install tomli: pip3 install tomli", file=sys.stderr)
        print("Or use Python 3.11+ which has built-in tomllib", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Repository:
    """Represents a skill repository."""
    name: str
    path: Path
    enabled: bool = True
    exclude_dirs: List[str] = field(default_factory=list)


@dataclass
class Destination:
    """Represents a destination directory for skills."""
    path: Path
    enabled: bool = True


@dataclass
class Settings:
    """Global settings for skill linking."""
    global_exclude_dirs: List[str] = field(default_factory=lambda: [
        "deprecated", "misc", "node_modules", ".git", "__pycache__", "test", "tests"
    ])
    duplicate_strategy: str = "warn"  # warn, skip, overwrite, error
    require_skill_md: bool = True
    verbose: bool = False


@dataclass
class Config:
    """Complete configuration for link-skills."""
    repositories: List[Repository] = field(default_factory=list)
    destinations: List[Destination] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)


# ============================================================================
# Default Configuration
# ============================================================================

def get_default_config() -> Config:
    """Return default configuration if no config file found."""
    script_dir = Path(__file__).parent.parent
    
    return Config(
        repositories=[
            Repository(
                name="default",
                path=script_dir,
                enabled=True,
                exclude_dirs=["deprecated", "misc"]
            )
        ],
        destinations=[
            Destination(path=Path.home() / ".claude" / "skills"),
            Destination(path=Path.home() / ".agents" / "skills"),
            Destination(path=Path.home() / ".kiro" / "skills"),
        ],
        settings=Settings()
    )


def get_config_paths() -> List[Path]:
    """Return possible config file locations in order of preference."""
    return [
        Path.home() / ".config" / "link-skills" / "config.toml",
        Path.home() / "scripts" / "link-skills-config.toml",
        Path(__file__).parent / "link-skills-config.toml",
    ]


# ============================================================================
# Configuration Loading
# ============================================================================

def expand_path(path_str: str) -> Path:
    """Expand ~ and resolve path."""
    return Path(path_str).expanduser().resolve()


def load_config(config_file: Optional[Path] = None, verbose: bool = False) -> Config:
    """Load configuration from TOML file or use defaults."""
    
    # If specific config file provided, use it
    if config_file:
        if not config_file.exists():
            print(f"✗ Error: Config file not found: {config_file}", file=sys.stderr)
            sys.exit(1)
        config_paths = [config_file]
    else:
        config_paths = get_config_paths()
    
    # Try to find and load config
    for config_path in config_paths:
        if config_path.exists():
            if verbose:
                print(f"📄 Loading config from: {config_path}")
            try:
                return parse_config_file(config_path)
            except Exception as e:
                print(f"⚠️  Warning: Failed to parse config: {e}", file=sys.stderr)
                print("⚠️  Using default configuration", file=sys.stderr)
                return get_default_config()
    
    # No config found, use defaults
    if verbose:
        print("📄 No config file found, using defaults")
    return get_default_config()


def parse_config_file(config_path: Path) -> Config:
    """Parse TOML config file."""
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    
    # Parse repositories
    repositories = []
    for repo_data in data.get("repositories", []):
        if repo_data.get("enabled", True):
            repositories.append(Repository(
                name=repo_data["name"],
                path=expand_path(repo_data["path"]),
                enabled=True,
                exclude_dirs=repo_data.get("exclude_dirs", [])
            ))
    
    # Parse destinations
    destinations = []
    for dest_data in data.get("destinations", []):
        if dest_data.get("enabled", True):
            destinations.append(Destination(
                path=expand_path(dest_data["path"]),
                enabled=True
            ))
    
    # Parse settings
    settings_data = data.get("settings", {})
    settings = Settings(
        global_exclude_dirs=settings_data.get("global_exclude_dirs", Settings().global_exclude_dirs),
        duplicate_strategy=settings_data.get("duplicate_strategy", "warn"),
        require_skill_md=settings_data.get("require_skill_md", True),
        verbose=settings_data.get("verbose", False)
    )
    
    return Config(
        repositories=repositories,
        destinations=destinations,
        settings=settings
    )


# ============================================================================
# Skill Discovery
# ============================================================================

@dataclass
class Skill:
    """Represents a discovered skill."""
    name: str
    source_path: Path
    repository: str


def discover_skills(repo: Repository, settings: Settings, verbose: bool = False) -> List[Skill]:
    """Discover all skills in a repository."""
    
    if not repo.path.exists():
        print(f"⚠ Warning: Repository not found: {repo.path}")
        return []
    
    if not repo.path.is_dir():
        print(f"⚠ Warning: Not a directory: {repo.path}")
        return []
    
    skills = []
    all_exclude_dirs = set(settings.global_exclude_dirs + repo.exclude_dirs)
    
    if verbose:
        print(f"  ⋯ Scanning: {repo.path}")
    
    # Walk directory tree
    for root, dirs, files in os.walk(repo.path):
        root_path = Path(root)
        
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in all_exclude_dirs]
        
        # Check if this directory contains SKILL.md
        if settings.require_skill_md:
            if "SKILL.md" in files:
                skill_name = root_path.name
                skills.append(Skill(
                    name=skill_name,
                    source_path=root_path,
                    repository=repo.name
                ))
        else:
            # Any directory is a potential skill
            # But skip if it's the repo root
            if root_path != repo.path:
                skill_name = root_path.name
                skills.append(Skill(
                    name=skill_name,
                    source_path=root_path,
                    repository=repo.name
                ))
    
    print(f"✓ {repo.name}: {len(skills)} skills found")
    return skills


# ============================================================================
# Skill Linking
# ============================================================================

def check_circular_symlink(dest: Path, repos: List[Repository]) -> bool:
    """Check if destination is a symlink into one of the source repos."""
    if not dest.is_symlink():
        return False
    
    try:
        resolved = dest.resolve(strict=False)
        for repo in repos:
            repo_resolved = repo.path.resolve(strict=False)
            if resolved == repo_resolved or repo_resolved in resolved.parents:
                print(f"✗ Error: {dest} is a symlink into repository ({resolved})", file=sys.stderr)
                print(f"Remove it: rm \"{dest}\"", file=sys.stderr)
                return True
    except Exception:
        pass
    
    return False


def link_skills(
    skills: List[Skill],
    destinations: List[Destination],
    repositories: List[Repository],
    settings: Settings,
    dry_run: bool = False,
    verbose: bool = False
) -> tuple[int, int]:
    """
    Link skills to all destinations.
    
    Returns:
        tuple: (total_linked, total_warnings)
    """
    total_linked = 0
    total_warnings = 0
    seen_skills: Dict[str, str] = {}  # key: "dest:skill_name", value: repo_name
    
    for dest in destinations:
        print(f"\n→ Linking to: {dest.path}")
        
        # Check for circular symlink
        if check_circular_symlink(dest.path, repositories):
            sys.exit(1)
        
        # Create destination directory
        if not dry_run:
            dest.path.mkdir(parents=True, exist_ok=True)
        else:
            if verbose:
                print(f"  [DRY RUN] Would create: {dest.path}")
        
        # Link each skill
        for skill in skills:
            target = dest.path / skill.name
            dup_key = f"{dest.path}:{skill.name}"
            
            # Check for duplicates
            if dup_key in seen_skills:
                if settings.duplicate_strategy == "warn":
                    print(f"  ⚠ {skill.name} (duplicate: skipping {skill.repository}, using {seen_skills[dup_key]})")
                    total_warnings += 1
                    continue
                elif settings.duplicate_strategy == "skip":
                    continue
                elif settings.duplicate_strategy == "error":
                    print(f"✗ Error: Duplicate skill: {skill.name} (from {skill.repository} and {seen_skills[dup_key]})", file=sys.stderr)
                    sys.exit(1)
                elif settings.duplicate_strategy == "overwrite":
                    # Continue to link (will overwrite)
                    pass
            
            seen_skills[dup_key] = skill.repository
            
            # Handle existing non-symlink files
            if target.exists() and not target.is_symlink():
                if not dry_run:
                    if target.is_dir():
                        import shutil
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                if verbose:
                    print(f"  [removed existing file] {skill.name}")
            
            # Create symlink
            if not dry_run:
                if target.is_symlink():
                    target.unlink()
                target.symlink_to(skill.source_path)
                if verbose:
                    print(f"  ✓ {skill.name} -> {skill.source_path}")
            else:
                print(f"  [DRY RUN] Would link: {skill.name} -> {skill.source_path}")
            
            total_linked += 1
    
    return total_linked, total_warnings


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Link-Skills: Multi-repository skill linker for AI coding tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Config file locations (first found wins):
  ~/.config/link-skills/config.toml
  ~/scripts/link-skills-config.toml
  ./link-skills-config.toml

Without a config file, defaults to linking from current repo to:
  ~/.claude/skills
  ~/.agents/skills
  ~/.kiro/skills
"""
    )
    
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to config file (overrides default locations)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config, args.verbose)
    except Exception as e:
        print(f"✗ Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Override verbose setting if specified on command line
    if args.verbose:
        config.settings.verbose = True
    
    # Show configuration if verbose
    if config.settings.verbose:
        print("\n⚙ Configuration:")
        print(f"  Repositories: {len(config.repositories)}")
        for repo in config.repositories:
            print(f"    - {repo.name}: {repo.path}")
        print(f"  Destinations: {len(config.destinations)}")
        for dest in config.destinations:
            print(f"    - {dest.path}")
        print(f"  Duplicate strategy: {config.settings.duplicate_strategy}")
        print(f"  Require SKILL.md: {config.settings.require_skill_md}")
        print()
    
    # Discover skills
    print("⋯ Scanning repositories...")
    all_skills = []
    for repo in config.repositories:
        skills = discover_skills(repo, config.settings, config.settings.verbose)
        all_skills.extend(skills)
    
    if not all_skills:
        print("\n⚠ No skills found in any repository")
        sys.exit(0)
    
    # Link skills
    total_linked, total_warnings = link_skills(
        all_skills,
        config.destinations,
        config.repositories,
        config.settings,
        dry_run=args.dry_run,
        verbose=config.settings.verbose
    )
    
    # Summary
    print()
    if args.dry_run:
        print(f"→ [DRY RUN] Would link {total_linked} skills to {len(config.destinations)} destination(s)")
    else:
        print(f"✓ Successfully linked {total_linked} skills to {len(config.destinations)} destination(s)")
    
    if total_warnings > 0:
        print(f"⚠ {total_warnings} warning(s) - see above")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
