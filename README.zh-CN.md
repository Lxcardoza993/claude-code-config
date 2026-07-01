# Claude Code 配置备份

> [English](README.md) | 中文

我的 Claude Code 自定义配置备份,使其在 CC 更新后仍能保留。每次 CC 更新后跑健康检查脚本,及早发现回退。

## 为什么有这个仓库

Claude Code 更新的是**二进制**(在 `~/.local/share/fnm/...` 之类路径),**不碰** `~/.claude/`——那是用户配置。所以我的自定义一般不会因更新而消失。真正的风险是:

1. **未来二进制把某个 env var 改名**——比如 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 是当前真实旋钮(v2.1.185 二进制 3 命中),但未来版本可能改名后静默不再认它。
2. **statusLine 输入 schema 变了**——CC 喂给 `statusline.py` 的 JSON 字段可能增删改名。
3. **我清空了 `~/.claude` 或重装**——配置没了。

这个仓库 + 健康检查脚本三者都抓。`statusline.py` 本体就放本仓库,通过软链接挂到 `~/.claude/`,这里改了实时生效。

## 保留了什么

| 文件 | 内容 |
|---|---|
| `statusline.py` | 状态行脚本。`~/.claude/statusline.py` 软链到它。显示:git 分支(±改动)· 模型 · **上下文 % + 10 格 ▰/▱ 进度条** · 运行中子agent数。无目录段(刻意)。 |
| `apply_autocompact_env.py` | 把 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` + `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` 写进每个 cc-switch profile + `settings.json`,使其在 profile 切换后不丢。 |
| `apply_statusline_wire.py` | 把 `statusLine` 字段接线进每个 cc-switch profile + `settings.json`。 |
| `cc-config-healthcheck.py` | 更新后健康检查——见下。 |
| `CLAUDE.md.snapshot` | 我的全局 `~/.claude/CLAUDE.md` 工作纪律规则快照。 |

**不在本仓库(刻意):** `settings.json` 和 cc-switch 的 `profiles/*.json`。它们含 `ANTHROPIC_AUTH_TOKEN` / API key。两个 `apply_*.py` 脚本是反向把不含密的字段(env 旋钮 + statusLine 接线)重新写进 live 文件。

## 自动压缩旋钮(已核实为真)

对 v2.1.185 二进制 grep 字面量核实——只有下面是真的,博客里其它"调优"变量都是杜撰(二进制 0 命中):

- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` — 50% 上下文触发自动压缩(默认约 96.7%)。
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` — 百分比所测的 token 窗口。
- `settings.json` 里 `autoCompactEnabled: true`。

外加一条 CLAUDE.md 规则:简单/中等任务在 40–50% 时主动 `/compact` 附保留指令,别等自动兜底;长任务/高难度编程项目靠 50% 自动触发。

## 全新安装 / `~/.claude` 被清空后恢复

```bash
git clone git@github.com:Lxcardoza993/claude-code-config.git ~/claude-code-config
ln -sf ~/claude-code-config/statusline.py ~/.claude/statusline.py
python3 ~/claude-code-config/apply_autocompact_env.py   # 需 ~/.claude/profiles + settings.json 已存在
python3 ~/claude-code-config/apply_statusline_wire.py
python3 ~/claude-code-config/cc-config-healthcheck.py
```

## CC 更新后健康检查

```bash
python3 ~/claude-code-config/cc-config-healthcheck.py
```

用 ✅/❌ 核验:

- 找到 CC 二进制,且仍 grep 认得两个 env var(未来改名会在这里报出来)。
- `statusline.py` 存在、能跑、输出含 `ctx` 段。
- `settings.json` + 每个 profile 都有 `PCT_OVERRIDE=50`、`WINDOW=300000`、`autoCompactEnabled`、且 `statusLine` 字段已接线。

退出码 0=全过,1=有回退。某项失败时看 `[detail]`,重跑对应 `apply_*.py` 或在此修 `statusline.py`(软链意味着改了立即生效)。

## License

私库个人配置。
