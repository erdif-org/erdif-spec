# LocalIdentifier

## Description

`LocalIdentifier` carries an identifier from a national registry, such as
the Czech RÚIAN. National identifiers play no role in locating the property
at the European level; they are passed through unchanged so that the end
user or a local system can verify the property in the national registry.

A location may carry several local identifiers, for example one for the
address and one for the building.

## Properties

--8<-- "_partials/terms-local-identifier.md"

## Validation rules

--8<-- "_partials/rules-local-identifier.md"

## Example

```json
"localIdentifiers": [
  {
    "@type": "erdif:LocalIdentifier",
    "registry": "RUIAN",
    "registryCountry": "CZ",
    "registryLevel": "Address",
    "identifier": "22349811"
  }
]
```
