# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/),
versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

First public version of the specification.

### Added
- Data model of 15 classes: the root `Advert` with `Price`, `Contact`,
  `Media` and `ExportInformation`; `Realty` with `Building`, `Room`,
  `Equipment`, `UtilityNetwork`, `Parking` and `LocalArea`; `Location` with
  `InspireIdentifier` and `LocalIdentifier`
- Three-level geolocation: INSPIRE identifier, mandatory WGS 84 coordinates
  with an explicit `approximateCoordinates` flag, and national identifiers
  with a postal address
- Namespaces `erdif:` (`https://erdif-org.github.io/erdif-spec/ns/v1#`)
  and `erdif-cl:` (`https://erdif-org.github.io/erdif-spec/codelist/v1/`)
- JSON-LD 1.1 context `schema/context.jsonld` declaring every term
  explicitly, with XSD datatype coercions, codelist values expanding to
  `erdif-cl:` IRIs, and `@protected`
- Term registry `schema/terms/` with the properties, ranges, cardinalities
  and cross-property validation rules of every class
- JSON Schema (draft 2020-12) for every class in `schema/`
- RDFS/OWL vocabulary `docs/ns/v1/erdif.ttl` (Turtle) generated from the
  term registry and the codelists, for linked-data tooling such as Dataspecer
- 16 codelists, all open until 1.0: `TransactionType`, `RealtyType`,
  `OwnershipType`, `EnergyClass`, `RealtyCondition`, `ConstructionType`,
  `RoomType`, `EquipmentType`, `AccessibilityFeature`, `UtilityNetwork`,
  `UtilityConnection`, `ParkingType`, `PriceType`, `ContactType`,
  `MediaType`, `AmenityType`; `appliesTo` restricts where a value may be used
- Human-readable text as language maps
- Documentation: data model, namespaces, codelists, localization,
  geolocation, versioning and conformance
- Example documents: an apartment for sale and a house for rent, and four
  invalid documents, each breaking exactly one rule
