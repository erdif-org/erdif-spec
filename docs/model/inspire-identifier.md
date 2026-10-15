# InspireIdentifier

## Description

`InspireIdentifier` references a spatial object published under the EU
INSPIRE directive. INSPIRE data are available in every member state with
the same structure, so this identifier is the primary supranational way to
locate a property: it resolves to the exact spatial object (address point,
building or cadastral parcel) and, through it, to the national address.

The identifier follows the INSPIRE structure: a theme, the namespace of the
data provider and a local identifier within that namespace. Supported
themes:

| Theme | Spatial object   |
|-------|------------------|
| `AD`  | Address point    |
| `BU`  | Building         |
| `CP`  | Cadastral parcel |

## Properties

--8<-- "_partials/terms-inspire-identifier.md"

## Validation rules

--8<-- "_partials/rules-inspire-identifier.md"

## Example

```json
"globalIdentifier": {
  "@type": "erdif:InspireIdentifier",
  "theme": "AD",
  "namespace": "CZ.CUZK.AD",
  "localId": "26777598"
}
```
