#!/usr/bin/env python3
"""
Generate Markdown property tables from the term registry schema/terms/.

For every class two partials are written: docs/_partials/terms-<file>.md
(property table) and docs/_partials/rules-<file>.md (validation rules).
They are embedded into the hand-written model page with the snippets
directive:

    --8<-- "_partials/terms-advert.md"
    --8<-- "_partials/rules-advert.md"

The explanatory prose stays hand-written, while the property table,
including links to schema.org, is generated from a single source of truth.

Usage:
    python scripts/build_term_docs.py
"""

import sys
from pathlib import Path

from docs_common import load_terms, localized, to_kebab, write_if_changed

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "schema" / "terms"
OUT = ROOT / "docs" / "_partials"


def load_namespaces(data: dict) -> dict:
    return data.get("namespaces", {})


def expand(curie: str, ns: dict) -> str:
    """erdif:Advert -> https://erdif-org.github.io/erdif-spec/ns/v1#Advert"""
    if ":" not in curie:
        return curie
    prefix, local = curie.split(":", 1)
    base = ns.get(prefix)
    return base + local if base else curie


def link(curie: str, ns: dict) -> str:
    """Build a Markdown link to the definition of a term.

    schema:     -> public schema.org documentation
    erdif:      -> the vocabulary page of this site
    erdif-cl:   -> the codelist page of this site
    other       -> plain code without a link
    """
    if ":" not in curie:
        return f"`{curie}`"

    prefix, local = curie.split(":", 1)
    iri = expand(curie, ns)

    if prefix == "schema":
        return f"[`{curie}`]({iri})"
    if prefix == "erdif-cl":
        return f"[`{curie}`](../codelists/{to_kebab(local)}.md)"
    if prefix == "erdif":
        # Classes start upper-case, properties lower-case. Anchors carry a
        # prefix so that erdif:Contact and erdif:contact do not collide.
        kind = "class" if local[:1].isupper() else "prop"
        return f"[`{curie}`](../vocabulary.md#{kind}-{to_kebab(local)})"
    return f"`{curie}`"


def render_class(cls: dict, ns: dict) -> str:
    lines = []

    types = " + ".join(link(t, ns) for t in cls.get("types", []))
    lines += ["**Entity types:** " + types, ""]

    desc = localized(cls.get("description"))
    if desc:
        lines += [desc, ""]

    lines += [
        "| Property | Semantics | Range | Cardinality | Description |",
        "|----------|-----------|-------|-------------|-------------|",
    ]

    for p in cls.get("properties", []):
        term = p["term"]
        sem = link(p["iri"], ns)
        rng = link(p.get("range", ""), ns)

        if p.get("cardinality"):
            card = f"`{p['cardinality']}`"
        else:
            card = "`1`" if p.get("required") else "`0..1`"

        note = localized(p.get("description"))
        if p.get("languageMap"):
            note += " Written as a language map."

        lines.append(f"| `{term}` | {sem} | {rng} | {card} | {note} |")

    lines += [
        "",
        '!!! info "Table source"',
        "    Generated from `schema/terms/`. Do not edit by hand.",
        "",
    ]
    return "\n".join(lines)


def render_rules(cls: dict) -> str:
    """Cross-property rules that cardinality alone cannot express."""
    rules = cls.get("rules", [])
    if not rules:
        return "No cross-property rules beyond the cardinalities above.\n"

    lines = [
        f"- **`{r['id']}`** — {localized(r.get('description'))}" for r in rules
    ]
    return "\n".join(lines) + "\n"


def render_vocabulary(data: dict, ns: dict) -> str:
    """Summary page of the erdif: namespace, the target of links in the tables."""
    lines = [
        "# erdif: vocabulary",
        "",
        "This page is the reference of the ERDIF namespace.",
        "Terms reused from schema.org are not listed here — see their",
        "definitions directly at [schema.org](https://schema.org/).",
        "",
    ]

    seen = set()

    lines += ["## Classes", ""]
    for cls in data["classes"]:
        for t in cls.get("types", []):
            if t.startswith("erdif:") and t not in seen:
                seen.add(t)
                local = t.split(":", 1)[1]
                lines += [
                    f"### {local} {{ #class-{to_kebab(local)} }}",
                    "",
                    f"`{expand(t, ns)}`",
                    "",
                    localized(cls.get("description")),
                    "",
                ]

    lines += ["## Properties", ""]
    props = {}
    for cls in data["classes"]:
        for p in cls.get("properties", []):
            iri = p["iri"]
            if iri.startswith("erdif:") and iri not in props:
                props[iri] = (p, cls["name"])

    for iri in sorted(props):
        p, owner = props[iri]
        local = iri.split(":", 1)[1]
        lines += [
            f"### {local} {{ #prop-{to_kebab(local)} }}",
            "",
            f"`{expand(iri, ns)}`",
            "",
            f"Domain: `{owner}`. Range: `{p.get('range', '')}`.",
            "",
            localized(p.get("description")),
            "",
        ]

    lines += [
        "---",
        "",
        "*Generated from `schema/terms/`. Do not edit by hand.*",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if not SRC.is_dir():
        print(f"ERROR: {SRC} does not exist", file=sys.stderr)
        return 1

    data = load_terms(ROOT)
    ns = load_namespaces(data)

    OUT.mkdir(parents=True, exist_ok=True)

    for cls in data["classes"]:
        write_if_changed(OUT / f"terms-{cls['file']}.md", render_class(cls, ns))
        write_if_changed(OUT / f"rules-{cls['file']}.md", render_rules(cls))

    write_if_changed(ROOT / "docs" / "vocabulary.md", render_vocabulary(data, ns))

    print(f"terms: {len(data['classes'])} classes + vocabulary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
