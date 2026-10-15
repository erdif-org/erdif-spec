# Contact

## Description

`Contact` describes the party managing the offer — an agent, a real estate
office or the owner advertising directly.

The entity is typed as `erdif:Contact` together with a schema.org type.
Producers use `schema:Person` or `schema:Organization`, or any of their
subtypes (for example `RealEstateAgent`).

## Separation of personal data

A contact usually carries personal data of a natural person (name, e-mail,
phone number). Under the GDPR such data must be removable or anonymisable
independently of the rest of the offer.

ERDIF therefore keeps the contact in a **separate entity** with no property
data mixed in. A receiving system can:

- store the contact apart from the property and the advert,
- delete or anonymise it on request without touching the offer itself,
- keep publishing the offer with a replacement contact (e.g. the office).

## Properties

--8<-- "_partials/terms-contact.md"

## Validation rules

--8<-- "_partials/rules-contact.md"

## Example

```json
"contact": {
  "@type": ["RealEstateAgent", "erdif:Contact"],
  "contactType": "Agent",
  "name": { "cs": "Jan Novák", "en": "Jan Novák" },
  "email": "jan.novak@example.com",
  "telephone": "+420123456789"
}
```
