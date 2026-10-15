# Room

## Description

`Room` describes one room of the property. The list of rooms replaces
country-specific layout notations (such as the Czech "2+kk"): a consumer
can derive the layout and the total usable area from the room types and
sizes in any local convention.

Rooms are optional (`0..*`): every building has at least one room, land
parcels have none. Parking spaces are not rooms — they are described by
[`Parking`](parking.md), because they do not count towards the layout or
usable area.

Accessibility features that concern a specific room (walk-in shower, grab
bars, turning space for a wheelchair) are stated on the room; features of
the property as a whole are stated on [`Realty`](realty.md).

The entity is typed as `schema:Room` and `erdif:Room`.

## Properties

--8<-- "_partials/terms-room.md"

## Validation rules

--8<-- "_partials/rules-room.md"

## Example

```json
{
  "@type": ["Room", "erdif:Room"],
  "roomType": "Bathroom",
  "floorSize": { "@type": "QuantitativeValue", "value": 6.2, "unitCode": "MTK" },
  "floorLevel": 3,
  "accessibility": ["WalkInShower", "GrabBars"]
}
```
