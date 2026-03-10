"""Wrappers around the local x_search_aggregator repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from search_openclaw.config import Config


class SocialScrapeError(RuntimeError):
    """Raised when a social scraping workflow fails."""


def detect_repo(config: Config) -> Path:
    repo_path = config.get("x_aggregator_repo_path")
    if repo_path:
        path = Path(str(repo_path)).expanduser().resolve()
        if path.exists():
            return path

    detected = config.detect_x_aggregator_settings().get("repo_path")
    if detected:
        return Path(detected)
    raise SocialScrapeError("未找到 x_search_aggregator 仓库，请先配置 x_aggregator_repo_path")


def detect_python(config: Config, repo: Path) -> str:
    configured = config.get("x_aggregator_python")
    if configured:
        return str(configured)
    detected = config.detect_x_aggregator_settings().get("python_bin")
    if detected:
        return str(detected)
    return "python3"


def run_x_login(config: Config, timeout: int = 180) -> str:
    repo = detect_repo(config)
    python_bin = detect_python(config, repo)
    state_path = config.get("x_auth_state_path") or config.detect_x_aggregator_settings().get("x_auth_state_path")
    if not state_path:
        state_path = str((repo / "auth_state_cookie.json").resolve())

    proc = subprocess.run(
        [python_bin, "login_x.py", "--state", state_path, "--timeout", str(timeout)],
        cwd=repo,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise SocialScrapeError(proc.stderr.strip() or proc.stdout.strip() or "X 登录失败")
    config.set("x_auth_state_path", state_path)
    return proc.stdout


def scrape_social(
    config: Config,
    platform: str,
    keyword: str,
    headless: bool = True,
    out_dir: str | None = None,
    zhihu_cookie: str | None = None,
) -> dict[str, dict]:
    repo = detect_repo(config)
    python_bin = detect_python(config, repo)
    output: dict[str, dict] = {}

    if platform in {"x", "both"}:
        x_state = config.get("x_auth_state_path") or config.detect_x_aggregator_settings().get("x_auth_state_path")
        if not x_state:
            raise SocialScrapeError("未找到 X 登录态文件，请先执行 search-openclaw login-x")
        cmd = [python_bin, "search_keyword_500.py", "--keyword", keyword, "--state", str(x_state)]
        if headless:
            cmd.append("--headless")
        if out_dir:
            cmd.extend(["--out-dir", out_dir])
        output["x"] = _run_and_parse(cmd, repo)

    if platform in {"zhihu", "both"}:
        cookie = zhihu_cookie or config.get("zhihu_cookie")
        if not cookie:
            raise SocialScrapeError("未配置 zhihu_cookie；请先运行 search-openclaw configure zhihu_cookie <COOKIE>")
        cmd = [python_bin, "zhihu_search_keyword_500.py", "--keyword", keyword, "--cookie", cookie]
        if headless:
            cmd.append("--headless")
        if out_dir:
            cmd.extend(["--out-dir", out_dir])
        output["zhihu"] = _run_and_parse(cmd, repo)

    return output


def _run_and_parse(cmd: list[str], repo: Path) -> dict[str, str]:
    proc = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if proc.returncode != 0:
        raise SocialScrapeError(stderr.strip() or stdout.strip() or "爬取失败")

    run_dir = _extract_run_dir(stdout)
    return {
        "command": " ".join(cmd),
        "run_dir": run_dir or "",
        "stdout": stdout,
    }


def _extract_run_dir(text: str) -> str | None:
    patterns = [
        r"运行目录:\s*(.+)",
        r"Run directory:\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None
