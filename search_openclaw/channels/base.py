"""Base channel class."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Channel(ABC):
    name: str = ""
    description: str = ""
    backends: list[str] = []
    tier: int = 0

    @abstractmethod
    def can_handle(self, target: str) -> bool:
        ...

    def check(self, config=None) -> tuple[str, str]:
        return "ok", "可用"
