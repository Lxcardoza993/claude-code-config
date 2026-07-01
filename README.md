# Claude Code Config

> [中文](README.zh-CN.md) | English

Backup of my Claude Code customizations so they survive Claude Code updates. Run the healthcheck after every CC update to catch regressions early.

## Why this repo exists

Claude Code updates the **binary** (under `~/.local/share/fnm/...` or similar) but does **not** touch `~/.claude/` — that's user config. So my customizations don't normally vanish on update. The real risks are:

1. **An env var gets renamed in a future binary** — e.g. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is the real knob today (3 hits in the v2.1.185 binary), but a future version could rename it and silently stop honoring it.
2. **The statusLine input schema changes** — the JSON CC pipes to `statusline.py` could add/rename fields.
3. **I wipe `~/.claude` or reinstall** — config is gone.

This repo + the healthcheck script catch all three. The `statusline.py` itself lives in this repo and is symlinked into `~/.claude/`, so edits here flow live.

## What's preserved

| File | What |
|---|---|
| `statusline.py` | The status line script. Symlinked from `~/.claude/statusline.py`. Shows: git branch (±dirty) · model · **context % with a 10-cell ▰/▱ bar** · running subagent count. No directory segment (by choice). |
| `apply_autocompact_env.py` | Bakes `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` + `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` into every cc-switch profile + `settings.json`, so they survive profile switches. |
| `apply_statusline_wire.py` | Wires the `statusLine` field into every cc-switch profile + `settings.json`. |
| `cc-config-healthcheck.py` | Post-update healthcheck — see below. |
| `CLAUDE.md.snapshot` | Snapshot of my global `~/.claude/CLAUDE.md` work-discipline rules. |

**Not in this repo (on purpose):** `settings.json` and the cc-switch `profiles/*.json`. They contain `ANTHROPIC_AUTH_TOKEN` / API keys. The two `apply_*.py` scripts re-derive the secret-free fields (env knobs + statusLine wiring) into the live files instead.

## The autocompact knobs (verified real)

Grep'd against the v2.1.185 binary — only these are real, the rest of the blog's "tuning" vars are apocrypha (0 binary hits):

- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` — triggers auto-compaction at 50% context (default ~96.7%).
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` — the token window the % is measured against.
- `autoCompactEnabled: true` in `settings.json`.

Plus a CLAUDE.md rule: for simple/medium tasks, manually `/compact` with a preservation directive at 40–50% rather than waiting for the auto fallback. Long tasks / hard programming projects rely on the 50% auto trigger.

## Restore after a fresh install / wiped `~/.claude`

```bash
git clone git@github.com:Lxcardoza993/claude-code-config.git ~/claude-code-config
ln -sf ~/claude-code-config/statusline.py ~/.claude/statusline.py
python3 ~/claude-code-config/apply_autocompact_env.py   # needs ~/.claude/profiles + settings.json to exist
python3 ~/claude-code-config/apply_statusline_wire.py
python3 ~/claude-code-config/cc-config-healthcheck.py
```

## Healthcheck after a Claude Code update

```bash
python3 ~/claude-code-config/cc-config-healthcheck.py
```

It verifies, with ✅/❌:

- The CC binary is found and still grep-recognizes both env vars (flags a future rename).
- `statusline.py` exists, runs, and emits the `ctx` segment.
- `settings.json` + every profile has `PCT_OVERRIDE=50`, `WINDOW=300000`, `autoCompactEnabled`, and the `statusLine` field wired.

Exit code 0 = all pass, 1 = something regressed. If a check fails, read the `[detail]` and re-run the matching `apply_*.py` or fix `statusline.py` here (the symlink means edits take effect immediately).

## License

Private personal config.
