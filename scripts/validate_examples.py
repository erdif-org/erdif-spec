#!/usr/bin/env python3
"""
Validate the example documents in examples/ against the JSON Schemas.

- examples/valid/*.jsonld must pass the schema and expand as JSON-LD
  (the ERDIF context is loaded from schema/context.jsonld, not the web).
- examples/invalid/*.jsonld must fail with exactly the error declared in
  their `_expect` field, and with no other error — so each invalid example
  provably breaks one rule, not several:

      "_expect": { "path": "/realty/location", "keyword": "required" }

  `path` is the JSON Pointer of the failing value, `keyword` the JSON
  Schema keyword that fails.

Usage:
    python scripts/validate_examples.py
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pyld import jsonld
from referencing import Registry, Resource

from docs_common import load_terms

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
EXAMPLES = ROOT / "examples"


def make_validator(registry_data: dict) -> Draft202012Validator:
    resources = []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)

    root_id = f"{registry_data['schemaBase']}{registry_data['root']}.schema.json"
    root = registry.contents(root_id)
    return Draft202012Validator(root, registry=registry, format_checker=FormatChecker())


def make_loader(context_url: str):
    context = json.loads((SCHEMA_DIR / "context.jsonld").read_text(encoding="utf-8"))

    def loader(url, options=None):
        if url != context_url:
            raise jsonld.JsonLdError(f"unexpected remote document {url}", "loading document failed")
        return {"contextUrl": None, "documentUrl": url, "document": context}

    return loader


def pointer(error) -> str:
    return "".join(f"/{p}" for p in error.absolute_path)


def describe(error) -> str:
    return f"{pointer(error) or '/'} [{error.validator}] {error.message}"


def check_valid(doc: dict, validator, loader) -> list[str]:
    problems = [describe(e) for e in validator.iter_errors(doc)]
    try:
        jsonld.expand(doc, {"documentLoader": loader})
    except jsonld.JsonLdError as exc:
        problems.append(f"JSON-LD expansion failed: {exc}")
    return problems


def check_invalid(doc: dict, validator) -> list[str]:
    expect = doc.get("_expect")
    if not isinstance(expect, dict) or not {"path", "keyword"} <= expect.keys():
        return ['missing `_expect` with "path" and "keyword"']

    errors = list(validator.iter_errors(doc))
    if not errors:
        return ["document is valid, but it should fail"]

    matching = [e for e in errors if pointer(e) == expect["path"] and e.validator == expect["keyword"]]
    others = [e for e in errors if e not in matching]

    problems = []
    if not matching:
        problems.append(f"expected error {expect['path']} [{expect['keyword']}] did not occur")
    problems += [f"unexpected error: {describe(e)}" for e in others]
    return problems


def main() -> int:
    registry_data = load_terms(ROOT)
    validator = make_validator(registry_data)
    loader = make_loader(registry_data["context"])

    failed = 0
    total = 0
    for kind in ("valid", "invalid"):
        for path in sorted((EXAMPLES / kind).glob("*.jsonld")):
            total += 1
            name = f"{kind}/{path.name}"
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                problems = [f"not valid JSON: {exc}"]
            else:
                problems = (check_valid(doc, validator, loader) if kind == "valid"
                            else check_invalid(doc, validator))

            if problems:
                failed += 1
                print(f"FAIL  {name}")
                for p in problems:
                    print(f"        {p}")
            else:
                note = f"  -> {doc['_expect']['path']} [{doc['_expect']['keyword']}]" if kind == "invalid" else ""
                print(f"ok    {name}{note}")

    if total == 0:
        print("ERROR: no examples found", file=sys.stderr)
        return 1
    print(f"\n{total - failed}/{total} examples behave as expected")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
