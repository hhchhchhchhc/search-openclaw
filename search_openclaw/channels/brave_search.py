"""Brave Search provider."""

from __future__ import annotations

from .base import Channel


class BraveSearchChannel(Channel):
    name = "brave_search"
    description = "Brave Search API"
    backends = ["Brave Search"]
    tier = 1

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if config and config.get("brave_api_key"):
            return "ok", "已配置 Brave API Key，适合作为主搜索"
        return "off", "未配置 brave_api_key；适合有卡、追求兼容性时优先接入"
