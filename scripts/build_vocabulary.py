#!/usr/bin/env python3
"""
Generate the ERDIF RDFS/OWL vocabulary (Turtle) from the term registry.

Sources:  schema/terms/*.json, codelists/*.json, schema/common.schema.json
Output:   docs/ns/v1/erdif.ttl

The file is a plain RDFS/OWL vocabulary that tools such as Dataspecer,
Protégé or any RDF library can load directly. It contains:

  * erdif: classes and properties (with domain, range, labels, comments),
  * codelists as classes with their values as skos:Concept instances,
  * the schema.org terms the format reuses, declared the way schema.org
    itself declares them (schema:domainIncludes / schema:rangeIncludes,
    both non-restrictive) so the vocabulary never narrows their meaning.

Usage:
    python scripts/build_vocabulary.py          # write the file
    python scripts/build_vocabulary.py --check  # fail if the file is stale
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docs_common import load_terms, write_if_changed  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "ns" / "v1" / "erdif.ttl"

ONTOLOGY_IRI = "https://erdif-org.github.io/erdif-spec/ns/v1"
SPEC_URL = "https://erdif-org.github.io/erdif-spec/"

PREFIXES = OrderedDict(
    [
        ("erdif", "https://erdif-org.github.io/erdif-spec/ns/v1#"),
        ("erdif-cl", "https://erdif-org.github.io/erdif-spec/codelist/v1/"),
        ("schema", "https://schema.org/"),
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
        ("owl", "http://www.w3.org/2002/07/owl#"),
        ("xsd", "http://www.w3.org/2001/XMLSchema#"),
        ("skos", "http://www.w3.org/2004/02/skos/core#"),
        ("dcterms", "http://purl.org/dc/terms/"),
    ]
)

# Properties of the nested schema.org value types. common.schema.json keeps
# them as JSON Schema only, so the RDF datatypes are declared here.
NESTED_TYPES = {
    "schema:QuantitativeValue": [
        ("schema:value", "xsd:decimal", {"en": "The numeric value.", "cs": "Číselná hodnota."}),
        ("schema:unitCode", "xsd:string", {"en": "UN/CEFACT Recommendation 20 unit code.", "cs": "Kód jednotky podle UN/CEFACT Recommendation 20."}),
    ],
    "schema:GeoCoordinates": [
        ("schema:latitude", "xsd:double", {"en": "WGS 84 latitude.", "cs": "Zeměpisná šířka (WGS 84)."}),
        ("schema:longitude", "xsd:double", {"en": "WGS 84 longitude.", "cs": "Zeměpisná délka (WGS 84)."}),
    ],
    "schema:PostalAddress": [
        ("schema:streetAddress", "xsd:string", {"en": "Street and house number.", "cs": "Ulice a číslo domu."}),
        ("schema:addressLocality", "xsd:string", {"en": "Municipality.", "cs": "Obec."}),
        ("schema:addressRegion", "xsd:string", {"en": "Region.", "cs": "Region."}),
        ("schema:postalCode", "xsd:string", {"en": "Postal code.", "cs": "PSČ."}),
        ("schema:addressCountry", "xsd:string", {"en": "ISO 3166-1 alpha-2 country code.", "cs": "Kód země podle ISO 3166-1 alpha-2."}),
    ],
}

# Short labels for schema.org classes the format subclasses or nests.
SCHEMA_CLASS_LABELS = {
    "schema:Thing": "Thing",
    "schema:RealEstateListing": "Real estate listing",
    "schema:Accommodation": "Accommodation",
    "schema:Person": "Person",
    "schema:Organization": "Organization",
    "schema:Place": "Place",
    "schema:Room": "Room",
    "schema:MediaObject": "Media object",
    "schema:PriceSpecification": "Price specification",
    "schema:QuantitativeValue": "Quantitative value",
    "schema:GeoCoordinates": "Geo coordinates",
    "schema:PostalAddress": "Postal address",
}

DATATYPE_PREFIXES = ("xsd:", "rdf:langString")

# A property used by several ERDIF classes must still have exactly one
# domain: tools such as Dataspecer keep only one domain per property. The
# single domain is the schema.org class the property really belongs to;
# the ERDIF classes reach it through rdfs:subClassOf. Any new multi-domain
# property must be added here, otherwise the build fails.
SHARED_DOMAIN = {
    "schema:name": "schema:Thing",
    "schema:identifier": "schema:Thing",
    "schema:description": "schema:Thing",
    "schema:unitCode": "schema:Thing",
    "schema:floorSize": "schema:Accommodation",
    "erdif:floorLevel": "schema:Accommodation",
    "erdif:accessibility": "schema:Accommodation",
}

# Direct parents of the schema.org classes the format uses, abbreviated to
# the classes that matter here (schema.org's full chain is longer, e.g.
# RealEstateListing ⊂ WebPage ⊂ CreativeWork ⊂ Thing).
SCHEMA_PARENT = {
    "schema:RealEstateListing": "schema:Thing",
    "schema:Accommodation": "schema:Place",
    "schema:Room": "schema:Accommodation",
    "schema:Place": "schema:Thing",
    "schema:Person": "schema:Thing",
    "schema:Organization": "schema:Thing",
    "schema:MediaObject": "schema:Thing",
    "schema:PriceSpecification": "schema:Thing",
    "schema:QuantitativeValue": "schema:Thing",
    "schema:GeoCoordinates": "schema:Thing",
    "schema:PostalAddress": "schema:Thing",
}


def literal(text: str, lang: str | None = None) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"' + (f"@{lang}" if lang else "")


def lang_literals(predicate: str, field) -> list[str]:
    """Render a language map as `predicate "..."@en, "..."@cs`."""
    if not field:
        return []
    if isinstance(field, str):
        return [f"{predicate} {literal(field)}"]
    values = [literal(text, lang) for lang, text in sorted(field.items()) if text]
    return [f"{predicate} {', '.join(values)}"] if values else []


def is_datatype(rng: str) -> bool:
    return rng.startswith(DATATYPE_PREFIXES)


def block(subject: str, statements: list[str]) -> str:
    body = " ;\n    ".join(statements)
    return f"{subject}\n    {body} .\n"


def local_name(curie: str) -> str:
    return curie.split(":", 1)[1]


def build() -> str:
    terms = load_terms(ROOT)
    codelist_dir = ROOT / "codelists"
    common = json.loads((ROOT / "schema" / "common.schema.json").read_text(encoding="utf-8"))

    out: list[str] = []
    out.append("# ERDIF vocabulary — generated by scripts/build_vocabulary.py from\n"
               "# schema/terms/*.json and codelists/*.json. Do not edit by hand.\n")
    for prefix, iri in PREFIXES.items():
        out.append(f"@prefix {prefix}: <{iri}> .")
    out.append("")

    # --- Ontology header -------------------------------------------------
    out.append(block(f"<{ONTOLOGY_IRI}>", [
        "a owl:Ontology",
        f"rdfs:label {literal('ERDIF vocabulary', 'en')}, {literal('Slovník ERDIF', 'cs')}",
        f"rdfs:comment {literal('European Real Estate Data Interchange Format — classes and properties of the format.', 'en')}, "
        f"{literal('European Real Estate Data Interchange Format — třídy a vlastnosti formátu.', 'cs')}",
        f"dcterms:source <{SPEC_URL}>",
        f"owl:versionInfo {literal('v1')}",
    ]))

    # --- Collect properties across classes --------------------------------
    # One property may be used by several classes; collect all domains.
    properties: "OrderedDict[str, dict]" = OrderedDict()
    schema_superclasses: "OrderedDict[str, None]" = OrderedDict()

    out.append("#" + "=" * 70)
    out.append("# Classes")
    out.append("#" + "=" * 70 + "\n")

    for cls in terms["classes"]:
        class_iri = f"erdif:{cls['name']}"
        supers = [t for t in cls.get("types", []) if t.startswith("schema:")]
        for s in supers:
            schema_superclasses[s] = None
        statements = ["a owl:Class", f"rdfs:label {literal(cls['name'], 'en')}"]
        statements += lang_literals("rdfs:comment", cls.get("description"))
        if len(supers) == 1:
            statements.append("rdfs:subClassOf " + supers[0])
        else:
            # Several schema.org types mean "one of them" in a document
            # (e.g. Contact is a Person OR an Organization); subClassOf of
            # all would mean their intersection, so only point to them and
            # hang the class directly under schema:Thing.
            statements.append("rdfs:subClassOf schema:Thing")
            if supers:
                statements.append("rdfs:seeAlso " + ", ".join(supers))
        statements.append(f"rdfs:isDefinedBy <{ONTOLOGY_IRI}>")
        out.append(block(class_iri, statements))

        for prop in cls["properties"]:
            entry = properties.setdefault(prop["iri"], {
                "term": prop["term"], "range": prop["range"],
                "description": prop.get("description"), "domains": [],
            })
            entry["domains"].append(class_iri)
            if entry["range"] != prop["range"]:
                raise SystemExit(f"{prop['iri']}: conflicting ranges {entry['range']} / {prop['range']}")

    for type_iri, props in NESTED_TYPES.items():
        for prop_iri, rng, desc in props:
            entry = properties.setdefault(prop_iri, {
                "term": local_name(prop_iri), "range": rng, "description": desc, "domains": [],
            })
            entry["domains"].append(type_iri)
            if entry["range"] != rng:
                raise SystemExit(f"{prop_iri}: conflicting ranges {entry['range']} / {rng}")

    def single_domain(iri: str, domains: list[str]) -> str:
        if len(domains) == 1:
            return domains[0]
        try:
            return SHARED_DOMAIN[iri]
        except KeyError:
            raise SystemExit(f"{iri} is used by {', '.join(domains)}; add it to SHARED_DOMAIN")

    # --- Properties -------------------------------------------------------
    def property_block(iri: str, entry: dict, reused: bool) -> str:
        rng = entry["range"]
        if reused:
            # schema.org's own, non-restrictive typing.
            statements = ["a rdf:Property"]
            domain_pred, range_pred = "schema:domainIncludes", "schema:rangeIncludes"
        else:
            statements = ["a " + ("owl:DatatypeProperty" if is_datatype(rng) else "owl:ObjectProperty")]
            domain_pred, range_pred = "rdfs:domain", "rdfs:range"
        statements.append(f"rdfs:label {literal(entry['term'], 'en')}")
        statements += lang_literals("rdfs:comment", entry.get("description"))
        statements.append(f"{domain_pred} {single_domain(iri, entry['domains'])}")
        statements.append(f"{range_pred} {rng}")
        if not reused:
            statements.append(f"rdfs:isDefinedBy <{ONTOLOGY_IRI}>")
        return block(iri, statements)

    out.append("#" + "=" * 70)
    out.append("# Properties defined by ERDIF")
    out.append("#" + "=" * 70 + "\n")
    for iri, entry in properties.items():
        if iri.startswith("erdif:"):
            out.append(property_block(iri, entry, reused=False))

    out.append("#" + "=" * 70)
    out.append("# schema.org terms reused by ERDIF")
    out.append("# (declared with schema:domainIncludes / schema:rangeIncludes, which do")
    out.append("#  not constrain the terms; the comments are ERDIF usage notes)")
    out.append("#" + "=" * 70 + "\n")
    for iri, entry in properties.items():
        if iri.startswith("schema:"):
            out.append(property_block(iri, entry, reused=True))

    # Nested schema.org value types.
    for type_iri in NESTED_TYPES:
        schema_superclasses.pop(type_iri, None)
        description = common["$defs"][local_name(type_iri)]["description"]
        out.append(block(type_iri, [
            "a owl:Class",
            f"rdfs:label {literal(SCHEMA_CLASS_LABELS[type_iri], 'en')}",
            f"rdfs:comment {literal(description, 'en')}",
            f"rdfs:subClassOf {SCHEMA_PARENT[type_iri]}",
            "rdfs:isDefinedBy <https://schema.org/>",
        ]))

    # schema.org classes used as superclasses or shared domains, with their
    # (abbreviated) parents, so the hierarchy resolves without loading schema.org.
    needed = list(schema_superclasses) + [d for d in SHARED_DOMAIN.values()]
    closure: "OrderedDict[str, None]" = OrderedDict()
    for c in needed:
        while c and c not in closure:
            closure[c] = None
            c = SCHEMA_PARENT.get(c)
    for c in closure:
        statements = [
            "a owl:Class",
            f"rdfs:label {literal(SCHEMA_CLASS_LABELS.get(c, local_name(c)), 'en')}",
        ]
        if c in SCHEMA_PARENT:
            statements.append(f"rdfs:subClassOf {SCHEMA_PARENT[c]}")
        statements.append("rdfs:isDefinedBy <https://schema.org/>")
        out.append(block(c, statements))

    # --- Codelists --------------------------------------------------------
    out.append("#" + "=" * 70)
    out.append("# Codelists — each is a class whose instances are skos:Concepts")
    out.append("#" + "=" * 70 + "\n")
    for path in sorted(codelist_dir.glob("*.json")):
        cl = json.loads(path.read_text(encoding="utf-8"))
        cl_iri = f"erdif-cl:{cl['name']}"
        statements = [
            "a owl:Class, skos:ConceptScheme",
            "rdfs:subClassOf skos:Concept",
            f"rdfs:label {literal(cl['name'], 'en')}",
        ]
        statements += lang_literals("rdfs:comment", cl.get("description"))
        statements.append(f"rdfs:isDefinedBy <{ONTOLOGY_IRI}>")
        out.append(block(cl_iri, statements))
        for value in cl.get("values", []):
            value_iri = f"<{PREFIXES['erdif-cl']}{cl['name']}#{value['code']}>"
            statements = [f"a skos:Concept, {cl_iri}", f"skos:inScheme {cl_iri}", f"skos:notation {literal(value['code'])}"]
            statements += lang_literals("skos:prefLabel", value.get("labels"))
            statements += lang_literals("skos:definition", value.get("description"))
            out.append(block(value_iri, statements))

    return "\n".join(out)


def main(check: bool = False) -> int:
    content = build()
    if check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            print(f"{OUTPUT.relative_to(ROOT)} is out of date; run scripts/build_vocabulary.py", file=sys.stderr)
            return 1
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    write_if_changed(OUTPUT, content)
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
