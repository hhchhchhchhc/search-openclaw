"""Collect and format provider health checks."""

from __future__ import annotations

from search_openclaw.channels import get_all_channels
from search_openclaw.config import Config


def check_all(config: Config) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for channel in get_all_channels():
        status, message = channel.check(config)
        results[channel.name] = {
            "status": status,
            "name": channel.description,
            "message": message,
            "tier": channel.tier,
            "backends": channel.backends,
        }
    return results


def format_report(results: dict[str, dict]) -> str:
    lines = ["Search OpenClaw 状态", "=" * 40]

    ok_count = sum(1 for item in results.values() if item["status"] == "ok")
    total = len(results)

    sections = [
        ("✅ 默认可用 / 零配置", 0),
        ("🔑 配 Key 后可用", 1),
        ("🧩 进阶组合 / 可选增强", 2),
    ]

    for title, tier in sections:
        group = [(name, item) for name, item in results.items() if item["tier"] == tier]
        if not group:
            continue
        lines.append("")
        lines.append(title + "：")
        for _name, item in group:
            prefix = {
                "ok": "  ✅",
                "warn": "  [!]",
                "off": "  --",
                "error": "  [X]",
            }.get(item["status"], "  --")
            lines.append(f"{prefix} {item['name']} — {item['message']}")

    lines.append("")
    lines.append(f"状态：{ok_count}/{total} 个搜索通道就绪")
    if ok_count < total:
        lines.append("提示：先运行 `search-openclaw configure ...`，再执行 `search-openclaw doctor`")
    return "\n".join(lines)
