"""Multi-search composition health check."""

from __future__ import annotations

from .base import Channel


class MultiSearchChannel(Channel):
    name = "multi_search"
    description = "多搜索源组合"
    backends = ["Brave", "Tavily", "Exa", "Perplexity", "iFlow"]
    tier = 2

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if not config:
            return "off", "未提供配置"

        configured = config.configured_provider_count()
        if configured >= 2:
            return "ok", f"已配置 {configured} 个搜索源，可用于容灾和补盲"
        if configured == 1:
            return "warn", "当前只有 1 个搜索源；建议至少再补一个做 fallback"
        return "off", "尚未配置搜索源；先从 Brave 或 Tavily 开始"
