# Namespaces

## Context declaration

All terms of the format are defined in the JSON-LD context
[`schema/context.jsonld`](https://github.com/erdif-org/erdif-spec/blob/main/schema/context.jsonld),
published at `https://erdif-org.github.io/erdif-spec/ns/v1/context.jsonld`.
A document references it in its `@context` key:

```json
{
  "@context": "https://erdif-org.github.io/erdif-spec/ns/v1/context.jsonld",
  ...
}
```

| Prefix     | IRI                                                     | Description                              |
|------------|---------------------------------------------------------|------------------------------------------|
| (default)  | `https://schema.org/`                                   | `@vocab` — default vocabulary            |
| `erdif`    | `https://erdif-org.github.io/erdif-spec/ns/v1#`         | Custom extension for European specifics  |
| `erdif-cl` | `https://erdif-org.github.io/erdif-spec/codelist/v1/`   | Codelist values                          |
| `xsd`      | `http://www.w3.org/2001/XMLSchema#`                     | Literal datatypes                        |

The context declares **every** term of the format explicitly, including the
ones reused from schema.org and the properties of nested schema.org types
(`QuantitativeValue`, `GeoCoordinates`, `PostalAddress`). Numeric, boolean
and date values are coerced to the matching XSD datatype, so expansion
produces typed literals. The context is `@protected`, so a document cannot
redefine a term of the format in its own inline context.

Terms that schema.org already defines with a matching meaning (for example
`price`, `floorSize`, `geo`, `yearBuilt`) are reused. Everything else is
defined in `erdif:` and listed in the [vocabulary](vocabulary.md).

## RDFS/OWL vocabulary

The same terms are published as an RDFS/OWL vocabulary in Turtle at
`https://erdif-org.github.io/erdif-spec/ns/v1/erdif.ttl`, for tools that
work with RDF schemas (Dataspecer, Protégé, SHACL validators). It is
generated from the term registry, so it never diverges from the context
and the JSON Schemas. It declares the `erdif:` classes and properties,
the codelists as SKOS concept schemes with their values, and the reused
schema.org terms with `schema:domainIncludes` / `schema:rangeIncludes`,
which never narrow their meaning. Every property has exactly one domain;
a property shared by several classes (for example `name`) is declared on
the schema.org class they have in common and reached through
`rdfs:subClassOf`.

Namespace IRIs contain only the major version (`v1`). Backward-compatible
changes keep the IRIs; a breaking change introduces `v2`. See
[Versioning](versioning.md).

## Codelist values

A codelist property is written with a short code, but expands to a full IRI
thanks to a scoped context:

```json
"transactionType": "Sale"
```

expands to

```text
https://erdif-org.github.io/erdif-spec/codelist/v1/TransactionType#Sale
```

Developers work with readable codes, while linked-data consumers get an
unambiguous identifier of the value.

## Multiple typing rule

Every entity carries **two types** at once:

- a **schema.org type**, which makes the data understandable to search
  engines, AI agents and any generic schema.org consumer,
- an **`erdif:` type**, which carries the domain semantics of ERDIF and is
  what ERDIF validation relies on.

```json
"@type": ["RealEstateListing", "erdif:Advert"]
"@type": ["PriceSpecification", "erdif:Price"]
"@type": ["Room", "erdif:Room"]
```

Where schema.org offers a more specific subtype (`Apartment` instead of
`Accommodation`, `ImageObject` instead of `MediaObject`), producers should
use it. Entities without a suitable schema.org counterpart (for example
`erdif:Building`, `erdif:Parking`) carry only the `erdif:` type.
