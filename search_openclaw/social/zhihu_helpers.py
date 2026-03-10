"""Copied helper functions adapted from local Zhihu crawlers."""

from __future__ import annotations

import re
from typing import Iterable

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)

ANSWER_URL_RE = re.compile(r"^https?://www\.zhihu\.com/question/(\d+)/answer/(\d+)(?:[/?#].*)?$")
ARTICLE_URL_RE = re.compile(r"^https?://zhuanlan\.zhihu\.com/p/(\d+)(?:[/?#].*)?$")
QUESTION_URL_RE = re.compile(r"^https?://www\.zhihu\.com/question/(\d+)(?:[/?#].*)?$")


def parse_cookie_string(cookie_string: str) -> list[dict]:
    cookies: list[dict] = []
    for chunk in str(cookie_string or "").split(";"):
        part = chunk.strip()
        if not part or "=" not in part:
            continue
        name, value = part.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            continue
        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": ".zhihu.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            }
        )
    if not cookies:
        raise ValueError("Cookie 为空或格式不正确")
    return cookies


def detect_risk_or_login(page) -> None:
    body_text = (page.locator("body").inner_text(timeout=3000) or "").strip()
    risk_markers = [
        "您当前请求存在异常",
        "暂时限制本次访问",
        "验证你是不是机器人",
        "登录后即可查看",
    ]
    if any(marker in body_text for marker in risk_markers):
        raise RuntimeError("知乎返回了风控或登录校验页面，请更新 Cookie")


def click_expand_buttons(page) -> None:
    labels = ["阅读全文", "展开阅读全文", "显示全部", "查看全部"]
    for label in labels:
        locator = page.locator(f'button:has-text("{label}"), div[role="button"]:has-text("{label}")')
        count = min(locator.count(), 8)
        for idx in range(count):
            try:
                locator.nth(idx).click(timeout=800)
                page.wait_for_timeout(120)
            except Exception:
                continue


def first_text(page, selectors: Iterable[str]) -> str:
    for selector in selectors:
        locator = page.locator(selector)
        count = locator.count()
        for idx in range(min(count, 4)):
            try:
                text = (locator.nth(idx).inner_text(timeout=1000) or "").strip()
            except Exception:
                continue
            if text:
                return text
    return ""


def longest_text(page, selectors: Iterable[str]) -> str:
    best = ""
    for selector in selectors:
        locator = page.locator(selector)
        count = locator.count()
        for idx in range(min(count, 8)):
            try:
                text = (locator.nth(idx).inner_text(timeout=1000) or "").strip()
            except Exception:
                continue
            if len(text) > len(best):
                best = text
    return best

