#!/usr/bin/env python3
"""Bake CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 + CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000
into every cc-switch profile + settings.json, so they survive profile switches.
Preserves all other fields. 2-space indent, ensure_ascii=False, trailing newline."""
import json, shutil, os, glob, sys

BASE = "/home/li/.claude"
PROFILES_DIR = os.path.join(BASE, "profiles")
SETTINGS = os.path.join(BASE, "settings.json")
BACKUP_DIR = os.path.join(BASE, ".bak-autocompact-20260701")

# collect: all *.json under profiles/ (recursive incl templates/) + settings.json
files = sorted(glob.glob(os.path.join(PROFILES_DIR, "**", "*.json"), recursive=True))
if SETTINGS not in files:
    files.append(SETTINGS)

print(f"Files to edit ({len(files)}):")
for f in files:
    print(f"  {f}")

# backup (preserve relative path structure)
print(f"\nBackup -> {BACKUP_DIR}")
for f in files:
    rel = os.path.relpath(f, BASE)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(f, dest)
print(f"Backed up {len(files)} files.\n")

# edit
results = []
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    env = d.setdefault("env", {})  # ensure env exists; if missing, create
    before_pct = env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "<MISSING>")
    before_win = env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "<MISSING>")
    env["CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"] = "50"
    env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = "300000"
    with open(f, "w") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    results.append((os.path.relpath(f, BASE), before_pct, before_win))

print("Edits:")
for rel, bp, bw in results:
    print(f"  {rel}: PCT {bp} -> 50 | WINDOW {bw} -> 300000")
print(f"\nDone. {len(results)} files edited. Backup at {BACKUP_DIR}")
