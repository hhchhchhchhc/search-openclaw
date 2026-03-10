"""Channel registry for Search OpenClaw."""

from __future__ import annotations

from typing import List, Optional

from .base import Channel
from .brave_search import BraveSearchChannel
from .exa_search import ExaSearchChannel
from .github import GitHubSearchChannel
from .iflow import IFlowChannel
from .multi_search import MultiSearchChannel
from .perplexity import PerplexitySearchChannel
from .tavily_search import TavilySearchChannel
from .web import WebChannel

ALL_CHANNELS: List[Channel] = [
    WebChannel(),
    GitHubSearchChannel(),
    BraveSearchChannel(),
    TavilySearchChannel(),
    ExaSearchChannel(),
    PerplexitySearchChannel(),
    IFlowChannel(),
    MultiSearchChannel(),
]


def get_channel(name: str) -> Optional[Channel]:
    for channel in ALL_CHANNELS:
        if channel.name == name:
            return channel
    return None


def get_all_channels() -> List[Channel]:
    return ALL_CHANNELS


__all__ = ["Channel", "ALL_CHANNELS", "get_channel", "get_all_channels"]
