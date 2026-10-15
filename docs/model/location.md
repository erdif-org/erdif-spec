# Location

## Description

`Location` identifies where the property is. It combines three independent
means of identification, described in detail in
[Geolocation](../geolocation.md):

1. an INSPIRE identifier ([`InspireIdentifier`](inspire-identifier.md)) as
   the primary supranational reference,
2. WGS 84 coordinates as a **mandatory** fallback, because an INSPIRE
   identifier may not exist yet (e.g. for new buildings),
3. national identifiers ([`LocalIdentifier`](local-identifier.md)) and a
   postal address as supplementary information.

Coordinates are often deliberately shifted to protect the exact address.
The `approximateCoordinates` flag makes this explicit, so a consumer knows
whether the point can be used for precise map display.

Information about the surroundings is **not** part of the location; it is
modelled separately as [`LocalArea`](local-area.md).

The entity is typed as `schema:Place` and `erdif:Location`.

## Properties

--8<-- "_partials/terms-location.md"

## Validation rules

--8<-- "_partials/rules-location.md"

## Example

```json
"location": {
  "@type": ["Place", "erdif:Location"],
  "globalIdentifier": {
    "@type": "erdif:InspireIdentifier",
    "theme": "AD",
    "namespace": "CZ.CUZK.AD",
    "localId": "26777598"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 50.07553, "longitude": 14.43781 },
  "approximateCoordinates": false,
  "localIdentifiers": [ ... ],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Korunní 810/104",
    "addressLocality": "Praha",
    "postalCode": "10100",
    "addressCountry": "CZ"
  }
}
```
