# Smart Backup Routing & Cloud Synchronization

## Routing Hierarchy
When a skill passes inspection and is installed locally, `skill-installer` ensures durable multi-device persistence across four layers:

### Layer 1: Existing Git Repository Sync
- Detects whether the local skills path or workspace is tracked by an existing Git repository (e.g. `Primuez/CLI-Skills-and-MDs`).
- Stages the new skill directory, commits with structured conventional commit syntax (`feat(skills): auto-install <skill-name>`), and pushes to remote.

### Layer 2: Automatic GitHub Backup Repository Provisioning
- If no Git tracking is detected and the GitHub CLI (`gh`) is authenticated, the installer auto-creates a private repository (`<user>/agent-skills-backup`) via `gh repo create`.
- Configures git remote and pushes the initial skill snapshot automatically.

### Layer 3: Cloud Storage & Plugin Synchronization
- If the agent is equipped with cloud storage tools (such as Google Workspace CLI `gws drive` or cloud buckets):
  - Automatically pushes skill bundles to a dedicated `Agent-Skills/` drive folder.
  - Ensures portability for agents operating across containerized or ephemeral cloud runtimes.
