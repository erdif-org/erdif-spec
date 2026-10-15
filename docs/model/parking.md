# Parking

## Description

`Parking` describes a parking option that belongs to the property — an
outdoor space, a covered space, a space in a shared garage or a private
garage — with the number of spaces and whether it is included in the price.

Parking is not modelled as a [room](room.md): it does not count towards the
layout or usable area of the unit, and a space in a shared garage is not
part of the unit at all.

When parking is paid separately (`includedInPrice: false`), its price is
given as a regular [price item](price.md) with `priceType` `Parking`. A
garage or parking space offered on its own uses `realtyType` `Parking` and
is described by the same entity.

## Properties

--8<-- "_partials/terms-parking.md"

## Validation rules

--8<-- "_partials/rules-parking.md"

## Example

```json
"parking": [
  {
    "@type": "erdif:Parking",
    "parkingType": "GarageSpace",
    "count": 1,
    "includedInPrice": false
  }
]
```
