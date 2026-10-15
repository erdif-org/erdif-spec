# LocalArea

## Description

`LocalArea` describes one amenity in the surroundings of the property — a
public transport stop, a school, a kindergarten, a park, a shop and so on —
optionally with its name and distance from the property.

The surroundings are attached to [`Realty`](realty.md), not to
[`Location`](location.md). The location identifies *where* the property is;
the surroundings describe *what is nearby*, which is descriptive
information used for presentation and search, not for spatial
identification.

schema.org has no property for nearby places, so the link is
`erdif:localArea`. For the amenity itself, however, schema.org offers
specific types (`BusStop`, `SubwayStation`, `Preschool`, `School`, `Park`,
`Hospital`, ...), and producers are encouraged to use them next to `Place`.

## Properties

--8<-- "_partials/terms-local-area.md"

## Validation rules

--8<-- "_partials/rules-local-area.md"

## Example

```json
"localArea": [
  {
    "@type": ["SubwayStation", "erdif:LocalArea"],
    "amenityType": "MetroStation",
    "name": { "cs": "Náměstí Míru" },
    "distance": { "@type": "QuantitativeValue", "value": 350, "unitCode": "MTR" }
  },
  {
    "@type": ["Preschool", "erdif:LocalArea"],
    "amenityType": "Kindergarten",
    "distance": { "@type": "QuantitativeValue", "value": 200, "unitCode": "MTR" }
  }
]
```
