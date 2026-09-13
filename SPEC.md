# Spec: Link-Skills Configuration Tool

## Overview
A flexible command-line tool that discovers skills across multiple repositories and symlinks them into standard AI coding tool skill directories (Claude, Kiro, Agent Skills, etc.). Lives in `~/scripts` for easy system-wide access.

## Current State
- Single bash script that symlinks skills from its own repository
- Hardcoded to scan `$REPO/skills` directory
- Supports three destinations: `~/.claude/skills`, `~/.agents/skills`, `~/.kiro/skills`
- Excludes `deprecated/` and `misc/` directories
- Based on mattpocock/skills architecture

## Goals

### Primary Goals
1. **Multi-Repository Support**: Configure multiple skill repositories to scan
2. **Flexible Configuration**: Use a config file to define skill sources
3. **Maintainability**: Keep the tool simple and easy to understand
4. **Compatibility**: Maintain compatibility with existing skill directory structures

### Secondary Goals
1. **Selective Syncing**: Option to include/exclude specific skills or repos
2. **Validation**: Check for conflicts and invalid skill structures
3. **Reporting**: Clear output about what was linked and any issues encountered

## Requirements

### Must Have
1. **Configuration File**: YAML configuration file defining skill repositories
2. **Multi-Source Scanning**: Scan multiple repositories for skills
3. **Destination Management**: Support existing destinations plus easy addition of new ones
4. **Safe Linking**: Handle existing files/links without data loss
5. **Clear Output**: Show what was linked, skipped, or had errors

### Should Have
1. **Validation Mode**: Dry-run to preview changes
2. **Conflict Detection**: Warn about duplicate skill names from different repos
3. **Selective Exclusion**: Configure which directories to skip per-repo or globally
4. **Target Filtering**: Option to link to specific destinations only

### Could Have
1. **Auto-Discovery**: Scan common locations for skill repos
2. **Unlink Command**: Remove all symlinks created by this tool
3. **Update Notifications**: Detect when source repos have updates
4. **Skill Priority**: When duplicates exist, define which repo takes precedence

## Design

### Configuration File Structure
Location: `~/scripts/link-skills-config.yaml` or `~/.config/link-skills/config.yaml`

```yaml
# Repositories to scan for skills
repositories:
  - path: ~/src/mattpocock/skills
    name: "mattpocock-skills"
    enabled: true
    exclude_dirs:
      - deprecated
      - misc
    
  - path: ~/src/my-custom-skills
    name: "my-skills"
    enabled: true
    exclude_dirs:
      - experimental
    
  - path: ~/work/team-skills
    name: "team-skills"
    enabled: false  # Can be toggled

# Destinations where skills will be linked
destinations:
  - path: ~/.claude/skills
    enabled: true
  - path: ~/.agents/skills
    enabled: true
  - path: ~/.kiro/skills
    enabled: true

# Global settings
settings:
  # Directories to always exclude (in addition to per-repo exclusions)
  global_exclude_dirs:
    - deprecated
    - misc
    - node_modules
  
  # How to handle duplicate skill names
  duplicate_strategy: "warn"  # Options: warn, skip, overwrite, error
  
  # Validate SKILL.md exists
  require_skill_md: true
```

### Command Line Interface

```bash
# Basic usage - link all configured repos
link-skills

# Dry run - show what would be linked
link-skills --dry-run

# Link specific repository
link-skills --repo mattpocock-skills

# Link to specific destination
link-skills --dest ~/.kiro/skills

# Verbose output
link-skills --verbose

# Initialize config file
link-skills --init

# Validate configuration
link-skills --validate

# List configured repos and destinations
link-skills --list

# Unlink all skills
link-skills --unlink
```

### Behavior Specifications

#### Discovery Process
1. Load configuration file (use defaults if not found)
2. Expand all paths (handle `~` and relative paths)
3. For each enabled repository:
   - Verify path exists
   - Find all directories containing `SKILL.md`
   - Apply exclude filters (global + per-repo)
   - Collect skill name and source path

#### Linking Process
1. For each enabled destination:
   - Create destination directory if it doesn't exist
   - Detect if destination is a symlink to a source repo (error if so)
   - For each discovered skill:
     - Check for existing file/link at target path
     - Handle per duplicate strategy
     - Create symlink from destination to source
     - Report success or failure

#### Conflict Resolution
- **Duplicate skill names**: Use strategy from config (warn, skip, overwrite, error)
- **Existing non-link files**: Always warn, never overwrite without explicit flag
- **Circular symlinks**: Detect and prevent (existing behavior)
- **Missing SKILL.md**: Skip with warning if `require_skill_md: true`

### Output Format

#### Standard Output
```
🔍 Scanning repositories...
  ✓ mattpocock-skills: 42 skills found
  ✓ my-skills: 8 skills found
  ⚠ team-skills: disabled, skipping

📦 Linking skills...
  ~/.claude/skills/
    ✓ python-expert -> ~/src/mattpocock/skills/python-expert
    ✓ code-reviewer -> ~/src/my-custom-skills/code-reviewer
    ⚠ test-writer (duplicate: using mattpocock-skills version)
  
  ~/.kiro/skills/
    ✓ python-expert -> ~/src/mattpocock/skills/python-expert
    ✓ code-reviewer -> ~/src/my-custom-skills/code-reviewer

✅ Successfully linked 50 skills to 2 destinations
⚠️  1 warning (see above)
```

#### Verbose Output
Include:
- Full paths for all operations
- Skipped directories and why
- Timing information
- Configuration values used

### Error Handling
- **Missing config**: Use sensible defaults (current behavior)
- **Invalid YAML**: Clear error message with line number
- **Missing repository**: Warning, continue with others
- **Permission errors**: Report which files/dirs, suggest fixes
- **Symlink failures**: Report skill name and reason

## Implementation Plan

### Phase 1: Configuration Support
1. Add YAML parsing (use `yq` or Python/Ruby if available, else skip to env vars)
2. Define default configuration structure
3. Implement config file loading with fallbacks
4. Add `--init` to create sample config

### Phase 2: Multi-Repository Scanning
1. Refactor skill discovery to accept multiple source paths
2. Add per-repository exclude patterns
3. Implement duplicate detection
4. Add repository-level enable/disable

### Phase 3: Enhanced CLI
1. Add command-line argument parsing
2. Implement `--dry-run` mode
3. Add `--repo` and `--dest` filters
4. Implement `--validate` command

### Phase 4: Polish
1. Improve output formatting
2. Add verbose mode
3. Add `--unlink` functionality
4. Write comprehensive README with examples

## Testing Considerations
- Test with empty config
- Test with non-existent repository paths
- Test duplicate skill names from different repos
- Test with read-only destinations (permission errors)
- Test circular symlink detection
- Test with special characters in paths
- Test backwards compatibility (works without config file)

## Documentation Needs
1. **README**: Updated with new configuration options
2. **Example Config**: Sample YAML with comments
3. **Migration Guide**: For users of the original script
4. **Troubleshooting**: Common issues and solutions

## Open Questions
1. Should the tool support remote repositories (git URLs)?
2. Should it support skill namespacing (prefix with repo name)?
3. Should it track what it has linked (state file)?
4. Should there be a "watch" mode that re-links on file changes?
5. Pure bash vs. rewrite in Python/Ruby for better YAML support?

## Success Criteria
- [ ] Can configure multiple skill repositories via YAML
- [ ] All configured repos are scanned and linked correctly
- [ ] Duplicate skills are handled per configuration
- [ ] Tool works without config file (backwards compatible)
- [ ] Clear, actionable error messages for all failure modes
- [ ] Dry-run mode accurately predicts real run behavior
- [ ] Documentation covers all features with examples
- [ ] Existing users can migrate with minimal friction
