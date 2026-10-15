#!/usr/bin/env python3
"""
Check that schema/context.jsonld and the term registry schema/terms/ agree.

The context and the term registry are two hand-maintained files describing
the same vocabulary, so they can drift apart. This script fails the build
when they do. It verifies that:

1. every namespace of the registry is declared in the context,
2. every term of the registry is declared in the context **explicitly** —
   relying on `@vocab` alone would silently break if the default vocabulary
   ever changed, and it gives the term no datatype,
3. every term expands to exactly the IRI the registry assigns to it,
4. terms with a numeric, boolean or date range are coerced with `@type`,
   so that expansion produces typed literals,
5. every term of the context is either in the registry, or a known nested
   schema.org helper property (the contents of QuantitativeValue,
   GeoCoordinates and PostalAddress).

Usage:
    python scripts/check_context.py
"""

import json
import sys
from pathlib import Path

from pyld import jsonld

from docs_common import load_terms

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT / "schema" / "context.jsonld"

# Properties of schema.org types reused as ranges. They are not ERDIF terms,
# but documents cannot be written without them, so the context declares them.
NESTED_HELPERS = {
    "value", "unitCode",                                   # QuantitativeValue
    "latitude", "longitude",                               # GeoCoordinates
    "streetAddress", "addressLocality", "addressRegion",
    "postalCode", "addressCountry",                        # PostalAddress
}

# Ranges that must carry a datatype coercion in the context.
TYPED_RANGES = {
    "xsd:integer": "http://www.w3.org/2001/XMLSchema#integer",
    "xsd:decimal": "http://www.w3.org/2001/XMLSchema#decimal",
    "xsd:double": "http://www.w3.org/2001/XMLSchema#double",
    "xsd:boolean": "http://www.w3.org/2001/XMLSchema#boolean",
    "xsd:dateTime": "http://www.w3.org/2001/XMLSchema#dateTime",
}


def expand_curie(curie: str, namespaces: dict) -> str:
    if ":" not in curie:
        return curie
    prefix, local = curie.split(":", 1)
    base = namespaces.get(prefix)
    return base + local if base else curie


def expanded_iri(ctx: dict, term: str) -> str | None:
    """Expand a single term through the context, as a processor would."""
    out = jsonld.expand({"@context": ctx, "@id": "urn:x", term: "probe"})
    if not out:
        return None
    keys = [k for k in out[0] if not k.startswith("@")]
    return keys[0] if len(keys) == 1 else None


def main() -> int:
    terms = load_terms(ROOT)
    ctx = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
    namespaces = terms["namespaces"]

    errors: list[str] = []
    declared = {k: v for k, v in ctx.items() if not k.startswith("@")}
    registry_terms: dict[str, dict] = {}

    for prefix, iri in namespaces.items():
        if ctx.get(prefix) != iri and prefix != "rdf":
            if ctx.get(prefix) is None:
                errors.append(f"namespace `{prefix}` is missing from the context")
            else:
                errors.append(
                    f"namespace `{prefix}` is `{ctx[prefix]}` in the context "
                    f"but `{iri}` in the registry"
                )

    for cls in terms["classes"]:
        for prop in cls["properties"]:
            term = prop["term"]
            want = expand_curie(prop["iri"], namespaces)
            previous = registry_terms.get(term)
            if previous and previous["iri"] != prop["iri"]:
                errors.append(
                    f"term `{term}` is mapped to `{previous['iri']}` and "
                    f"`{prop['iri']}` in different classes"
                )
            registry_terms[term] = prop

            if term not in declared:
                errors.append(
                    f"term `{term}` ({cls['name']}) is not declared in the context; "
                    "it would resolve only through @vocab"
                )
                continue

            got = expanded_iri(ctx, term)
            if got != want:
                errors.append(
                    f"term `{term}` ({cls['name']}) expands to `{got}`, "
                    f"but the registry says `{want}`"
                )

            rng = prop.get("range", "")
            if rng in TYPED_RANGES:
                definition = declared[term]
                coerced = isinstance(definition, dict) and definition.get("@type")
                if coerced != TYPED_RANGES[rng] and coerced != rng:
                    errors.append(
                        f"term `{term}` ({cls['name']}) has range `{rng}` but the "
                        f"context coerces it to `{coerced}`"
                    )

    for term in sorted(declared):
        if term in registry_terms or term in NESTED_HELPERS:
            continue
        if isinstance(declared[term], str) and term in namespaces:
            continue  # namespace prefix
        errors.append(
            f"term `{term}` is declared in the context but is not in the registry"
        )

    if errors:
        print("context and registry disagree:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"context OK: {len(registry_terms)} registry terms, "
        f"{len(NESTED_HELPERS)} nested helpers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
