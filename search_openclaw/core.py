"""Core API for Search OpenClaw."""

from __future__ import annotations

from search_openclaw.config import Config


class SearchOpenClaw:
    """Search-focused doctor and configuration facade."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def doctor(self) -> dict[str, dict]:
        from search_openclaw.doctor import check_all

        return check_all(self.config)

    def doctor_report(self) -> str:
        from search_openclaw.doctor import check_all, format_report

        return format_report(check_all(self.config))
