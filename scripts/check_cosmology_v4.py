"""Check the assembled v4 manuscript and its direct local references."""

from __future__ import annotations

import hashlib
import json
import re

from build_cosmology_v4 import EDITION, OUTPUT, ROOT, build


def main() -> None:
    expected = build()
    assert OUTPUT.read_text(encoding="utf-8") == expected, "Stale reading edition"
    files = sorted(EDITION.glob("[0-9][0-9]_*.md"))
    files += [EDITION / "README.md", OUTPUT]
    files += sorted((ROOT / "docs/quantum").glob("*.md"))
    missing = []
    link_count = 0
    for path in files:
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", content):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            link_count += 1
            destination = (path.parent / target.split("#")[0]).resolve()
            generated_record = (EDITION / "publication_checks.json").resolve()
            if destination != generated_record and not destination.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not missing, "Missing local links:\n" + "\n".join(missing)
    references = (EDITION / "10_REFERENCES.md").read_text(encoding="utf-8")
    defined = set(re.findall(r"\*\*(R\d+)\.", references))
    cited = set(re.findall(r"\bR\d+\b", expected))
    assert cited <= defined, f"Undefined references: {cited - defined}"
    assert expected.count('<a id="chapter-') == 12
    record = {
        "edition": "Omega Cosmology v4 full draft",
        "date": "2026-10-09",
        "chapters": 12,
        "word_count_whitespace": len(expected.split()),
        "bytes": OUTPUT.stat().st_size,
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "direct_local_links_checked": link_count,
        "reference_entries": len(defined),
        "combined_matches_sources": True,
        "new_numerical_experiments": False,
    }
    (EDITION / "publication_checks.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
