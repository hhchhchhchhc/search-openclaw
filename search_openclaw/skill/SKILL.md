---
name: search-openclaw
description: >
  Configure and use OpenClaw web search providers. Use when the user asks to
  set up Brave Search, Tavily, Exa, Perplexity, iFlow, or
  wants a better web-search stack for research and information gathering.
---

# Search OpenClaw

Focus on the search layer first.

## Quick rules

- If the user has a card and wants stability, prefer Brave.
- If the user wants low friction and no card, prefer Tavily.
- If the user wants fallback or broader coverage, combine at least two providers.
- If the user needs GitHub search, prefer `gh` when available.

## Commands

```bash
search-openclaw doctor
search-openclaw configure brave_api_key <KEY>
search-openclaw configure tavily_api_key <KEY>
search-openclaw configure exa_api_key <KEY>
search-openclaw configure perplexity_api_key <KEY>
search-openclaw configure iflow_api_key <KEY>
search-openclaw doctor --fix
search-openclaw scrape-social "AI Agent" --platform both
```

## Suggested provider order

1. Brave
2. Tavily
3. Exa
4. iFlow

## GitHub search

```bash
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
```

## Generic web reading

```bash
curl -s "https://r.jina.ai/URL"
```
