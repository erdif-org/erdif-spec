# Geolocation

ERDIF identifies the location of a property through a three-level
hierarchy. Each level has a different role; together they guarantee that a
property can always be shown on a map and, where possible, linked to
authoritative spatial data. All levels live in [`Location`](model/location.md).

## 1. INSPIRE identifier

The primary, supranational reference. The EU INSPIRE directive obliges
member states to publish spatial data with a common structure, so an
INSPIRE identifier works the same way in every country. It resolves to the
spatial object itself — including its geometry — and through it to the
national address.

ERDIF uses three INSPIRE themes:

| Theme | Spatial object   | Typical use                    |
|-------|------------------|--------------------------------|
| `AD`  | Address point    | Apartments, houses             |
| `BU`  | Building         | Whole buildings                |
| `CP`  | Cadastral parcel | Land, properties without address |

```json
"globalIdentifier": {
  "@type": "erdif:InspireIdentifier",
  "theme": "AD",
  "namespace": "CZ.CUZK.AD",
  "localId": "26777598"
}
```

The identifier is optional, because it may not exist yet — typically for
new buildings that are not registered.

## 2. GPS coordinates (WGS 84)

A **mandatory** fallback that must always be present, given in
[WGS 84](https://en.wikipedia.org/wiki/World_Geodetic_System). It guarantees
that every property can at least be shown as a point on a map, even when no
INSPIRE identifier is available.

```json
"geo": {
  "@type": "GeoCoordinates",
  "latitude": 50.07553,
  "longitude": 14.43781
},
"approximateCoordinates": false
```

Many advertisers deliberately shift the point to hide the exact address.
`approximateCoordinates` states whether that is the case, and must always
be given explicitly:

- `false` — the point marks the property; it can be used for precise map
  display and distance calculations,
- `true` — the point is only approximate; consumers should show an area
  rather than a pin.

## 3. National identifiers

Supplementary metadata: identifiers from national registries (for example
RÚIAN in the Czech Republic) and the postal address in the local format.
They have no system role at the European level — ERDIF does not use them
to locate the property — but they are passed through unchanged so that the
end user or a local system can verify the property in the national registry.

```json
"localIdentifiers": [
  {
    "@type": "erdif:LocalIdentifier",
    "registry": "RUIAN",
    "registryCountry": "CZ",
    "registryLevel": "Address",
    "identifier": "22349811"
  }
],
"address": {
  "@type": "PostalAddress",
  "streetAddress": "Korunní 810/104",
  "addressLocality": "Praha",
  "postalCode": "10100",
  "addressCountry": "CZ"
}
```
