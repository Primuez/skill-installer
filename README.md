<div align="center">

# 🛡️ Skill Installer
### The Intelligent, Security-First Package Manager for AI Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Security: NVIDIA SkillSpector](https://img.shields.io/badge/Security-NVIDIA_SkillSpector-76B900.svg)](https://github.com/NVIDIA/skillspector)
[![Agent Ready](https://img.shields.io/badge/Agents-Hermes_|_Claude_|_Antigravity-8A2BE2.svg)](#supported-runtimes)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Stop skill bloat. Block malicious prompt injections. Automatically back up your agent skills across machines.**

[Features](#-key-features) • [Installation](#-quick-start) • [Architecture](#-architecture) • [CLI Usage](#-cli-usage) • [Supported Runtimes](#-supported-runtimes)

</div>

---

## 💡 Why Skill Installer?

AI Agent skills (such as those for **Hermes**, **Claude Code**, **Antigravity**, and **OpenClaw**) give autonomous agents superhuman capabilities. However, modern agent skill adoption faces three major pitfalls:

1. ⚠️ **Context Bloat & Semantic Collision:** Installing dozens of overlapping skills pollutes the agent's system prompt, causing tool hallucinations and benchmark score degradation.
2. 🚨 **Supply Chain & Security Vulnerabilities:** Third-party skills execute terminal and tool commands with the agent's permissions. Rogue skills can harvest API keys, scan `.env` secrets, or open reverse shells.
3. ☁️ **Fragmented Backups & Lost Work:** Skills installed in ephemeral containers or cloud instances vanish upon restart unless reliably tracked and backed up to version control or cloud drives.

**Skill Installer solves all three.**

---

## ⚡ Key Features

- 🔍 **Stage 1 — Need Assessment & Alternative Discovery:** Analyzes the target skill's functional purpose against your existing library. If your agent already possesses functional equivalents covering >80% of the capability, it prevents duplicate installation.
- 🛡️ **Stage 2 — Adaptive Security Inspection Gate:**
  - **NVIDIA SkillSpector Integration:** Runs AST and semantic scanning for prompt injection, environment harvesting, and reverse shells.
  - **Alternative Inspector Discovery:** If SkillSpector is missing, automatically scans your system for alternative security skills (such as `skill-audit` or `cyber-audit`) and uses their security rules.
  - **Interactive Setup Prompt:** If no inspector exists anywhere on your system, prompts you: *"No skill inspector detected. Would you like to install NVIDIA SkillSpector?"* with one-click automated setup (`skill-installer setup-inspector`).
  - **Heuristic Fallback:** Gracefully falls back to a built-in static analyzer so you are never left unprotected.
- 🚀 **Stage 3 — Automated Installation & Multi-Target Backup:**
  - Installs verified skills locally to your agent's directory.
  - **Existing Backup Detection:** Syncs automatically to your existing git repository (e.g., `CLI-Skills-and-MDs`).
  - **Zero-Config GitHub Repo Provisioning:** If no backup repo exists, automatically provisions a new private GitHub repository via `gh` CLI.
  - **Cloud Plugin Sync:** Syncs to connected cloud storage (e.g. Google Drive via Google Workspace CLI `gws drive`).

---

## 🏗️ Architecture

```
                          [ Skill Source ]
                (GitHub Raw URL, Git Repo, or Local Folder)
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │  STAGE 1: Need Assessment & Functional Check    │
          │  - Extract core task capability                 │
          │  - Compare against 1,000+ local agent skills    │
          └────────────────────────┬────────────────────────┘
                                   │
             ┌─────────────────────┴─────────────────────┐
             │                                           │
   [ Duplicate / Overlap ]                      [ Distinct & Needed ]
             │                                           │
             ▼                                           ▼
       🛑 SKIP INSTALL                         ┌───────────────────┐
    (Report existing stack)                    │  STAGE 2: Scan    │
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
                             ┌─────────────────────────────────────────────┼─────────────────────────────┐
                             │                                             │                             │
                             ▼                                             ▼                             ▼
                  [ Existing Git Backup ]                       [ No Backup Repo Found ]      [ Cloud Storage Sync ]
                  (Commit & push directly)                       (Auto-create GitHub repo      (Google Drive via GWS
                                                                  via `gh repo create`)         or S3 storage plugins)
```

---

## 🚀 Quick Start

### 1. Installation

Clone this repository or install the executable directly:

```bash
git clone https://github.com/Primuez/skill-installer.git ~/.skill-installer
sudo ln -s ~/.skill-installer/bin/skill-installer /usr/local/bin/skill-installer
```

### 2. Optional: Setup NVIDIA SkillSpector Engine

For deep security scanning, install NVIDIA's official scanner:

```bash
python3 -m venv ~/.venv-skillspector
~/.venv-skillspector/bin/pip install git+https://github.com/NVIDIA/skillspector.git
```
*(If omitted, Skill Installer automatically falls back to its built-in static regex security analyzer).*

---

## 💻 CLI Usage

### Install a Skill (Full 3-Stage Pipeline)
```bash
skill-installer install https://github.com/owner/repo/tree/main/skills/docker-deploy
```

### Assess Need Only (Dry Run)
Check if your agent already has tools that perform this job without downloading:
```bash
skill-installer check ./new-skill/SKILL.md
```

### Security Scan Only
Scan any local skill directory for malicious patterns:
```bash
skill-installer scan ./suspicious-skill/
```

### Force Installation
Override alternative warnings for specialized variants:
```bash
skill-installer install https://github.com/owner/repo/tree/main/skills/special-tool --force
```

---

## 🤖 Using Inside Agent Sessions

Skill Installer is packaged as a native Agent Skill. In **Hermes**, **Claude Code**, or **Antigravity**, simply type:

```
/skill-installer https://github.com/NousResearch/hermes-agent/tree/main/skills/pdf
```

The agent will automatically load `skill-installer`, perform the 3-stage verification, show the security audit report, and commit the verified skill to your backup repository.

---

## 🌐 Supported Runtimes

| Runtime | Support Level | Integration Method |
| :--- | :---: | :--- |
| **Hermes Agent** (Nous Research) | 🟢 Native | Native Skill (`/skill-installer`) & CLI |
| **Claude Code** (Anthropic) | 🟢 Native | Agent Skill & CLI runner |
| **Antigravity** (Google DeepMind) | 🟢 Native | Background CLI daemon & Agent Tool |
| **Universal Agent OS** (`npx skills`) | 🟢 Native | Multi-agent symlinking & sync |
| **OpenClaw** | 🟢 Native | Shell / Workspace tool |

---

## 🤝 Contributing

Contributions are warmly welcomed! Feel free to:
1. Open an issue for feature suggestions or new security rule heuristics.
2. Submit a PR with enhancements to backup providers (e.g. S3, Dropbox, IPFS).

---

## 📄 License

MIT License © 2026 [Rahul Kasturiya (Primuez)](https://github.com/Primuez).
Feel free to use, modify, and distribute this software for personal or commercial projects.
