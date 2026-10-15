# Codelists

The source of truth is the
[`codelists/`](https://github.com/erdif-org/erdif-spec/tree/main/codelists)
directory. The codelist pages are generated from it on every docs build.

## Rules

- Value identifiers are English, in **PascalCase**
- Values are **not translated** — labels only serve as documentation
- Labels and descriptions are language maps; a column is shown for every
  language present in the data
- `appliesTo` on a value restricts where it may be used — the level
  (`Realty`, `Room`) for accessibility features, or the network for utility
  connections
- During JSON-LD expansion a value resolves to the IRI
  `https://erdif-org.github.io/erdif-spec/codelist/v1/<Codelist>#<Code>`

## Open and closed codelists

- **Closed** (`closed: true`) — the list is exhaustive; the producer must use
  one of the listed values and validation may reject unknown values.
- **Open** (`closed: false`) — the list is representative; the producer may use
  its own code and validation must accept it.

!!! warning "Development version"
    Until version 1.0 all codelists are open. Which codelists become closed
    will be decided before the release.

## List of codelists

| Codelist | Used by |
|----------|---------|
| [TransactionType](codelists/transaction-type.md) | `Advert.transactionType` |
| [RealtyType](codelists/realty-type.md) | `Realty.realtyType` |
| [OwnershipType](codelists/ownership-type.md) | `Realty.ownershipType` |
| [EnergyClass](codelists/energy-class.md) | `Realty.energyClass` |
| [RoomType](codelists/room-type.md) | `Room.roomType` |
| [EquipmentType](codelists/equipment-type.md) | `Equipment.equipmentType` |
| [UtilityNetwork](codelists/utility-network.md) | `UtilityNetwork.network` |
| [UtilityConnection](codelists/utility-connection.md) | `UtilityNetwork.connection` |
| [PriceType](codelists/price-type.md) | `Price.priceType` |
| [ContactType](codelists/contact-type.md) | `Contact.contactType` |
| [MediaType](codelists/media-type.md) | `Media.mediaType` |
| [AmenityType](codelists/amenity-type.md) | `LocalArea.amenityType` |
| [RealtyCondition](codelists/realty-condition.md) | `Realty.condition` |
| [ConstructionType](codelists/construction-type.md) | `Building.constructionType` |
| [ParkingType](codelists/parking-type.md) | `Parking.parkingType` |
| [AccessibilityFeature](codelists/accessibility-feature.md) | `Realty.accessibility`, `Room.accessibility` |
