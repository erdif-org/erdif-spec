# Building

## Description

`Building` describes the building a property belongs to. An apartment is
one of many units in a building, and attributes such as the construction
type, the year of completion or the presence of an elevator are shared by
all of them. Keeping them in a separate entity avoids mixing building-level
facts with the description of the unit.

For a house the building and the property are the same object; the
building attributes are still written into `building`, so consumers find
them in one place regardless of the property type. Land parcels have no
building.

The year of completion reuses `schema:yearBuilt`. schema.org has no
properties for the other attributes, so they are defined in `erdif:`.

## Properties

--8<-- "_partials/terms-building.md"

## Validation rules

--8<-- "_partials/rules-building.md"

## Example

```json
"building": {
  "@type": "erdif:Building",
  "constructionType": "Brick",
  "yearBuilt": 1912,
  "lastRenovationYear": 2019,
  "floorsAboveGround": 5,
  "floorsUnderground": 1,
  "elevator": true
}
```
