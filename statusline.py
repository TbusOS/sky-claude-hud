#!/usr/bin/env python3
"""Claude Code HUD statusline - lightweight, fast, Xshell/SSH compatible."""

import json
import os
import subprocess
import sys
from datetime import datetime

# ANSI colors
RST = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Progress bar chars
FILL = "\u2588"  # █
EMPTY = "\u2591"  # ░
SEP = f" {DIM}\u2502{RST} "  # │


def color_by_pct(pct):
    if pct < 60:
        return GREEN
    elif pct < 80:
        return YELLOW
    return RED


def make_bar(pct, width=20):
    pct = max(0, min(100, pct))
    filled = int(pct * width / 100)
    c = color_by_pct(pct)
    return f"{c}{FILL * filled}{DIM}{EMPTY * (width - filled)}{RST} {c}{pct:.0f}%{RST}"


def fmt_cost(usd):
    if usd is None:
        return f"{DIM}--{RST}"
    if usd < 0.01:
        return f"{WHITE}$0.00{RST}"
    return f"{WHITE}${usd:.2f}{RST}"


def fmt_duration(ms):
    if ms is None or ms <= 0:
        return f"{DIM}--{RST}"
    s = ms / 1000
    if s < 60:
        return f"{DIM}\u23f1{RST} {s:.0f}s"
    m = int(s // 60)
    sec = int(s % 60)
    if m < 60:
        return f"{DIM}\u23f1{RST} {m}m{sec:02d}s"
    h = int(m // 60)
    m = m % 60
    return f"{DIM}\u23f1{RST} {h}h{m:02d}m"


def fmt_lines(added, removed):
    parts = []
    if added:
        parts.append(f"{GREEN}+{added}{RST}")
    if removed:
        parts.append(f"{RED}-{removed}{RST}")
    return " ".join(parts) if parts else ""


def fmt_reset(ts):
    if ts is None or ts <= 0:
        return ""
    try:
        reset = datetime.fromtimestamp(ts)
    except (OSError, OverflowError, ValueError):
        return ""
    fmt = "%H:%M" if reset.date() == datetime.now().date() else "%m-%d %H:%M"
    return f" {DIM}→{reset.strftime(fmt)}{RST}"


def fmt_rate(data, label):
    if not data:
        return ""
    pct = data.get("used_percentage", 0)
    if pct is None or pct == 0:
        return ""
    c = color_by_pct(pct)
    w = 8
    filled = int(pct * w / 100)
    bar = f"{c}{FILL * filled}{DIM}{EMPTY * (w - filled)}{RST}"
    return f"{label} {bar} {c}{pct:.0f}%{RST}{fmt_reset(data.get('resets_at'))}"


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return

    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        return

    # -- Line 1: model | context bar | cost | duration | lines --
    parts1 = []

    # Model
    model = ""
    m = d.get("model", {})
    if isinstance(m, dict):
        model = m.get("display_name") or m.get("id", "")
    if model:
        parts1.append(f"{BOLD}{MAGENTA}\u25c6{RST} {BOLD}{WHITE}{model}{RST}")

    # Context window (with 200k overflow warning)
    ctx = d.get("context_window", {})
    if ctx:
        pct = ctx.get("used_percentage")
        if pct is not None:
            bar = make_bar(pct)
            if d.get("exceeds_200k_tokens"):
                bar += f" {RED}\u26a0 200k+{RST}"
            parts1.append(bar)

    # Cost
    cost = d.get("cost", {})
    if cost:
        usd = cost.get("total_cost_usd")
        parts1.append(fmt_cost(usd))

        dur = cost.get("total_duration_ms")
        if dur:
            parts1.append(fmt_duration(dur))

        lines = fmt_lines(
            cost.get("total_lines_added"),
            cost.get("total_lines_removed"),
        )
        if lines:
            parts1.append(lines)

    if parts1:
        print(SEP.join(parts1))

    # -- Line 2: git branch or cwd | rate limits --
    parts2 = []

    cwd = d.get("cwd", "")

    branch = ""
    if cwd:
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=cwd, capture_output=True, text=True, timeout=1,
            )
            if r.returncode == 0:
                branch = r.stdout.strip()
        except Exception:
            pass

    # Always show relative path
    if cwd:
        display_cwd = cwd
        home = os.path.expanduser("~")
        if display_cwd.startswith(home):
            display_cwd = "~" + display_cwd[len(home):]
        parts2.append(f"{DIM}\u25b8{RST} {WHITE}{display_cwd}{RST}")

    if branch:
        parts2.append(f"{CYAN}\u2387 {branch}{RST}")
        # git dirty check (~1ms each, exit on first change)
        git_flags = []
        try:
            r = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=cwd, capture_output=True, timeout=1,
            )
            if r.returncode == 1:
                git_flags.append(f"{GREEN}\u25cf staged{RST}")
        except Exception:
            pass
        try:
            r = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=cwd, capture_output=True, timeout=1,
            )
            if r.returncode == 1:
                git_flags.append(f"{YELLOW}\u2731 modified{RST}")
        except Exception:
            pass
        if git_flags:
            parts2.append(" ".join(git_flags))

    # Rate limits
    rl = d.get("rate_limits", {})
    if isinstance(rl, dict):
        r5 = fmt_rate(rl.get("five_hour"), f"{DIM}5h{RST}")
        r7 = fmt_rate(rl.get("seven_day"), f"{DIM}7d{RST}")
        if r5:
            parts2.append(r5)
        if r7:
            parts2.append(r7)

    if parts2:
        print(SEP.join(parts2))


if __name__ == "__main__":
    main()
