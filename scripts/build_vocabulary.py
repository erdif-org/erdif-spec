#!/usr/bin/env python3
"""
Generate the RDFS/OWL vocabulary docs/ns/v1/erdif.ttl from the term
registry schema/terms/, the codelists in codelists/ and the nested value
types in schema/common.schema.json.

The vocabulary is what linked-data tools consume: it is the Turtle
counterpart of the JSON-LD context, published next to it at
https://erdif-org.github.io/erdif-spec/ns/v1/erdif.ttl, and it can be
imported as a vocabulary into modelling tools such as Dataspecer.

What is generated:

- the ontology header (`owl:Ontology`),
- every class of the registry as `owl:Class`, with `rdfs:subClassOf` to its
  schema.org type when it has exactly one (two alternatives, as in Contact =
  Person or Organization, are given as `rdfs:seeAlso`, because
  `rdfs:subClassOf` both would mean their intersection),
- every `erdif:` property as `owl:DatatypeProperty` (XSD or `rdf:langString`
  range) or `owl:ObjectProperty`, with `rdfs:domain` for a single domain and
  `schema:domainIncludes` for several,
- every reused `schema:` property as `rdf:Property` with
  `schema:domainIncludes` / `schema:rangeIncludes` only, so the meaning of
  the schema.org term is not narrowed by an `rdfs:domain`,
- the nested schema.org value types (QuantitativeValue, GeoCoordinates,
  PostalAddress) and the schema.org superclasses, so that nothing the
  vocabulary refers to is left undeclared,
- every codelist as `owl:Class` + `skos:ConceptScheme` and its values as
  `skos:Concept`.

Cardinalities and required flags are not part of a vocabulary; they belong
to an application profile (and to the JSON Schemas).

The file is committed, because it is a published artifact. CI runs this
script with --check, which fails when it is out of date.

Usage:
    python scripts/build_vocabulary.py           # write docs/ns/v1/erdif.ttl
    python scripts/build_vocabulary.py --check   # verify it is up to date
"""

import json
import sys
from pathlib import Path

from docs_common import load_terms, to_kebab, write_if_changed

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "ns" / "v1" / "erdif.ttl"
CODELISTS = ROOT / "codelists"
COMMON = ROOT / "schema" / "common.schema.json"

ONTOLOGY_IRI = "https://erdif-org.github.io/erdif-spec/ns/v1"
VERSION = "v1"
SCHEMA_ORG = "https://schema.org/"

# Languages of the generated labels and comments, in output order. Other
# languages present in the data are appended alphabetically.
LANGS = ("en", "cs")

PREFIXES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "schema": SCHEMA_ORG,
}

ONTOLOGY_LABEL = {
    "en": "ERDIF - European Real Estate Data Interchange Format",
    "cs": "ERDIF - Evropský formát pro výměnu realitních dat",
}
ONTOLOGY_COMMENT = {
    "en": "Vocabulary of the European Real Estate Data Interchange Format: "
          "the classes, properties and codelists used by ERDIF documents.",
    "cs": "Slovník Evropského formátu pro výměnu realitních dat: třídy, "
          "vlastnosti a číselníky používané dokumenty ERDIF.",
}

# schema.org classes the vocabulary refers to (as superclasses or nested
# value types). They are declared minimally, so that nothing is left
# dangling when the file is imported on its own. The comments of the nested
# value types are taken from common.schema.json instead.
SCHEMA_CLASSES = {
    "RealEstateListing": "A listing that describes one or more real-estate offerings.",
    "Accommodation": "A place that can accommodate human beings, e.g. an apartment or a house.",
    "Place": "Entities that have a somewhat fixed, physical extension.",
    "Room": "A room is a distinguishable space within a structure.",
    "MediaObject": "A media object, such as an image, video or audio object.",
    "PriceSpecification": "A structured value representing a price or price range.",
    "Person": "A person (alive, dead, undead, or fictional).",
    "Organization": "An organization such as a school, NGO, corporation, club, etc.",
    "QuantitativeValue": "A point value or interval for product characteristics and other purposes.",
    "GeoCoordinates": "The geographic coordinates of a place or event.",
    "PostalAddress": "The mailing address.",
}

# Properties of the nested schema.org value types, with the datatype ERDIF
# uses for them. They are not ERDIF terms, but ERDIF documents cannot be
# written without them, so the vocabulary declares them the same way the
# JSON-LD context does.
NESTED_PROPERTIES = {
    "QuantitativeValue": {
        "value": ("xsd:decimal", {
            "en": "The numeric value of the quantity.",
            "cs": "Číselná hodnota veličiny.",
        }),
        "unitCode": ("xsd:string", {
            "en": "Unit of measure per UN/CEFACT Recommendation 20 (e.g. MTK for square metres).",
            "cs": "Měrná jednotka podle UN/CEFACT Recommendation 20 (např. MTK pro m²).",
        }),
    },
    "GeoCoordinates": {
        "latitude": ("xsd:double", {
            "en": "Latitude in WGS 84 decimal degrees.",
            "cs": "Zeměpisná šířka ve stupních WGS 84.",
        }),
        "longitude": ("xsd:double", {
            "en": "Longitude in WGS 84 decimal degrees.",
            "cs": "Zeměpisná délka ve stupních WGS 84.",
        }),
    },
    "PostalAddress": {
        "streetAddress": ("xsd:string", {
            "en": "Street and house number.",
            "cs": "Ulice a číslo domu.",
        }),
        "addressLocality": ("xsd:string", {
            "en": "Municipality or city.",
            "cs": "Obec nebo město.",
        }),
        "addressRegion": ("xsd:string", {
            "en": "Region, state or province.",
            "cs": "Kraj, region nebo provincie.",
        }),
        "postalCode": ("xsd:string", {
            "en": "Postal code.",
            "cs": "Poštovní směrovací číslo.",
        }),
        "addressCountry": ("xsd:string", {
            "en": "Country as a two-letter ISO 3166-1 code.",
            "cs": "Země jako dvoupísmenný kód ISO 3166-1.",
        }),
    },
}


class RegistryError(Exception):
    pass


# --- Turtle helpers ---------------------------------------------------------

def literal(text: str, lang: str | None = None) -> str:
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"' + (f"@{lang}" if lang else "")


def lang_literals(field: dict | str | None) -> list[str]:
    """Language-tagged literals for a language map, in LANGS order."""
    if isinstance(field, str):
        return [literal(field)]
    if not field:
        return []
    ordered = [lang for lang in LANGS if field.get(lang)]
    ordered += sorted(lang for lang in field if lang not in LANGS and field[lang])
    return [literal(field[lang], lang) for lang in ordered]


def is_datatype(rng: str) -> bool:
    return rng.startswith("xsd:") or rng == "rdf:langString"


def block(subject: str, triples: list[tuple[str, list[str]]]) -> str:
    """Render one subject with its predicate-object lists."""
    lines = [subject]
    body = [(p, objs) for p, objs in triples if objs]
    for i, (pred, objs) in enumerate(body):
        end = " ." if i == len(body) - 1 else " ;"
        lines.append(f"    {pred} {', '.join(objs)}{end}")
    return "\n".join(lines) + "\n"


# --- Sources ----------------------------------------------------------------

def load_codelist(name: str) -> dict:
    path = CODELISTS / f"{to_kebab(name)}.json"
    if not path.is_file():
        raise RegistryError(f"codelist `{name}` has no file {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != name:
        raise RegistryError(f"{path.name} declares name `{data.get('name')}`, expected `{name}`")
    return data


def nested_type_descriptions() -> dict[str, str]:
    """Descriptions of the nested schema.org types from common.schema.json."""
    defs = json.loads(COMMON.read_text(encoding="utf-8"))["$defs"]
    return {name: defs[name]["description"] for name in NESTED_PROPERTIES if name in defs}


def collect_properties(registry: dict) -> dict[str, dict]:
    """Group the registry properties by IRI; the same IRI in several classes
    is one property with several domains."""
    props: dict[str, dict] = {}
    for cls in registry["classes"]:
        for prop in cls["properties"]:
            entry = props.setdefault(prop["iri"], {
                "term": prop["term"], "ranges": [], "domains": [], "descriptions": [],
            })
            if entry["term"] != prop["term"]:
                raise RegistryError(
                    f"`{prop['iri']}` is called `{entry['term']}` and `{prop['term']}` "
                    "in different classes"
                )
            if prop["range"] not in entry["ranges"]:
                entry["ranges"].append(prop["range"])
            entry["domains"].append(f"erdif:{cls['name']}")
            entry["descriptions"].append((cls["name"], prop.get("description") or {}))
    return props


def property_comments(descriptions: list[tuple[str, dict]]) -> list[str]:
    """One comment per language. When the classes describe the property
    differently, the descriptions are joined and prefixed with the class."""
    distinct: list[tuple[str, dict]] = []
    for cls_name, desc in descriptions:
        if desc not in (d for _, d in distinct):
            distinct.append((cls_name, desc))
    if len(distinct) == 1:
        return lang_literals(distinct[0][1])
    langs = [lang for lang in LANGS if any(d.get(lang) for _, d in distinct)]
    return [
        literal(" ".join(f"{cls_name}: {d[lang]}" for cls_name, d in distinct if d.get(lang)), lang)
        for lang in langs
    ]


# --- Rendering --------------------------------------------------------------

def render_header(registry: dict) -> str:
    ns = registry["namespaces"]
    prefixes = {**PREFIXES, "erdif": ns["erdif"], "erdif-cl": ns["erdif-cl"]}
    lines = [
        "# ERDIF vocabulary (RDFS/OWL)",
        "# Generated by scripts/build_vocabulary.py from schema/terms/, codelists/",
        "# and schema/common.schema.json. Do not edit by hand.",
        "",
    ]
    lines += [f"@prefix {p}: <{iri}> ." for p, iri in prefixes.items()]
    lines.append("")
    lines.append(block(f"<{ONTOLOGY_IRI}>", [
        ("a", ["owl:Ontology"]),
        ("rdfs:label", lang_literals(ONTOLOGY_LABEL)),
        ("rdfs:comment", lang_literals(ONTOLOGY_COMMENT)),
        ("owl:versionInfo", [literal(VERSION)]),
        ("rdfs:seeAlso", [f"<{registry['context']}>"]),
    ]))
    return "\n".join(lines)


def render_classes(registry: dict) -> str:
    out = ["", "# --- Classes ---", ""]
    for cls in registry["classes"]:
        schema_types = [t for t in cls["types"] if t.startswith("schema:")]
        erdif_types = [t for t in cls["types"] if t.startswith("erdif:")]
        if erdif_types != [f"erdif:{cls['name']}"]:
            raise RegistryError(f"class `{cls['name']}` must have exactly the type erdif:{cls['name']}")
        for t in schema_types:
            if t.split(":", 1)[1] not in SCHEMA_CLASSES:
                raise RegistryError(f"schema.org class `{t}` is not in SCHEMA_CLASSES")
        # Exactly one schema.org type is a superclass. Several (Contact is a
        # Person or an Organization) are alternatives, and rdfs:subClassOf
        # of both would mean their intersection, so they are only linked.
        out.append(block(f"erdif:{cls['name']}", [
            ("a", ["owl:Class"]),
            ("rdfs:label", [literal(cls["name"], "en")]),
            ("rdfs:comment", lang_literals(cls.get("description"))),
            ("rdfs:subClassOf", schema_types if len(schema_types) == 1 else []),
            ("rdfs:seeAlso", schema_types if len(schema_types) > 1 else []),
            ("rdfs:isDefinedBy", [f"<{ONTOLOGY_IRI}>"]),
        ]))
    return "\n".join(out)


def render_schema_classes() -> str:
    out = ["", "# --- schema.org classes referred to by the vocabulary ---", ""]
    nested = nested_type_descriptions()
    for name, comment in SCHEMA_CLASSES.items():
        out.append(block(f"schema:{name}", [
            ("a", ["owl:Class"]),
            ("rdfs:label", [literal(name, "en")]),
            ("rdfs:comment", [literal(nested.get(name, comment), "en")]),
            ("rdfs:isDefinedBy", [f"<{SCHEMA_ORG}>"]),
        ]))
    return "\n".join(out)


def render_erdif_properties(props: dict[str, dict]) -> str:
    out = ["", "# --- erdif: properties ---", ""]
    for iri in sorted(p for p in props if p.startswith("erdif:")):
        entry = props[iri]
        if len(entry["ranges"]) != 1:
            raise RegistryError(f"`{iri}` has several ranges: {entry['ranges']}")
        rng = entry["ranges"][0]
        kind = "owl:DatatypeProperty" if is_datatype(rng) else "owl:ObjectProperty"
        single = len(entry["domains"]) == 1
        out.append(block(iri, [
            ("a", [kind]),
            ("rdfs:label", [literal(entry["term"], "en")]),
            ("rdfs:comment", property_comments(entry["descriptions"])),
            ("rdfs:domain", entry["domains"] if single else []),
            ("schema:domainIncludes", entry["domains"] if not single else []),
            ("rdfs:range", [rng]),
            ("rdfs:isDefinedBy", [f"<{ONTOLOGY_IRI}>"]),
        ]))
    return "\n".join(out)


def render_schema_properties(props: dict[str, dict]) -> str:
    """Reused schema.org properties, merged with the properties of the nested
    value types (schema:unitCode is used by both Price and QuantitativeValue)."""
    merged: dict[str, dict] = {}
    for iri, entry in props.items():
        if iri.startswith("schema:"):
            merged[iri] = {
                "term": entry["term"],
                "ranges": list(entry["ranges"]),
                "domains": list(entry["domains"]),
                "descriptions": list(entry["descriptions"]),
            }
    for type_name, nested in NESTED_PROPERTIES.items():
        for term, (rng, desc) in nested.items():
            entry = merged.setdefault(f"schema:{term}", {
                "term": term, "ranges": [], "domains": [], "descriptions": [],
            })
            if rng not in entry["ranges"]:
                entry["ranges"].append(rng)
            entry["domains"].append(f"schema:{type_name}")
            entry["descriptions"].append((type_name, desc))

    out = ["", "# --- schema.org properties reused by ERDIF ---", ""]
    for iri in sorted(merged):
        entry = merged[iri]
        out.append(block(iri, [
            ("a", ["rdf:Property"]),
            ("rdfs:label", [literal(entry["term"], "en")]),
            ("rdfs:comment", property_comments(entry["descriptions"])),
            ("schema:domainIncludes", entry["domains"]),
            ("schema:rangeIncludes", entry["ranges"]),
            ("rdfs:isDefinedBy", [f"<{SCHEMA_ORG}>"]),
        ]))
    return "\n".join(out)


def render_codelists(registry: dict, props: dict[str, dict]) -> str:
    base = registry["namespaces"]["erdif-cl"]
    names = sorted({
        entry["ranges"][0].split(":", 1)[1]
        for entry in props.values() if entry["ranges"][0].startswith("erdif-cl:")
    })
    out = ["", "# --- Codelists ---", ""]
    for name in names:
        data = load_codelist(name)
        scheme = f"erdif-cl:{name}"
        out.append(block(scheme, [
            ("a", ["owl:Class", "skos:ConceptScheme"]),
            ("rdfs:subClassOf", ["skos:Concept"]),
            ("rdfs:label", [literal(name, "en")]),
            ("rdfs:comment", lang_literals(data.get("description"))),
            ("rdfs:isDefinedBy", [f"<{ONTOLOGY_IRI}>"]),
        ]))
        for value in data["values"]:
            code = value["code"]
            out.append(block(f"<{base}{name}#{code}>", [
                ("a", ["skos:Concept", scheme]),
                ("skos:inScheme", [scheme]),
                ("skos:notation", [literal(code)]),
                ("skos:prefLabel", lang_literals(value.get("labels"))),
                ("skos:definition", lang_literals(value.get("description"))),
            ]))
    return "\n".join(out)


def render(registry: dict) -> str:
    props = collect_properties(registry)
    return "".join([
        render_header(registry),
        render_classes(registry),
        render_schema_classes(),
        render_erdif_properties(props),
        render_schema_properties(props),
        render_codelists(registry, props),
    ])


def main() -> int:
    check = "--check" in sys.argv[1:]

    try:
        text = render(load_terms(ROOT))
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT).as_posix()} is out of date", file=sys.stderr)
            print("Run: python scripts/build_vocabulary.py", file=sys.stderr)
            return 1
        print(f"vocabulary OK: {OUT.relative_to(ROOT).as_posix()}")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_if_changed(OUT, text)
    print(f"vocabulary: {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
