"""Tavily search provider."""

from __future__ import annotations

from .base import Channel


class TavilySearchChannel(Channel):
    name = "tavily_search"
    description = "Tavily Search API"
    backends = ["Tavily"]
    tier = 1

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if config and config.get("tavily_api_key"):
            return "ok", "已配置 Tavily API Key，适合零门槛起步"
        return "off", "未配置 tavily_api_key；不想绑卡时建议优先试它"
