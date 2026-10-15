# ERDIF

**European Real Estate Data Interchange Format** — an open data format for
exchanging real estate listings between systems across Europe.

!!! warning "Beta"
    This specification is a beta. The data model may still change before
    version 1.0; see [Versioning](versioning.md).

## Purpose

Real estate portals, agency software and aggregators exchange listings in
proprietary, country-specific formats. Every integration means a new
mapping, and concepts that differ between countries — layout notation,
national address registries, local price conventions — are hard to compare.

ERDIF defines one vocabulary and one serialization for a listing that:

- has a **common international core** (property type, transaction type,
  price with currency, area in m², coordinates) understandable in any
  country,
- identifies the location through **European INSPIRE identifiers** with
  WGS 84 coordinates as a mandatory fallback,
- carries human-readable text in **any number of languages**,
- gives every attribute a **machine-readable meaning** through links to
  public vocabularies,
- separates **personal data** of the contact so it can be removed
  independently,
- is independent of the transport interface — it describes the document,
  not the API that carries it.

It is intended for developers of systems that export or import listings:
portals, agency CRMs, aggregators and search engines.

## Core principles

- Serialized as **JSON-LD 1.1**, so a document is plain JSON for developers
  and linked data for machines
- **schema.org** as the default vocabulary (`@vocab`)
- Custom **`erdif:`** namespace for European specifics
- Entities carry **multiple types** (e.g. `RealEstateListing` + `erdif:Advert`)
- Codelist values are dereferenceable IRIs in the **`erdif-cl:`** namespace
- Human-readable text is stored as **language maps**

## Where to start

- [Data model](model/advert.md) — the entities and their properties,
  starting from the root `Advert`
- [Examples](examples.md) — a complete document
- [Conformance](conformance.md) — what makes a document valid
- [Codelists](codelists.md) — allowed values

## Version

Current version: **1.0.0-beta.1** (development version `dev`)

## License

TODO
