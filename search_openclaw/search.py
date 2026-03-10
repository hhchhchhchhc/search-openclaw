"""Provider-backed search helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass

import requests

from search_openclaw.config import Config


class SearchError(RuntimeError):
    """Raised when a provider search cannot be completed."""


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    score: float | None = None
    published_date: str | None = None


def available_provider_order(config: Config) -> list[str]:
    order: list[str] = []
    if config.get("brave_api_key"):
        order.append("brave")
    if config.get("tavily_api_key"):
        order.append("tavily")
    if config.get("exa_api_key"):
        order.append("exa")
    if config.get("perplexity_api_key"):
        order.append("perplexity")
    if config.get("iflow_api_key"):
        order.append("iflow")
    if config.get("github_token") or shutil.which("gh"):
        order.append("github")
    if not order:
        order.append("web")
    return order


def auto_provider(config: Config) -> str:
    return available_provider_order(config)[0]


def search(query: str, provider: str, limit: int, config: Config) -> tuple[str, list[SearchResult]]:
    chosen = auto_provider(config) if provider == "auto" else provider

    if chosen == "brave":
        return chosen, _search_brave(query, limit, config)
    if chosen == "tavily":
        return chosen, _search_tavily(query, limit, config)
    if chosen == "exa":
        return chosen, _search_exa(query, limit, config)
    if chosen == "perplexity":
        return chosen, _search_perplexity(query, limit, config)
    if chosen == "iflow":
        return chosen, _search_iflow(query, limit, config)
    if chosen == "github":
        return chosen, _search_github(query, limit, config)
    raise SearchError(f"不支持的 provider: {chosen}")


def stream_iflow(query: str, config: Config):
    api_key = config.get("iflow_api_key")
    base_url = (config.get("iflow_base_url") or "https://apis.iflow.cn/v1").rstrip("/")
    model = config.get("iflow_model") or "qwen3-max"
    if not api_key:
        raise SearchError("未检测到 iFlow API Key")

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是研究助手。请把用户查询整理成结构化研究摘要，优先给出要点、关键词、后续搜索建议。"
                    ),
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "max_tokens": 700,
            "stream": True,
        },
        timeout=60,
        stream=True,
    )
    _raise_for_http_error(response, "iFlow")
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:].strip()
        if payload == "[DONE]":
            break
        try:
            item = json.loads(payload)
        except json.JSONDecodeError:
            continue
        delta = ((item.get("choices") or [{}])[0].get("delta") or {}).get("content")
        if delta:
            yield delta


def search_iflow_structured(query: str, config: Config) -> dict:
    api_key = config.get("iflow_api_key")
    base_url = (config.get("iflow_base_url") or "https://apis.iflow.cn/v1").rstrip("/")
    model = config.get("iflow_model") or "qwen3-max"
    if not api_key:
        raise SearchError("未检测到 iFlow API Key")

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是研究助手。请只返回 JSON 对象，不要 markdown。"
                        "字段包括 summary(字符串), bullets(字符串数组), keywords(字符串数组), "
                        "suggested_queries(字符串数组)。"
                    ),
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "max_tokens": 900,
            "stream": False,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    _raise_for_http_error(response, "iFlow")
    payload = response.json()
    choices = payload.get("choices") or []
    if not choices:
        raise SearchError("iFlow 返回为空")
    content = choices[0].get("message", {}).get("content", "").strip()
    return json.loads(content)


def dump_results_json(provider: str, results: list[SearchResult]) -> str:
    payload = {
        "provider": provider,
        "results": [asdict(item) for item in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def format_results(provider: str, results: list[SearchResult]) -> str:
    lines = [f"Provider: {provider}", ""]
    if not results:
        lines.append("No results")
        return "\n".join(lines)

    for idx, item in enumerate(results, start=1):
        lines.append(f"{idx}. {item.title}")
        lines.append(f"   URL: {item.url}")
        if item.published_date:
            lines.append(f"   Date: {item.published_date}")
        if item.score is not None:
            lines.append(f"   Score: {item.score}")
        if item.snippet:
            lines.append(f"   Snippet: {item.snippet}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _raise_for_http_error(response: requests.Response, provider: str) -> None:
    if response.ok:
        return
    try:
        payload = response.json()
    except Exception:
        payload = response.text
    raise SearchError(f"{provider} 请求失败: HTTP {response.status_code} - {payload}")


def _search_brave(query: str, limit: int, config: Config) -> list[SearchResult]:
    api_key = config.get("brave_api_key")
    if not api_key:
        raise SearchError("未配置 brave_api_key")

    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api_key},
        params={"q": query, "count": min(limit, 20)},
        timeout=20,
    )
    _raise_for_http_error(response, "Brave")
    payload = response.json()
    items = payload.get("web", {}).get("results", [])
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=(item.get("description") or " ".join(item.get("extra_snippets") or [])).strip(),
            source="brave",
            published_date=item.get("page_age"),
        )
        for item in items[:limit]
    ]


def _search_tavily(query: str, limit: int, config: Config) -> list[SearchResult]:
    api_key = config.get("tavily_api_key")
    if not api_key:
        raise SearchError("未配置 tavily_api_key")

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "max_results": min(limit, 20),
            "search_depth": "basic",
            "topic": "general",
            "include_answer": False,
            "include_favicon": True,
        },
        timeout=30,
    )
    _raise_for_http_error(response, "Tavily")
    payload = response.json()
    items = payload.get("results", [])
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
            source="tavily",
            score=item.get("score"),
        )
        for item in items[:limit]
    ]


def _search_exa(query: str, limit: int, config: Config) -> list[SearchResult]:
    api_key = config.get("exa_api_key")
    if not api_key:
        raise SearchError("未配置 exa_api_key")

    response = requests.post(
        "https://api.exa.ai/search",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "type": "auto",
            "numResults": min(limit, 20),
            "contents": {"highlights": {"maxCharacters": 600}},
        },
        timeout=30,
    )
    _raise_for_http_error(response, "Exa")
    payload = response.json()
    items = payload.get("results", [])
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=" ".join(item.get("highlights") or []) or item.get("summary") or item.get("text") or "",
            source="exa",
            published_date=item.get("publishedDate"),
        )
        for item in items[:limit]
    ]


def _search_perplexity(query: str, limit: int, config: Config) -> list[SearchResult]:
    api_key = config.get("perplexity_api_key")
    if not api_key:
        raise SearchError("未配置 perplexity_api_key")

    response = requests.post(
        "https://api.perplexity.ai/search",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "max_results": min(limit, 20),
            "max_tokens_per_page": 1024,
        },
        timeout=30,
    )
    _raise_for_http_error(response, "Perplexity")
    payload = response.json()
    items = payload.get("results", [])
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("snippet", ""),
            source="perplexity",
            published_date=item.get("date") or item.get("last_updated"),
        )
        for item in items[:limit]
    ]


def _search_github(query: str, limit: int, config: Config) -> list[SearchResult]:
    gh = shutil.which("gh")
    if not gh:
        raise SearchError("未安装 gh CLI，无法执行 GitHub 搜索")

    fields = "name,owner,description,url,stargazerCount,updatedAt"
    result = subprocess.run(
        [
            gh,
            "search",
            "repos",
            query,
            "--limit",
            str(limit),
            "--json",
            fields,
        ],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )
    if result.returncode != 0:
        raise SearchError(f"GitHub 搜索失败: {result.stderr.strip() or result.stdout.strip()}")
    payload = json.loads(result.stdout or "[]")
    return [
        SearchResult(
            title=f"{item.get('owner', {}).get('login', '')}/{item.get('name', '')}".strip("/"),
            url=item.get("url", ""),
            snippet=item.get("description") or "",
            source="github",
            score=float(item.get("stargazerCount", 0)),
            published_date=item.get("updatedAt"),
        )
        for item in payload
    ]


def _search_iflow(query: str, limit: int, config: Config) -> list[SearchResult]:
    api_key = config.get("iflow_api_key")
    base_url = (config.get("iflow_base_url") or "https://apis.iflow.cn/v1").rstrip("/")
    model = config.get("iflow_model") or "qwen3-max"
    if not api_key:
        raise SearchError("未检测到 iFlow API Key；请先在 OpenClaw 中配置 iflow，或手动写入 iflow_api_key")

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一个研究助手。用户给你一个搜索查询。"
                        "请基于你的能力给出简洁研究摘要，输出不超过 5 条要点。"
                        "每条要点尽量包含可验证的实体名、项目名或关键词。"
                        "不要输出 markdown 表格。"
                    ),
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "max_tokens": 700,
            "stream": False,
        },
        timeout=60,
    )
    _raise_for_http_error(response, "iFlow")
    payload = response.json()
    choices = payload.get("choices") or []
    if not choices:
        raise SearchError("iFlow 返回为空")
    content = choices[0].get("message", {}).get("content", "").strip()
    return [
        SearchResult(
            title=f"iFlow research brief: {query}",
            url="",
            snippet=content,
            source="iflow",
        )
    ]
