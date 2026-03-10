"""Perplexity provider."""

from __future__ import annotations

from .base import Channel


class PerplexitySearchChannel(Channel):
    name = "perplexity_search"
    description = "Perplexity API"
    backends = ["Perplexity"]
    tier = 1

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if config and config.get("perplexity_api_key"):
            return "ok", "已配置 Perplexity API Key，可做检索增强"
        return "off", "未配置 perplexity_api_key；可选，通常用于进阶增强"
