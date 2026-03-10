"""GitHub search/read capability."""

from __future__ import annotations

import shutil
import subprocess

from .base import Channel


class GitHubSearchChannel(Channel):
    name = "github"
    description = "GitHub 搜索"
    backends = ["gh CLI", "GitHub token"]
    tier = 0

    def can_handle(self, target: str) -> bool:
        return "github.com" in target

    def check(self, config=None) -> tuple[str, str]:
        if config and config.get("github_token"):
            return "ok", "已配置 GitHub token，可走 API 或 gh CLI"

        gh = shutil.which("gh")
        if not gh:
            return "warn", "gh CLI 未安装；公开仓库仍可通过网页读取"
        try:
            result = subprocess.run(
                [gh, "auth", "status"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if result.returncode == 0:
                return "ok", "gh CLI 已认证，可用于仓库/代码/Issue 搜索"
            return "warn", "gh CLI 已安装但未认证；运行 gh auth login 可解锁完整能力"
        except Exception:
            return "warn", "gh CLI 状态检查失败；运行 gh auth status 查看详情"
