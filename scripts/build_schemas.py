#!/usr/bin/env python3
"""
Generate JSON Schema files schema/<class>.schema.json from the term registry
schema/terms/ and the codelists in codelists/.

Structure (types, required properties, cardinality, codelists) comes from
the registry. Constraints the registry cannot express are stored next to
the term as a `jsonSchema` fragment, merged into the generated schema:

- on a property: constraints of its value (pattern, minimum, ...),
- on a rule: a fragment added to the class under `allOf`.

A rule may instead carry `appliesTo`, which derives the constraint from the
`appliesTo` lists in the codelist:

- {"property": "accessibility", "value": "Realty"} — the property must not
  use listed codes whose `appliesTo` excludes "Realty",
- {"property": "connection", "valueFrom": "network"} — the same, with the
  allowed scope taken from the value of the sibling property `network`.

Rules without either stay documentation only. The schemas stay open
(unknown properties are allowed), so that documents of a newer minor
version remain valid against an older schema.

The schemas are committed, because they are published artifacts. CI runs
this script with --check, which fails when they are out of date.

Usage:
    python scripts/build_schemas.py           # write the schemas
    python scripts/build_schemas.py --check   # verify they are up to date
"""

import json
import sys
from pathlib import Path

from docs_common import load_terms, localized, to_kebab

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "schema"
CODELISTS = ROOT / "codelists"
COMMON = "common.schema.json"

# ISO 8601 date-time with a time zone. The pattern enforces the time zone
# even for validators that treat `format` as an annotation only.
DATETIME = {"type": "string", "format": "date-time", "pattern": "(Z|[+-][0-9]{2}:[0-9]{2})$"}

XSD = {
    "xsd:string": {"type": "string", "minLength": 1},
    "xsd:dateTime": DATETIME,
    "xsd:decimal": {"type": "number"},
    "xsd:integer": {"type": "integer"},
    "xsd:boolean": {"type": "boolean"},
    "xsd:anyURI": {"type": "string", "format": "uri"},
}


class RegistryError(Exception):
    pass


def load_codelist(name: str) -> dict:
    path = CODELISTS / f"{to_kebab(name)}.json"
    if not path.is_file():
        raise RegistryError(f"codelist `{name}` has no file {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != name:
        raise RegistryError(f"{path.name} declares name `{data.get('name')}`, expected `{name}`")
    return data


def codelist_schema(name: str) -> dict:
    data = load_codelist(name)
    codes = [v["code"] for v in data["values"]]
    if data.get("closed"):
        return {"type": "string", "enum": codes}
    # Open codelist: any code is valid, listed ones are offered to editors.
    return {"type": "string", "minLength": 1, "examples": codes}


def value_schema(prop: dict, files: dict) -> dict:
    rng = prop["range"]
    prefix, local = rng.split(":", 1)

    if prop.get("languageMap"):
        schema = {"$ref": f"{COMMON}#/$defs/languageMap"}
    elif rng in XSD:
        schema = dict(XSD[rng])
    elif prefix == "erdif-cl":
        schema = codelist_schema(prop.get("codelist", local))
    elif prefix == "erdif":
        if local not in files:
            raise RegistryError(f"`{prop['term']}` has range `{rng}`, which is not a class")
        schema = {"$ref": f"{files[local]}.schema.json"}
    elif prefix == "schema":
        schema = {"$ref": f"{COMMON}#/$defs/{local}"}
    else:
        raise RegistryError(f"`{prop['term']}` has unsupported range `{rng}`")

    schema.update(prop.get("jsonSchema", {}))
    return schema


def property_schema(prop: dict, files: dict) -> dict:
    schema = value_schema(prop, files)
    card = prop.get("cardinality")
    if card in ("0..*", "1..*"):
        schema = {"type": "array", "items": schema}
        if card == "1..*":
            schema["minItems"] = 1
        if "$ref" not in schema["items"]:
            schema["uniqueItems"] = True
    elif card not in (None, "1", "0..1"):
        raise RegistryError(f"`{prop['term']}` has unsupported cardinality `{card}`")
    return {"description": localized(prop.get("description")), **schema}


def type_schema(erdif_type: str) -> dict:
    """@type must be, or contain, the erdif: type (multiple typing rule)."""
    return {
        "description": f"Must be or contain `{erdif_type}`, usually next to a schema.org type.",
        "anyOf": [
            {"const": erdif_type},
            {"type": "array", "items": {"type": "string"}, "contains": {"const": erdif_type}},
        ],
    }


def excluded_codes(codelist: dict, scope: str) -> list[str]:
    """Listed codes whose appliesTo does not include the scope."""
    return [
        v["code"] for v in codelist["values"]
        if v.get("appliesTo") and scope not in v["appliesTo"]
    ]


def not_codes(prop: dict, codes: list[str]) -> dict:
    forbidden = {"not": {"enum": codes}}
    if prop.get("cardinality") in ("0..*", "1..*"):
        forbidden = {"items": forbidden}
    return {"properties": {prop["term"]: forbidden}}


def applies_to_schema(cls: dict, check: dict) -> dict:
    props = {p["term"]: p for p in cls["properties"]}
    prop = props[check["property"]]
    codelist = load_codelist(prop["codelist"])

    if "value" in check:
        return not_codes(prop, excluded_codes(codelist, check["value"]))

    scopes = sorted({s for v in codelist["values"] for s in v.get("appliesTo", [])})
    source = check["valueFrom"]
    return {
        "allOf": [
            {
                "if": {"required": [source], "properties": {source: {"const": scope}}},
                "then": not_codes(prop, excluded_codes(codelist, scope)),
            }
            for scope in scopes
        ]
    }


def class_schema(cls: dict, registry: dict, files: dict) -> dict:
    erdif_type = next(t for t in cls["types"] if t.startswith("erdif:"))
    is_root = cls["file"] == registry["root"]

    required = ["@type"]
    properties = {"@type": type_schema(erdif_type)}

    if is_root:
        ctx = registry["context"]
        required.insert(0, "@context")
        properties = {
            "@context": {
                "description": "The ERDIF context, alone or first among other contexts.",
                "anyOf": [
                    {"const": ctx},
                    {"type": "array", "prefixItems": [{"const": ctx}]},
                ],
            },
            **properties,
        }

    for prop in cls["properties"]:
        properties[prop["term"]] = property_schema(prop, files)
        if prop.get("required"):
            required.append(prop["term"])

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{registry['schemaBase']}{cls['file']}.schema.json",
        "title": cls["name"],
        "description": localized(cls.get("description")),
        "type": "object",
        "required": required,
        "properties": properties,
    }

    rules = []
    for rule in cls.get("rules", []):
        if "jsonSchema" in rule:
            rules.append({"$comment": rule["id"], **rule["jsonSchema"]})
        elif "appliesTo" in rule:
            rules.append({"$comment": rule["id"], **applies_to_schema(cls, rule["appliesTo"])})
    if rules:
        schema["allOf"] = rules

    return schema


def render(registry: dict) -> dict[Path, str]:
    files = {c["name"]: c["file"] for c in registry["classes"]}
    return {
        OUT / f"{cls['file']}.schema.json":
            json.dumps(class_schema(cls, registry, files), indent=2, ensure_ascii=False) + "\n"
        for cls in registry["classes"]
    }


def main() -> int:
    check = "--check" in sys.argv[1:]

    try:
        outputs = render(load_terms(ROOT))
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    expected = set(outputs) | {OUT / COMMON}
    orphans = sorted(set(OUT.glob("*.schema.json")) - expected)

    if check:
        stale = [p for p, text in outputs.items()
                 if not p.is_file() or p.read_text(encoding="utf-8") != text]
        problems = [f"{p.name} is out of date" for p in stale]
        problems += [f"{p.name} does not belong to any class" for p in orphans]
        if problems:
            print("JSON Schemas do not match the term registry:", file=sys.stderr)
            for msg in problems:
                print(f"  - {msg}", file=sys.stderr)
            print("Run: python scripts/build_schemas.py", file=sys.stderr)
            return 1
        print(f"schemas OK: {len(outputs)} classes")
        return 0

    for path, text in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
    for path in orphans:
        print(f"WARNING: {path.name} does not belong to any class", file=sys.stderr)

    print(f"schemas: {len(outputs)} classes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
