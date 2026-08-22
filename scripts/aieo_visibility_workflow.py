#!/usr/bin/env python3
"""GitHub Actions向けに可視性収集の既知Provider障害だけを縮退扱いする。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TRACKER = Path(__file__).with_name("aieo_visibility_tracker.py")
KNOWN_REFERRER_BLOCK = "requests from referer <empty> are blocked."


def is_known_provider_degradation(output: str) -> bool:
    """現在確認済みのGoogle HTTPリファラー制限だけを縮退対象にする。"""
    text = output.lower()
    return (
        "google custom search" in text
        and "http 403" in text
        and KNOWN_REFERRER_BLOCK in text
    )


def write_github_output(name: str, value: str) -> None:
    path = os.getenv("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> int:
    completed = subprocess.run(
        [sys.executable, str(TRACKER)],
        text=True,
        capture_output=True,
        check=False,
    )

    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)

    if completed.returncode == 0:
        write_github_output("provider_degraded", "false")
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        return 0

    if is_known_provider_degradation(combined):
        # 既知のHTTPリファラー制限だけはデータを書かずに安全な縮退として扱う。
        write_github_output("provider_degraded", "true")
        print(
            "::warning title=AIEO visibility provider degraded::"
            "Google Custom SearchのHTTPリファラー制限により収集をスキップしました。"
            "新しい可視性データは保存していません。"
        )
        return 0

    # 設定破損・GitHub API障害・プログラム例外などは隠さず通常の失敗として伝播する。
    write_github_output("provider_degraded", "false")
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
