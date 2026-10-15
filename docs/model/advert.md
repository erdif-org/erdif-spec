# Advert

## Description

`Advert` is the root entity of every ERDIF document and represents one offer
of a property on the market. It carries the commercial part of the offer —
transaction type, prices, marketing text, media and the contact — while the
physical property is described separately in [`Realty`](realty.md).

This split reflects the fact that one property can be offered repeatedly and
in different ways over time (sold, later rented out), whereas its physical
description stays the same.

The marketing text (`description`) belongs to the advert, not to the
property: it is written for one specific offer and changes with the
transaction type.

The entity is typed as `schema:RealEstateListing`, which makes the document
understandable to search engines and generic schema.org consumers, and as
`erdif:Advert`, which carries the ERDIF semantics.

## Properties

--8<-- "_partials/terms-advert.md"

## Validation rules

--8<-- "_partials/rules-advert.md"

## Example

```json
{
  "@context": "https://erdif-org.github.io/erdif-spec/ns/v1/context.jsonld",
  "@type": ["RealEstateListing", "erdif:Advert"],
  "formatVersion": "1.0.0-beta.1",
  "identifier": "ADV-2026-009874",
  "datePosted": "2026-09-09T16:30:00Z",
  "transactionType": "Sale",
  "description": {
    "cs": "Prostorný byt 2+kk v cihlovém domě po rekonstrukci.",
    "en": "Spacious two-room apartment in a renovated brick building."
  },
  "prices": [ ... ],
  "contact": { ... },
  "realty": { ... },
  "media": [ ... ],
  "exportInformation": { ... }
}
```
