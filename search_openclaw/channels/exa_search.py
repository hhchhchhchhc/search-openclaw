"""Exa search provider."""

from __future__ import annotations

import shutil
import subprocess

from .base import Channel


class ExaSearchChannel(Channel):
    name = "exa_search"
    description = "Exa 语义搜索"
    backends = ["Exa API", "mcporter"]
    tier = 1

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if config and config.get("exa_api_key"):
            return "ok", "已配置 Exa API Key，可补充语义搜索"

        mcporter = shutil.which("mcporter")
        if not mcporter:
            return "warn", "未配置 exa_api_key，且 mcporter 不可用；可改走 Brave / Tavily"
        try:
            result = subprocess.run(
                [mcporter, "config", "list"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if "exa" in result.stdout.lower():
                return "ok", "mcporter 已配置 Exa，可作为低成本补充搜索源"
            return "warn", "mcporter 已安装但未注册 Exa；可执行 mcporter config add exa https://mcp.exa.ai/mcp"
        except Exception:
            return "warn", "mcporter 检查失败；Exa 状态未知"
