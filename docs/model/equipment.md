# Equipment

## Description

`Equipment` is an item of furnishing or equipment. It is bound to a
specific [room](room.md) rather than to the property as a whole, so the
information *where* the item is located is preserved (a dishwasher in the
kitchen, a washing machine in the bathroom).

The category comes from the `EquipmentType` codelist; the optional `name`
is a language map with a human-readable label.

## Properties

--8<-- "_partials/terms-equipment.md"

## Validation rules

--8<-- "_partials/rules-equipment.md"

## Example

```json
"equipment": [
  {
    "@type": "erdif:Equipment",
    "equipmentType": "Appliance",
    "name": { "cs": "Lednice", "en": "Refrigerator" }
  }
]
```
