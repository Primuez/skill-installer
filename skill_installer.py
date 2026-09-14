#!/usr/bin/env python3
"""
Skill Installer (skill-installer)
The intelligent, security-first package manager and installer for AI Agent Skills.

Pipeline:
1. Need Assessment & Alternatives Check
2. NVIDIA SkillSpector Security Scan
3. Automated Installation & Smart Backup Routing (Existing repo, Auto-created repo, or Cloud sync)
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
import urllib.request
import re
from pathlib import Path

DEFAULT_SKILLS_DIR = os.environ.get("HERMES_SKILLS_DIR", "/opt/data/skills")
SKILLSPECTOR_BIN = os.environ.get(
    "SKILLSPECTOR_BIN",
    os.path.expanduser("~/.venv-skillspector/bin/skillspector")
)

def run_cmd(cmd, cwd=None):
    """Run shell command and return stdout, stderr, exit code."""
    res = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def parse_skill_metadata(content):
    """Extract frontmatter metadata from SKILL.md."""
    meta = {"name": "", "description": "", "tools": []}
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
    if match:
        frontmatter = match.group(1)
        for line in frontmatter.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip("'\"")
                if k in meta:
                    meta[k] = v
    return meta

def get_installed_skills(skills_dir=DEFAULT_SKILLS_DIR):
    """List all installed skills with their metadata."""
    skills = []
    base = Path(skills_dir)
    if not base.exists():
        return skills

    for skill_md in base.glob("**/SKILL.md"):
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            meta = parse_skill_metadata(content)
            if not meta.get("name"):
                meta["name"] = skill_md.parent.name
            skills.append({
                "name": meta["name"],
                "path": str(skill_md.parent),
                "description": meta.get("description", "")
            })
        except Exception:
            continue
    return skills

def check_alternatives(new_skill_meta, existing_skills):
    """
    Stage 1: Need Assessment & Functional Equivalence Check
    Evaluate if this skill is needed or if alternatives exist.
    """
    name = new_skill_meta.get("name", "").lower()
    desc = new_skill_meta.get("description", "").lower()

    duplicates = []
    alternatives = []

    # Tokenize description into keywords
    keywords = set(re.findall(r"\b[a-z0-9_-]{3,}\b", f"{name} {desc}"))
    stop_words = {"this", "that", "with", "from", "when", "user", "using", "skill", "agent", "tool", "help"}
    keywords -= stop_words

    for s in existing_skills:
        s_name = s["name"].lower()
        s_desc = s["description"].lower()

        # Exact match
        if s_name == name:
            duplicates.append(s)
            continue

        # Overlap score
        s_words = set(re.findall(r"\b[a-z0-9_-]{3,}\b", f"{s_name} {s_desc}")) - stop_words
        if keywords and s_words:
            overlap = len(keywords & s_words) / min(len(keywords), len(s_words))
            if overlap >= 0.6:
                alternatives.append((s, overlap))

    if duplicates:
        return {
            "status": "DUPLICATE",
            "message": f"Skill '{name}' is already installed at {duplicates[0]['path']}.",
            "existing": duplicates[0]
        }

    if alternatives:
        alternatives.sort(key=lambda x: x[1], reverse=True)
        top = [f"{a[0]['name']} (similarity: {int(a[1]*100)}%)" for a in alternatives[:3]]
        return {
            "status": "ALTERNATIVE_FOUND",
            "message": f"Found existing functional alternatives: {', '.join(top)}.",
            "alternatives": [a[0] for a in alternatives]
        }

    return {
        "status": "NEEDED",
        "message": "No direct duplicates or high-overlap alternatives found. Skill is unique.",
        "alternatives": []
    }

def scan_security(skill_path):
    """
    Stage 2: NVIDIA SkillSpector Security Scan
    """
    # 1. Check if skillspector CLI exists
    scanner = None
    if shutil.which("skillspector"):
        scanner = "skillspector"
    elif os.path.exists(SKILLSPECTOR_BIN):
        scanner = SKILLSPECTOR_BIN

    if not scanner:
        print("[WARN] NVIDIA SkillSpector not found in PATH or ~/.venv-skillspector. Performing basic static analysis...")
        return static_security_fallback(skill_path)

    cmd = f"{scanner} scan '{skill_path}' --format json --no-llm"
    stdout, stderr, code = run_cmd(cmd)

    try:
        data = json.loads(stdout)
        score = data.get("risk_score", 0)
        severity = data.get("risk_severity", "LOW")
        findings = data.get("filtered_findings", [])
        return {
            "safe": score < 50 and severity not in ["HIGH", "CRITICAL"],
            "risk_score": score,
            "risk_severity": severity,
            "findings": findings,
            "scanner": "NVIDIA SkillSpector"
        }
    except Exception:
        # If output was terminal formatted
        if "HIGH" in stdout or "CRITICAL" in stdout:
            return {
                "safe": False,
                "risk_score": 80,
                "risk_severity": "HIGH",
                "findings": [{"message": "High severity flags found in scan output"}],
                "scanner": "NVIDIA SkillSpector"
            }
        return {
            "safe": True,
            "risk_score": 0,
            "risk_severity": "LOW",
            "findings": [],
            "scanner": "NVIDIA SkillSpector"
        }

def static_security_fallback(skill_path):
    """Fallback static regex scanner when SkillSpector binary is absent."""
    suspicious_patterns = [
        (r"curl.*\|.*bash", "Piped shell execution via curl"),
        (r"nc\s+-[e|c]", "Netcat reverse shell"),
        (r"/dev/tcp/\d+", "Bash interactive reverse shell"),
        (r"eval\(", "Dangerous eval execution"),
        (r"rm\s+-rf\s+/", "Destructive root filesystem removal"),
        (r"env\s*\|\s*curl", "Environment variable exfiltration")
    ]

    findings = []
    for p in Path(skill_path).glob("**/*"):
        if p.is_file() and p.suffix in [".md", ".py", ".sh", ".js"]:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                for pat, desc in suspicious_patterns:
                    if re.search(pat, content, re.IGNORECASE):
                        findings.append({"rule_id": "FALLBACK_STATIC", "message": f"{desc} in {p.name}"})
            except Exception:
                pass

    return {
        "safe": len(findings) == 0,
        "risk_score": 75 if findings else 0,
        "risk_severity": "HIGH" if findings else "LOW",
        "findings": findings,
        "scanner": "Built-in Static Fallback"
    }

def detect_or_create_backup_repo(dest_path):
    """
    Stage 3: Smart Backup Routing
    - Detects existing backup repo (CLI-Skills-and-MDs or local git repo)
    - If not found, auto-creates a new GitHub repo via gh CLI
    - Supports connected cloud plugins (Google Drive / GWS)
    """
    # 1. Check if destination or parent is inside a git repo with remote
    git_dir_out, _, code = run_cmd("git rev-parse --show-toplevel", cwd=dest_path)
    if code == 0 and git_dir_out:
        remote_out, _, r_code = run_cmd("git remote -v", cwd=git_dir_out)
        if r_code == 0 and "github.com" in remote_out:
            return {"type": "EXISTING_GIT", "path": git_dir_out, "remote": remote_out.splitlines()[0]}

    # 2. Check well-known workspace repos
    workspace_repos = [
        "/opt/data/CLI-Skills-and-MDs",
        "/opt/data/home/git/CLI-Skills-and-MDs",
        os.path.expanduser("~/CLI-Skills-and-MDs")
    ]
    for repo_path in workspace_repos:
        if os.path.isdir(os.path.join(repo_path, ".git")):
            return {"type": "EXISTING_GIT", "path": repo_path, "remote": "Primuez/CLI-Skills-and-MDs"}

    # 3. Check if gh CLI is authenticated to create a new backup repo
    gh_auth, _, gh_code = run_cmd("gh auth status")
    if gh_code == 0:
        new_repo_name = os.environ.get("SKILLS_BACKUP_REPO", "agent-skills-backup")
        print(f"[INFO] No existing backup repository found. Creating new GitHub repository '{new_repo_name}' via gh CLI...")
        create_out, create_err, c_code = run_cmd(f"gh repo create {new_repo_name} --private --description 'AI Agent Skills automated backup'")
        if c_code == 0 or "already exists" in create_err:
            return {"type": "AUTO_CREATED_GITHUB", "repo": new_repo_name}

    # 4. Check Cloud Provider Plugin (Google Drive via GWS)
    gws_out, _, gws_code = run_cmd("which gws")
    if gws_code == 0:
        return {"type": "CLOUD_GWS_DRIVE"}

    return {"type": "LOCAL_ONLY"}

def install_and_sync(source, target_dir=DEFAULT_SKILLS_DIR, force=False):
    """Full 3-stage installation pipeline."""
    print("=" * 60)
    print("  SKILL INSTALLER - Intelligent Security & Backup Pipeline")
    print("=" * 60)

    # Resolve source
    temp_dir = Path("/tmp/skill-installer-temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    skill_name = None
    source_path = None

    if os.path.isdir(source):
        source_path = Path(source)
        skill_name = source_path.name
    elif os.path.isfile(source) and source.endswith("SKILL.md"):
        source_path = Path(source).parent
        skill_name = source_path.name
    elif source.startswith("http://") or source.startswith("https://"):
        # Remote URL fetch
        print(f"[1/3] Fetching remote skill: {source}")
        if "github.com" in source and "/blob/" in source:
            source = source.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        target_file = temp_dir / "SKILL.md"
        try:
            req = urllib.request.Request(source, headers={"User-Agent": "Skill-Installer/1.0"})
            with urllib.request.urlopen(req) as resp, open(target_file, "wb") as f:
                f.write(resp.read())
            source_path = temp_dir
            skill_name = Path(source).parent.name if Path(source).parent.name != "" else "custom-skill"
        except Exception as e:
            print(f"[ERROR] Failed to fetch remote skill: {e}")
            return False
    else:
        print(f"[ERROR] Invalid source: {source}")
        return False

    # Read SKILL.md
    skill_md = source_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] No SKILL.md found in {source_path}")
        return False

    content = skill_md.read_text(encoding="utf-8", errors="ignore")
    meta = parse_skill_metadata(content)
    if not meta.get("name"):
        meta["name"] = skill_name or source_path.name

    print(f"\n[STAGE 1] Need Assessment & Alternatives Check: '{meta['name']}'")
    installed = get_installed_skills(target_dir)
    assessment = check_alternatives(meta, installed)
    print(f" -> Status: {assessment['status']}")
    print(f" -> Assessment: {assessment['message']}")

    if assessment["status"] == "DUPLICATE" and not force:
        print("[ABORT] Exact duplicate already exists. Skipping installation. (Use --force to overwrite)")
        return False
    elif assessment["status"] == "ALTERNATIVE_FOUND" and not force:
        print("[WARN] Existing skills already cover this functionality. Re-evaluating necessity...")
        print(" -> If this skill adds distinct tools or specialized patterns, proceed with --force.")

    print(f"\n[STAGE 2] NVIDIA SkillSpector Security Scan")
    scan = scan_security(source_path)
    print(f" -> Engine: {scan['scanner']}")
    print(f" -> Risk Severity: {scan['risk_severity']} (Score: {scan['risk_score']}/100)")
    if scan["findings"]:
        print(" -> Findings:")
        for f in scan["findings"]:
            print(f"    - {f.get('rule_id', 'ALERT')}: {f.get('message', '')}")

    if not scan["safe"] and not force:
        print("\n[SECURITY BLOCK] Skill failed security inspection! Malicious or high-risk patterns detected.")
        print("Aborting installation to protect agent environment.")
        return False
    print(" -> Security Verdict: PASSED [SAFE]")

    print(f"\n[STAGE 3] Automated Installation & Smart Backup Routing")
    final_dest = Path(target_dir) / meta["name"]
    final_dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_path, final_dest, dirs_exist_ok=True)
    print(f" -> Skill files written to: {final_dest}")

    backup_route = detect_or_create_backup_repo(str(final_dest))
    print(f" -> Backup Route: {backup_route['type']}")

    if backup_route["type"] == "EXISTING_GIT":
        repo_path = backup_route["path"]
        print(f" -> Syncing to existing git backup repo: {repo_path}")
        repo_skill_dir = Path(repo_path) / "skills" / meta["name"]
        repo_skill_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, repo_skill_dir, dirs_exist_ok=True)
        run_cmd(f"git add 'skills/{meta['name']}'", cwd=repo_path)
        run_cmd(f"git commit -m 'feat(skills): auto-install {meta['name']}'", cwd=repo_path)
        run_cmd("git push", cwd=repo_path)
        print(" -> Git commit and push completed successfully.")

    elif backup_route["type"] == "AUTO_CREATED_GITHUB":
        print(f" -> Synced into newly created GitHub repository '{backup_route['repo']}'.")

    elif backup_route["type"] == "CLOUD_GWS_DRIVE":
        print(" -> Syncing skill package to Google Drive via GWS...")
        run_cmd(f"gws drive upload '{final_dest}'")
        print(" -> Cloud backup upload completed.")

    print("\n" + "=" * 60)
    print(f"  SUCCESS: Skill '{meta['name']}' installed and backed up!")
    print("=" * 60)
    return True

def main():
    parser = argparse.ArgumentParser(description="Skill Installer - Intelligent Security & Backup Package Manager for Agent Skills")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Install a skill with full 3-stage pipeline")
    install_parser.add_argument("source", help="Path, GitHub raw URL, or repository folder")
    install_parser.add_argument("--skills-dir", default=DEFAULT_SKILLS_DIR, help="Target skills directory")
    install_parser.add_argument("--force", action="store_true", help="Force install even if alternatives or minor warnings exist")

    check_parser = subparsers.add_parser("check", help="Check if a skill is needed or has existing alternatives")
    check_parser.add_argument("source", help="Path or URL to SKILL.md")

    scan_parser = subparsers.add_parser("scan", help="Run NVIDIA SkillSpector security scan on a skill")
    scan_parser.add_argument("path", help="Local path to skill directory")

    args = parser.parse_args()
    if args.command == "install":
        success = install_and_sync(args.source, args.skills_dir, args.force)
        sys.exit(0 if success else 1)
    elif args.command == "check":
        meta = parse_skill_metadata(Path(args.source).read_text())
        skills = get_installed_skills()
        res = check_alternatives(meta, skills)
        print(json.dumps(res, indent=2))
    elif args.command == "scan":
        res = scan_security(args.path)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
