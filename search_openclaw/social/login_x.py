"""Copied and adapted X login helper."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log into x.com and save storage state.")
    parser.add_argument("--state", required=True, help="Path to save Playwright storage state")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds to wait before saving state")
    parser.add_argument(
        "--persistent-dir",
        default="~/.config/google-chrome",
        help="Chrome user data dir for persistent profile",
    )
    parser.add_argument(
        "--chrome-path",
        default="/usr/bin/google-chrome",
        help="Path to Chrome executable",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_path = Path(args.state).expanduser().resolve()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        profile_dir = Path(args.persistent_dir).expanduser().resolve()
        profile_dir.mkdir(parents=True, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            executable_path=args.chrome_path,
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-software-rasterizer",
                "--use-gl=swiftshader",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )
        page = context.new_page()
        page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
        print("=" * 60)
        print("Please finish login in the opened browser window.")
        print(f"After login, keep the page open for up to {args.timeout} seconds.")
        print("=" * 60)
        page.wait_for_timeout(args.timeout * 1000)
        context.storage_state(path=str(state_path))
        print(f"Saved login state to: {state_path}")
        context.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

