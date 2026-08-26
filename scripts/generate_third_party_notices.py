# /// script
# requires-python = ">=3.14"
# dependencies = ["pip-licenses>=5.5.5"]
# ///
"""Regenerate third_party_notices.md from the packages installed in .venv.

Run it with `uv run --script scripts/generate_third_party_notices.py` after
`uv sync`, since the notices are derived from the resolved environment.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "third_party_notices.md"
PROJECT_NAME = "transcriber-whisper"

# pip-licenses reports this placeholder when a field is missing.
UNKNOWN = "UNKNOWN"

HEADER = f"""# Third-Party Notices

`{PROJECT_NAME}` は以下のサードパーティパッケージに依存し、配布物にはそれらを同梱している。
各パッケージの著作権は原著作者に帰属する。

このファイルは `scripts/generate_third_party_notices.py` が生成する。手で編集しない。
"""


def venv_python() -> Path:
    """Path to the interpreter of the project environment to inspect."""
    relative = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    path = ROOT / ".venv" / relative
    if not path.is_file():
        raise SystemExit(f"error: {path} not found; run `uv sync` first")
    return path


def collect() -> list[dict[str, str]]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "piplicenses",
            "--python",
            str(venv_python()),
            "--from=mixed",
            "--format=json",
            "--order=name",
            "--with-authors",
            "--with-urls",
            "--with-license-file",
            "--no-license-path",
            "--ignore-packages",
            PROJECT_NAME,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


def cell(value: str) -> str:
    """Escape a value so it cannot break out of a Markdown table cell."""
    return value.replace("|", "\\|") if value != UNKNOWN else "-"


def fence(text: str) -> str:
    """Backtick fence long enough to wrap text that itself contains fences."""
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def render(packages: list[dict[str, str]]) -> str:
    lines = [HEADER, "## 一覧", "", "| パッケージ | バージョン | ライセンス | 著作者 |", "|---|---|---|---|"]
    for pkg in packages:
        name, url = pkg["Name"], pkg["URL"]
        label = f"[{name}]({url})" if url != UNKNOWN else name
        lines.append(f"| {label} | {pkg['Version']} | {cell(pkg['License'])} | {cell(pkg['Author'])} |")

    lines += ["", "## ライセンス全文", ""]
    for pkg in packages:
        lines.append(f"### {pkg['Name']} {pkg['Version']}")
        lines.append("")
        text = pkg["LicenseText"]
        if text == UNKNOWN:
            lines += [
                f"配布物にライセンスファイルが含まれていない。ライセンス表記は `{pkg['License']}`。",
                "",
            ]
            continue
        marker = fence(text)
        lines += [marker, text.strip(), marker, ""]

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(collect()), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
