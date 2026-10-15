"""Helpers shared by the documentation generators."""

import json
from pathlib import Path

# Language of the generated documentation. The source JSON files keep
# human-readable text as language maps, so more languages can be added
# to the data without touching the generators.
DOCS_LANG = "en"


def load_terms(root: Path) -> dict:
    """Load the term registry from schema/terms/.

    The registry is split one file per class (mirroring docs/model/*.md),
    so several classes can be edited without touching a single large JSON
    file. `_index.json` holds the namespaces, the published IRIs and the
    class files in their canonical order; the returned dict is the index
    with "classes" replaced by the loaded class objects.
    """
    terms_dir = root / "schema" / "terms"
    index = json.loads((terms_dir / "_index.json").read_text(encoding="utf-8"))
    classes = [
        json.loads((terms_dir / f"{file}.json").read_text(encoding="utf-8"))
        for file in index["classes"]
    ]
    return {**index, "classes": classes}


def localized(field, lang: str = DOCS_LANG) -> str:
    """Return text from a language map, falling back to the first available language."""
    if isinstance(field, dict):
        return field.get(lang) or next(iter(field.values()), "")
    return field or ""


def to_kebab(name: str) -> str:
    """PascalCase / camelCase -> kebab-case"""
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("-")
        out.append(ch.lower())
    return "".join(out)


def write_if_changed(path: Path, content: str) -> None:
    # Rewriting an unchanged file would trigger another rebuild under
    # `mkdocs serve` and the build hook would loop forever.
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")
