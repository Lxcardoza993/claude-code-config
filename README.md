# Claude Code Config

> [中文](README.zh-CN.md) | English

Shared Claude Code customizations that survive CC updates: a **status line** (git · model · context % · running subagents), **auto-compact at 50 %**, and a **session-start health check** that flags regressions automatically.

## What it wires

| Customization | Where | Effect |
|---|---|---|
| `statusLine` | `~/.claude/settings.json` | `python3 ~/.claude/statusline.py` renders one line |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` | `env` | auto-compact triggers at 50 % context (not the default ~80 %) |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` | `env` | compaction window |
| `autoCompactEnabled=true` | top-level | enables auto-compact |
| SessionStart hook | plugin | runs a fast health check on every session start |

The status line shows: `branch · model · ▰▰▰▱▱▱▱▱▱▱ ctx 30% · ⚡ 2/3` (running subagents here/total, recursive over workflow subagents).

## Install — Option A: plugin (recommended)

Gives you the auto health-check hook, `/cc-config:install|healthcheck|restore` commands, and `/plugin update` for upgrades.

```
/plugin marketplace add Lxcardoza993/claude-code-config
/plugin install cc-config@cc-config-market
/cc-config:install
```

Then **restart Claude Code**. The hook auto-activates on install (it is not written into your `settings.json`, so cc-switch profile switches can't wipe it).

## Install — Option B: one-shot bash (fallback)

No plugin, no commands — just wires `settings.json` + copies `statusline.py`. Good for locked-down machines or when you don't want a plugin.

```bash
curl -fsSL https://raw.githubusercontent.com/Lxcardoza993/claude-code-config/main/install.sh | bash
```

Then **restart Claude Code**. Re-run the same command to update later.

## cc-switch users

[cc-switch](https://github.com/farion1231/cc-switch) stores profiles as full `settings.json` snapshots in `~/.claude/profiles/*.json` that overwrite `~/.claude/settings.json` on switch. The installer detects this and propagates the env vars + `statusLine` into **every** profile, so switching profiles no longer wipes your customizations.

## After a Claude Code update

CC updates can rename env vars or move the binary. The SessionStart hook (plugin path) catches this automatically and surfaces a warning. To run the full check manually:

```
/cc-config:healthcheck        # plugin path
```

If a check fails, `/cc-config:install` (or re-run `install.sh`) repairs it.

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace manifest (repo root = marketplace)
cc-config/                        # the plugin
  .claude-plugin/plugin.json      # plugin manifest
  hooks/hooks.json                # SessionStart → healthcheck.py --hook
  commands/{install,healthcheck,restore}.md
  scripts/{statusline,install,healthcheck}.py
install.sh                        # non-plugin one-shot installer
```

## License

MIT
