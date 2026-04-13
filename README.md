# Sky Claude HUD

A lightweight statusline for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that works over SSH and in terminals like Xshell. No GUI, no browser — just a compact two-line HUD rendered with ANSI escape codes.

一个轻量级的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 状态栏，适用于 SSH 和 Xshell 等终端环境。无需 GUI 或浏览器，仅通过 ANSI 转义码渲染紧凑的两行 HUD。

## Preview / 预览

```
◆ Claude Opus 4.6 [high] │ ████████████░░░░░░░░ 58% │ $1.23 │ ⏱ 12m04s │ +42 -7
▸ ~/project │ ⎇ feat/my-branch │ ✱ modified │ 5h ████░░░░ 51%
```

**Line 1 / 第一行:** Model & effort level, context window usage bar, session cost, duration, lines changed

**Line 2 / 第二行:** Working directory, git branch & dirty state, API rate limit usage

## Features / 特性

- **Zero dependencies** — pure Python 3 stdlib, no pip install needed / 纯 Python 3 标准库，无需 pip 安装
- **SSH-friendly** — ANSI colors only, works in Xshell, PuTTY, iTerm2, etc. / 仅使用 ANSI 颜色，适用于各种终端
- **Fast** — single-shot stdin→stdout, no daemon, no polling / 单次 stdin→stdout，无守护进程
- **Color-coded bars** — green/yellow/red thresholds for context and rate limits / 上下文和速率限制的绿/黄/红阈值
- **Git-aware** — shows branch, staged, and modified status / 显示分支、暂存和修改状态

## Requirements / 环境依赖

| Dependency / 依赖 | Version / 版本 | Note / 说明 |
|---|---|---|
| **Python** | >= 3.6 | Uses f-strings and `subprocess.run` / 使用 f-string 和 `subprocess.run` |
| **Git** | any | Optional, for branch & dirty state detection / 可选，用于分支和状态检测 |
| **Claude Code** | >= 1.0.x | Must support `statusLine` in `~/.claude/settings.json` / 需支持 statusLine 配置 |

Terminal must support **ANSI escape codes** and **Unicode** (block characters `█░`, box drawing `│`, branch symbol `⎇`).

终端需支持 **ANSI 转义码** 和 **Unicode**（方块字符 `█░`、制表符 `│`、分支符号 `⎇`）。

## Install / 安装

```bash
git clone https://github.com/TbusOS/sky-claude-hud.git
cd sky-claude-hud
./install.sh
```

The installer will:
1. Test that `statusline.py` runs correctly / 测试 `statusline.py` 是否正常运行
2. Add a `statusLine` entry to `~/.claude/settings.json` / 向配置文件写入 `statusLine` 条目
3. Restart Claude Code to activate / 重启 Claude Code 即可生效

### Manual install / 手动安装

Edit `~/.claude/settings.json` and add:

编辑 `~/.claude/settings.json`，添加：

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /path/to/sky-claude-hud/statusline.py"
  }
}
```

## How it works / 工作原理

Claude Code pipes a JSON blob to the statusline command's stdin on every status update. `statusline.py` parses the JSON and prints two formatted lines to stdout:

Claude Code 在每次状态更新时，将一个 JSON 数据通过 stdin 传入 statusline 命令。`statusline.py` 解析 JSON 后输出两行格式化文本到 stdout：

```
stdin (JSON) → statusline.py → stdout (ANSI-colored text)
```

### JSON fields used / 使用的 JSON 字段

| Field | Description / 说明 |
|---|---|
| `model.display_name` | Model name / 模型名称 |
| `effort_level` | Thinking effort / 思考深度 |
| `context_window.used_percentage` | Context usage % / 上下文使用率 |
| `cost.total_cost_usd` | Session cost / 会话费用 |
| `cost.total_duration_ms` | Session duration / 会话时长 |
| `cost.total_lines_added` | Lines added / 新增行数 |
| `cost.total_lines_removed` | Lines removed / 删除行数 |
| `cwd` | Working directory / 工作目录 |
| `worktree.branch` | Git branch (from Claude) / Git 分支 |
| `rate_limits.five_hour` | 5-hour rate limit / 5 小时速率限制 |
| `rate_limits.seven_day` | 7-day rate limit / 7 天速率限制 |

## Uninstall / 卸载

Remove the `statusLine` block from `~/.claude/settings.json`, then delete the cloned repo.

从 `~/.claude/settings.json` 中删除 `statusLine` 配置块，然后删除克隆的仓库。

## License / 许可证

MIT
