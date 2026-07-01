# Claude Code Config

> 中文 | [English](README.md)

一套可跨 Claude Code 更新保留的共享定制:**状态栏**(git · 模型 · 上下文百分比 · 运行中的子 agent)+ **50 % 自动压缩** + **会话启动健康检查**(自动捕获回归)。

## 写入了什么

| 定制项 | 位置 | 效果 |
|---|---|---|
| `statusLine` | `~/.claude/settings.json` | `python3 ~/.claude/statusline.py` 渲染一行 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` | `env` | 上下文到 50 % 就自动压缩(默认约 80 %) |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` | `env` | 压缩窗口 |
| `autoCompactEnabled=true` | 顶层 | 启用自动压缩 |
| SessionStart 钩子 | 插件 | 每次会话启动跑一次快速健康检查 |

状态栏显示:`branch · model · ▰▰▰▱▱▱▱▱▱▱ ctx 30% · ⚡ 2/3`(运行中子 agent 此处/总数,递归统计 workflow 子 agent)。

## 安装 — 方式 A:插件(推荐)

带自动健康检查钩子、`/cc-config:install|healthcheck|restore` 命令,可用 `/plugin update` 升级。

```
/plugin marketplace add Lxcardoza993/claude-code-config
/plugin install cc-config@cc-config-market
/cc-config:install
```

然后**重启 Claude Code**。钩子在安装时自动激活(不写进你的 `settings.json`,所以 cc-switch 切 profile 不会清掉它)。

## 安装 — 方式 B:一行 bash(备选)

不装插件、不带命令——只接 `settings.json` + 拷贝 `statusline.py`。适合锁定机器或不想装插件的场景。

```bash
curl -fsSL https://raw.githubusercontent.com/Lxcardoza993/claude-code-config/main/install.sh | bash
```

然后**重启 Claude Code**。以后升级重跑同一行即可。

## cc-switch 用户

[cc-switch](https://github.com/farion1231/cc-switch) 把 profile 存成 `~/.claude/profiles/*.json` 里的完整 `settings.json` 快照,切换时会覆盖 `~/.claude/settings.json`。安装器会探测到这一点,把 env 变量 + `statusLine` 写进**每一个** profile,这样切 profile 不再清掉你的定制。

## Claude Code 更新之后

CC 更新可能改 env 变量名或挪走二进制。SessionStart 钩子(插件路径)会自动捕获并以警告形式提示。手动跑完整检查:

```
/cc-config:healthcheck        # 插件路径
```

若某项失败,`/cc-config:install`(或重跑 `install.sh`)即可修复。

## 仓库结构

```
.claude-plugin/marketplace.json   # 市场清单(仓库根 = 市场)
cc-config/                        # 插件
  .claude-plugin/plugin.json      # 插件清单
  hooks/hooks.json                # SessionStart → healthcheck.py --hook
  commands/{install,healthcheck,restore}.md
  scripts/{statusline,install,healthcheck}.py
install.sh                        # 非插件一行安装器
```

## 许可证

MIT
