#!/usr/bin/env python3
"""Wire statusLine (-> ~/.claude/statusline.py) into every cc-switch profile + settings.json,
so the context% status line survives profile switches. Preserves all other fields."""
import json, shutil, os, glob

BASE = "/home/li/.claude"
PROFILES_DIR = os.path.join(BASE, "profiles")
SETTINGS = os.path.join(BASE, "settings.json")
BACKUP_DIR = os.path.join(BASE, ".bak-statusline-20260701")

STATUSLINE = {"type": "command",
              "command": "python3 /home/li/.claude/statusline.py"}

files = sorted(glob.glob(os.path.join(PROFILES_DIR, "**", "*.json"), recursive=True))
if SETTINGS not in files:
    files.append(SETTINGS)

print(f"Files to edit ({len(files)}):")
for f in files:
    print(f"  {os.path.relpath(f, BASE)}")

print(f"\nBackup -> {BACKUP_DIR}")
for f in files:
    rel = os.path.relpath(f, BASE)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(f, dest)
print(f"Backed up {len(files)} files.\n")

results = []
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    before = d.get("statusLine", "<MISSING>")
    d["statusLine"] = STATUSLINE
    with open(f, "w") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    results.append((os.path.relpath(f, BASE), before))

print("Edits:")
for rel, before in results:
    had = "already" if before != "<MISSING>" else "added"
    print(f"  {rel}: {had}")

print(f"\nDone. {len(results)} files. Backup at {BACKUP_DIR}")
