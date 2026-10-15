#!/usr/bin/env python3
"""
Generate Markdown codelist pages from the JSON files in codelists/.

The codelists/*.json files are the source of truth. This script renders
docs/codelists/<name>.md with a table of values. Generated files are not
committed (see .gitignore) — they are rebuilt on every docs build.

The table has a label and description column for every language present
in the data (English first), so adding a language to the JSON is enough
to show it in the docs.

Usage:
    python scripts/build_codelist_docs.py
"""

import json
import sys
from pathlib import Path

from docs_common import DOCS_LANG, localized, to_kebab, write_if_changed

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "codelists"
OUT = ROOT / "docs" / "codelists"


def languages(data: dict) -> list[str]:
    """Languages used in value labels and descriptions, docs language first."""
    found = set()
    for v in data.get("values", []):
        for field in ("labels", "description"):
            if isinstance(v.get(field), dict):
                found.update(v[field])
    found.discard(DOCS_LANG)
    return [DOCS_LANG, *sorted(found)]


def render(data: dict) -> str:
    name = data.get("name", "?")
    closed = data.get("closed", True)
    langs = languages(data)

    lines = [f"# {name}", ""]

    desc = localized(data.get("description"))
    if desc:
        lines += [desc, ""]

    lines += [f"**Codelist type:** {'closed' if closed else 'open'}", ""]
    if not closed:
        lines += [
            "!!! note",
            "    This codelist is open — if no value fits, the producer",
            "    may use its own code outside this list.",
            "",
        ]

    # `appliesTo` restricts where a value may be used (e.g. Realty/Room,
    # or the utility network a connection belongs to).
    has_scope = any(v.get("appliesTo") for v in data.get("values", []))

    header = ["Code"]
    header += [f"Label ({l.upper()})" for l in langs]
    header += [f"Description ({l.upper()})" for l in langs]
    if has_scope:
        header.append("Applies to")

    lines += [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["-----"] * len(header)) + "|",
    ]

    for v in data.get("values", []):
        labels = v.get("labels", {})
        note = v.get("description", {})

        cells = [f"`{v.get('code', '')}`"]
        cells += [labels.get(l, "") for l in langs]
        cells += [note.get(l, "") for l in langs]
        if has_scope:
            cells.append(", ".join(f"`{a}`" for a in v.get("appliesTo", [])))

        lines.append("| " + " | ".join(cells) + " |")

    lines += [
        "",
        "---",
        "",
        f"*This page is generated from `codelists/{to_kebab(name)}.json`. "
        "Do not edit by hand.*",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if not SRC.is_dir():
        print(f"ERROR: directory {SRC} does not exist", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)

    files = sorted(SRC.glob("*.json"))
    if not files:
        print(f"WARNING: no .json files in {SRC}")
        return 0

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"ERROR: {path.name} is not valid JSON: {exc}", file=sys.stderr)
            return 1

        write_if_changed(OUT / (path.stem + ".md"), render(data))

    print(f"codelists: {len(files)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
