# Realty

## Description

`Realty` describes the physical property independently of how it is
currently being offered. It holds the internationally comparable core —
type of property and area — together with ownership, energy class,
condition and the links to its location, building, rooms, utilities,
parking and surroundings.

The area follows the type of property: buildings and units state
`floorSize`, land parcels state `plotSize`. Either way the area is given in
square metres (`MTK`), which satisfies the mandatory core of the format.

Attributes of the whole building (construction, year built, elevator) are
not stored here but in [`Building`](building.md), because all units of a
building share them. Accessibility is split by level: features of the
property as a whole (entrance, access to the unit) are stated here,
features of a specific room (bathroom, turning space) on the
[room](room.md).

The entity is typed as `erdif:Realty` together with `schema:Accommodation`
or one of its subtypes (for example `Apartment`, `House`). Land parcels are
not accommodation and use `schema:Place` instead.

## Properties

--8<-- "_partials/terms-realty.md"

## Validation rules

--8<-- "_partials/rules-realty.md"

## Example

```json
"realty": {
  "@type": ["Apartment", "erdif:Realty"],
  "realtyType": "Apartment",
  "ownershipType": "Personal",
  "energyClass": "C",
  "condition": "AfterRenovation",
  "floorSize": { "@type": "QuantitativeValue", "value": 58.4, "unitCode": "MTK" },
  "floorLevel": 3,
  "accessibility": ["ElevatorAccess"],
  "building": { ... },
  "location": { ... },
  "rooms": [ ... ],
  "utilityNetworks": [ ... ],
  "parking": [ ... ],
  "localArea": [ ... ]
}
```

A land parcel has no rooms and no building:

```json
"realty": {
  "@type": ["Place", "erdif:Realty"],
  "realtyType": "Land",
  "plotSize": { "@type": "QuantitativeValue", "value": 1250, "unitCode": "MTK" },
  "location": { ... }
}
```
