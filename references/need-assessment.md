# Need Assessment & Functional Equivalence Guide

## Why Need Assessment Matters
AI Agent skills take up prompt real estate and memory. As skill libraries grow beyond 100+ skills, semantic collision and tool confusion degrade model accuracy. Installing redundant skills degrades the agent instead of empowering it.

## The 4-Tier Overlap Matrix

| Overlap Tier | Definition | Action |
| :--- | :--- | :--- |
| **Exact Duplicate (100%)** | Same name, same tool, identical instructions | 🔴 **Skip Immediately.** Output local path. |
| **High Overlap (70% - 99%)** | Different tool but achieves the exact same job (e.g. `duckduckgo-search` vs existing `n8n-search`) | 🟠 **Skip by default.** Recommend existing stack unless specialized advantage is proven. |
| **Partial Overlap (40% - 69%)** | Shares tools or domain, but introduces distinct workflow or deeper module patterns | 🟡 **Conditional Install.** Install and record synergy notes in commit metadata. |
| **Zero Overlap (0% - 39%)** | Unaddressed capability or new third-party integration | 🟢 **Proceed to Security Scan.** |

## Functional Equivalence Rules
1. **Tooling != Job:** A skill named `slack-bot` (using Slack API) and `slack-automation` (using n8n Slack nodes) perform the same job: interacting with Slack. Check the job, not just the SDK.
2. **Multi-Skill Coverage:** If 2 or 3 existing skills in combination cover the requested capability, the new skill is considered functionally equivalent and should be skipped.
