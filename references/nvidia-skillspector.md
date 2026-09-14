# Security Inspection Architecture & Inspector Discovery Hierarchy

## Adaptive Discovery Hierarchy
When an agent or developer invokes `skill-installer`, the tool ensures security through an adaptive multi-tier hierarchy:

```
                  ┌──────────────────────────────────────────────┐
                  │ 1. Is NVIDIA SkillSpector installed in PATH  │
                  │    or ~/.venv-skillspector/bin/skillspector? │
                  └──────────────────────┬───────────────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │                               │
                       [YES]                            [NO]
                         │                               │
                         ▼                               ▼
                 Run NVIDIA AST &          ┌───────────────────────────┐
                 Semantic Analysis         │ 2. Check for Alternative  │
                                           │    Inspector Skills       │
                                           │    (e.g., skill-audit)    │
                                           └─────────────┬─────────────┘
                                                         │
                                         ┌───────────────┴───────────────┐
                                         │                               │
                                       [YES]                            [NO]
                                         │                               │
                                         ▼                               ▼
                              Execute Multi-Phase             ┌───────────────────────────┐
                              Audit Framework                 │ 3. Prompt User:           │
                                                              │    "Install SkillSpector?"│
                                                              └─────────────┬─────────────┘
                                                                            │
                                                            ┌───────────────┴───────────────┐
                                                            │                               │
                                                          [YES]                            [NO]
                                                            │                               │
                                                            ▼                               ▼
                                                   Run 1-Click Setup:             Built-in Heuristic
                                                   ~/.venv-skillspector            Static Analyzer
```

## Threat Vector Analysis for Agent Skills
Agent skills are fundamentally executable prompt instructions combined with scripts and tools. They operate with elevated agent privileges:
- Direct shell and terminal access
- Environment variables containing frontier LLM API keys, database credentials, and cloud tokens
- Network access via `curl`, `fetch`, or HTTP tools

## Threat Vectors Scanned
1. **Environment Harvesting:**
   Patterns scanning `/proc`, `env`, `os.environ`, `.env`, or dumping bash history.
2. **Reverse Shells & Piped Execution:**
   Commands utilizing `curl ... | bash`, `nc -e`, Python socket reverse shells, or `/dev/tcp`.
3. **Tool Poisoning & System Prompt Overrides:**
   Hidden unicode or instructions in markdown designed to override model guardrails or redirect outputs to malicious remote servers.
4. **Credential Exfiltration:**
   Silent transmission of sensitive local paths (e.g. `~/.ssh`, `~/.aws/credentials`, `~/.config/gh`) to third-party endpoints.

## Scoring & Quarantine Policy
- **Risk Score 0-39 (LOW):** Verified clean. Auto-install permitted.
- **Risk Score 40-69 (MEDIUM):** Informational warnings (e.g., unusual network calls). Manual inspection recommended.
- **Risk Score 70+ / Severity HIGH or CRITICAL:** Installation blocked immediately. Skill quarantined to prevent agent infection.
