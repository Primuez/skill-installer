---
name: skill-installer
title: Skill Installer
description: Intelligent, security-first package manager for AI Agent Skills. Evaluates functional need, executes NVIDIA SkillSpector security inspection, installs safely, and routes backups to GitHub or cloud storage.
author: Rahul Kasturiya (Primuez)
layer: meta
license: MIT
version: 2.0.0
---

# 🛡️ Skill Installer — Security-First Agent Skill Manager

Skill Installer is an intelligent, security-hardened package manager and workflow engine for discovering, inspecting, installing, and synchronizing AI Agent Skills across Hermes, Claude Code, Antigravity, OpenClaw, and Universal Agent OS.

Unlike naive `curl | bash` or blind copy scripts, **Skill Installer** enforces a strict 3-stage validation pipeline:
1. **Need Assessment & Alternatives Check** — Prevents agent context bloat by checking if your agent already possesses the required capability or functional equivalents.
2. **NVIDIA SkillSpector Security Scan** — Scans skill instructions and executable code for prompt injection, environment variable harvesting, tool poisoning, and reverse shells.
3. **Automated Installation & Smart Backup Routing** — Installs verified skills locally and automatically syncs them to an existing git backup repository, auto-creates a new GitHub backup repo, or uploads to connected cloud storage (e.g., Google Drive via GWS).

---

## ⚡ Quick Start

### Invocations

**Inside an AI Agent Session:**
```
/skill-installer <url-or-local-path>
```

**From the Terminal CLI:**
```bash
# Full 3-stage pipeline: Check -> Scan -> Install & Backup
skill-installer install https://github.com/owner/repo/tree/main/skills/target-skill

# Only check necessity and existing alternatives:
skill-installer check ./target-skill/SKILL.md

# Run NVIDIA SkillSpector security analysis:
skill-installer scan ./target-skill/
```

---

## 🏗️ The 3-Stage Installation Architecture

```
                                  [ Skill Source ]
                       (Git Repo, Raw URL, or Local Folder)
                                         │
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │  STAGE 1: Need Assessment & Alternative Check │
                 └───────────────────────┬───────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
         [ Exact Duplicate ]                         [ Unique / Additive ]
                   │                                           │
                   ▼                                           ▼
             🛑 ABORT INSTALL                        ┌───────────────────┐
      (Report existing alternative)                  │  STAGE 2: Scan    │
                                                     │ NVIDIA SkillSpector
                                                     └─────────┬─────────┘
                                                               │
                                             ┌─────────────────┴─────────────────┐
                                             │                                   │
                                    [ High Risk / Poison ]               [ Safe / Clean ]
                                             │                                   │
                                             ▼                                   ▼
                                       ⛔ QUARANTINE                   ┌───────────────────┐
                                   (Block & alert user)                │ STAGE 3: Install  │
                                                                       │  & Backup Route   │
                                                                       └─────────┬─────────┘
                                                                                 │
                                                   ┌─────────────────────────────┼─────────────────────────────┐
                                                   │                             │                             │
                                                   ▼                             ▼                             ▼
                                        [ Existing Backup Repo ]      [ No Backup Detected ]          [ Cloud Plugin Sync ]
                                         (CLI-Skills-and-MDs)           (Auto-create GitHub            (Google Drive / GWS /
                                         Commit & Push directly          Backup Repository)             S3 Object Storage)
```

---

## 📋 Stage Details

### Stage 1: Need Assessment & Functional Equivalence

Agents suffer from context degradation when flooded with overlapping or redundant skills. Before downloading any code:
- **Core Function Extraction:** Reads the target `SKILL.md` to extract the primary job to be done (not merely the name or library).
- **Redundancy Analysis:** Scans the active agent's skill library for functional overlap:
  - If 2+ existing skills already cover 80%+ of the capability (e.g. requesting `duckduckgo-search` when `n8n-search` + `deep-research` already exist), installation is skipped with an explanatory rationale.
  - If the skill provides a genuine architectural upgrade or fills an unaddressed domain gap, it passes to Stage 2.

### Stage 2: Security Inspection Gate & Inspector Discovery Hierarchy

Agent skills execute with shell and tool privileges. Malicious third-party skills can exfiltrate API keys, execute remote payloads, or hijack agent prompts.

To ensure safety across diverse environments, Skill Installer implements an **adaptive inspector discovery hierarchy**:

1. **Primary Gate (NVIDIA SkillSpector):**
   - Automatically detects NVIDIA SkillSpector binary in PATH or `~/.venv-skillspector/bin/skillspector`.
   - Runs deep AST & semantic scanning for tool poisoning, prompt overrides, and credential harvesting.

2. **Secondary Gate (Alternative Inspector Discovery):**
   - If NVIDIA SkillSpector is not installed as a binary, Skill Installer automatically searches your agent's library for alternative security auditor skills (such as `skill-audit`, `cyber-audit`, or `skill-check`).
   - If found, it routes the skill through multi-phase surface, script, and credential audit rules.

3. **Tertiary Gate (Interactive User Onboarding & Setup):**
   - If NO skill inspector or scanner exists in your system, the agent/CLI prompts the user:
     > *"⚠️ No skill security inspector detected in your system. Third-party skills execute shell commands with agent privileges. Would you like to install NVIDIA SkillSpector? (Recommended)"*
   - Can be automatically installed via `skill-installer setup-inspector` (or `--auto-install-inspector` flag).
   - If declined, it falls back to the built-in static heuristic analyzer with an explicit warning advisory.

### Stage 3: Automated Installation & Smart Backup Routing

Once verified safe, the skill is installed into the agent's active skills directory (`/opt/data/skills/<name>`) and backed up:
1. **Existing Backup Detected:** If a tracking repository exists (e.g. `Primuez/CLI-Skills-and-MDs`), the skill is staged, committed, and pushed with a clean commit message (`feat(skills): auto-install <name>`).
2. **No Backup Setup Found:** The installer leverages the authenticated GitHub CLI (`gh`) to automatically provision a new private backup repository (`agent-skills-backup`), initialize git tracking, and push the initial backup snapshot.
3. **Cloud Storage Plugins:** If configured or connected via plugins (e.g., Google Workspace CLI `gws drive`), the skill directory is automatically synchronized to cloud storage.

---

## 🔧 Configuration & Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HERMES_SKILLS_DIR` | `/opt/data/skills` | Directory where active agent skills reside |
| `SKILLSPECTOR_BIN` | `~/.venv-skillspector/bin/skillspector` | Path to NVIDIA SkillSpector binary |
| `SKILLS_BACKUP_REPO` | `agent-skills-backup` | Default fallback repo name for new backup creation |
| `XDG_CONFIG_HOME` | `~/.config` | Path to GitHub CLI (`gh`) auth configurations |

---

## ⚠️ Security Rules & Best Practices

1. **One-by-One Token Discipline:** Install skills one at a time with dedicated commits to avoid hitting conversational context limits and token rate caps.
2. **Review Precedes Download:** Never bypass Stage 1. Redundant skills bloat prompts and degrade reasoning benchmarks.
3. **No Unprompted Extras:** Only install what is explicitly requested — never wander across remote repositories downloading arbitrary optional bundles.
4. **Interactive Command Bypass:** When invoking external package runners (e.g. `npx skills add`), always supply `-y` to prevent headless agent terminals from hanging on interactive prompts.
