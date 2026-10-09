"""Build the v4 reading edition; optionally export a Drive-friendly text copy."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "docs/cosmology/v4"
OUTPUT = EDITION / "OMEGA_COSMOLOGY_V4_COMPLETE.md"
REPO_URL = "https://github.com/6ixpoolgames/Omega/blob/codex/operational-continuation-comparison/"


def build() -> str:
    chapters = sorted(EDITION.glob("[0-9][0-9]_*.md"))
    if [p.name[:2] for p in chapters] != [f"{i:02d}" for i in range(12)]:
        raise ValueError("Expected exactly one chapter each, 00 through 11.")
    texts = [p.read_text(encoding="utf-8").strip() for p in chapters]
    titles = [s.splitlines()[0].removeprefix("# ") for s in texts]
    for i, title in enumerate(titles):
        if not title.startswith(f"{i:02d} — "):
            raise ValueError(f"Incorrect heading in {chapters[i]}")
    contents = "\n".join(f"- [{title}](#chapter-{i:02d})" for i, title in enumerate(titles))
    body = "\n\n---\n\n".join(
        f'<a id="chapter-{i:02d}"></a>\n\n{text}' for i, text in enumerate(texts)
    )
    for i, path in enumerate(chapters):
        body = body.replace(f"]({path.name})", f"](#chapter-{i:02d})")
    return (
        "# Omega Cosmology v4\n\n"
        "**Physical possibility, situated value and the Alpha–Omega interpretation**\n\n"
        "Full draft · 9 October 2026\n\n"
        "A self-contained synthesis for review. The classical calibration is explicit; "
        "general quantum breadth remains open. The ethical bridge is value requiring "
        "valuers together with conditional normativity. Alpha–Omega supplies an "
        "interpretive layer.\n\n"
        "Generated from the numbered source chapters; edit those chapters and rebuild.\n\n"
        "## Contents\n\n" + contents + "\n\n---\n\n" + body + "\n"
    )


def drive_export(content: str) -> str:
    def expand(match: re.Match[str]) -> str:
        label, target = match.groups()
        if target.startswith(("https://", "http://", "#")):
            return match.group(0)
        path, _, fragment = target.partition("#")
        relative = (EDITION / path).resolve().relative_to(ROOT.resolve()).as_posix()
        url = REPO_URL + quote(relative, safe="/")
        if fragment:
            url += "#" + fragment
        return f"[{label}]({url})"

    return re.sub(r"\[([^\]\n]+)\]\(([^)\n]+)\)", expand, content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--drive-export", type=Path)
    args = parser.parse_args()
    content = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Combined edition is missing or stale.")
    else:
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    if args.drive_export:
        args.drive_export.parent.mkdir(parents=True, exist_ok=True)
        args.drive_export.write_text(drive_export(content), encoding="utf-8", newline="\n")
    print(f"v4: 12 chapters, {len(content.split()):,} whitespace-delimited words.")


if __name__ == "__main__":
    main()
