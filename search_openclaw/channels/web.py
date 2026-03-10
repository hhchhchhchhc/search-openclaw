"""Generic web reading fallback."""

from __future__ import annotations

from .base import Channel


class WebChannel(Channel):
    name = "web"
    description = "网页读取"
    backends = ["Jina Reader / 任意网页读取"]
    tier = 0

    def can_handle(self, target: str) -> bool:
        return target.startswith("http://") or target.startswith("https://")

    def check(self, config=None) -> tuple[str, str]:
        return "ok", "可作为通用网页 fallback 使用"
