# ExportInformation

## Description

`ExportInformation` is the audit trail of the export: which system produced
the data, under which identifier the advert is known there, and when the
export happened.

It lets a receiving system match records on repeated imports — the pair
`sourceSystem` + `sourceAdvertId` identifies the same advert across
exports — and decide, using `exportedAt`, whether an incoming document is
newer than the stored one.

## Properties

--8<-- "_partials/terms-export-information.md"

## Validation rules

--8<-- "_partials/rules-export-information.md"

## Example

```json
"exportInformation": {
  "@type": "erdif:ExportInformation",
  "sourceSystem": "RealiSoft",
  "sourceAdvertId": "EXT-12345",
  "exportedAt": "2026-09-09T16:30:00Z"
}
```
