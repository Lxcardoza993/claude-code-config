#!/usr/bin/env python3
"""Claude Code config healthcheck — 在 CC 更新后运行,验证 statusline + 自动压缩
自定义配置仍然有效且仍被接线。Usage: python3 cc-config-healthcheck.py
退出码:0=全过,1=有失败。"""
import json, glob, os, subprocess, sys, shutil

BASE = "/home/li/.claude"
PROFILES_DIR = f"{BASE}/profiles"
SETTINGS = f"{BASE}/settings.json"
STATUSLINE = f"{BASE}/statusline.py"

PASS = "\033[38;5;78m✅\033[0m"
FAIL = "\033[38;5;196m❌\033[0m"
results = []

def check(ok, msg, detail=""):
    results.append((PASS if ok else FAIL, msg, detail))
    return ok

# 1. 定位 CC 二进制 + 版本
cc_bin, cc_ver = None, "?"
try:
    p = shutil.which("claude")
    if p:
        cc_bin = os.path.realpath(p)
        cc_ver = (subprocess.run(["claude","--version"], capture_output=True, text=True, timeout=5).stdout.strip()
                  or "?")
except Exception:
    pass
check(bool(cc_bin), f"CC binary found ({cc_ver})", cc_bin or "claude not on PATH")

# 2. 二进制是否仍识别自动压缩 env var(未来版本改名则这里会失败 → 提示)
if cc_bin and os.path.exists(cc_bin):
    for var in ["CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "CLAUDE_CODE_AUTO_COMPACT_WINDOW"]:
        try:
            r = subprocess.run(["grep","-a","-c",var,cc_bin], capture_output=True, text=True, timeout=15)
            n = int(r.stdout.strip()) if r.returncode == 0 else 0
        except Exception:
            n = -1
        check(n > 0, f"binary recognizes {var}", f"{n} hits" if n >= 0 else "grep failed")
else:
    check(False, "binary grep skipped", "no binary")

# 3. statusline.py 存在且能跑(输出含 ctx)
sl_exists = os.path.exists(STATUSLINE)
check(sl_exists, "statusline.py exists", STATUSLINE)
if sl_exists:
    try:
        mock = json.dumps({"transcript_path":"", "cwd":"/home/li",
                           "model":{"display_name":"X","id":"x"},
                           "context":50000, "context_window":200000})
        r = subprocess.run(["python3", STATUSLINE], input=mock,
                           capture_output=True, text=True, timeout=5)
        check("ctx" in r.stdout, "statusline.py runs + emits ctx", r.stdout.strip()[:80])
    except Exception as e:
        check(False, "statusline.py run failed", str(e))

# 4. settings.json
try:
    s = json.load(open(SETTINGS)); env = s.get("env", {})
    check(env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE") == "50", "settings PCT_OVERRIDE=50", env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"))
    check(env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW") == "300000", "settings WINDOW=300000", env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW"))
    check(s.get("autoCompactEnabled") is True, "settings autoCompactEnabled=true", s.get("autoCompactEnabled"))
    sl = s.get("statusLine", {})
    check(str(sl.get("command","")).endswith("statusline.py"), "settings statusLine wired", sl.get("command"))
except Exception as e:
    check(False, "settings.json read failed", str(e))

# 5. 所有 profile
for p in sorted(glob.glob(f"{PROFILES_DIR}/**/*.json", recursive=True)):
    try:
        d = json.load(open(p)); env = d.get("env", {}); sl = d.get("statusLine", {})
        rel = os.path.relpath(p, BASE)
        ok = (env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE") == "50"
              and env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW") == "300000"
              and str(sl.get("command","")).endswith("statusline.py"))
        check(ok, f"profile {rel}", "PCT/WINDOW/statusLine " + ("OK" if ok else "MISSING"))
    except Exception as e:
        check(False, f"profile {os.path.relpath(p,BASE)} read failed", str(e))

# 汇总
print("\n=== Claude Code config healthcheck ===\n")
fails = sum(1 for m, *_ in results if m == FAIL)
for mark, msg, detail in results:
    print(f"  {mark} {msg}" + (f"  [{detail}]" if detail else ""))
print(f"\n{len(results)-fails}/{len(results)} passed, {fails} failed")
sys.exit(1 if fails else 0)
