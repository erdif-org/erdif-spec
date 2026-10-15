# Examples

Complete example documents are in the
[`examples/`](https://github.com/erdif-org/erdif-spec/tree/main/examples) directory.

## Valid documents

### Apartment for sale (Prague)

A two-room apartment in a renovated brick building. It shows most of the
model: several price items including a separately paid parking space,
the full geolocation hierarchy, rooms with equipment, utility connections,
the building, parking, surroundings and media.

```json
--8<-- "examples/valid/apartment-sale.jsonld"
```

### House for rent (Brno)

A newly built family house with a garden. It covers what the apartment
does not: rent with monthly service charges and a deposit, a commission
available on request only, a contact reachable by phone only, approximate
coordinates without an INSPIRE identifier, both floor and plot area, and
accessibility features on both the property and a room.

```json
--8<-- "examples/valid/house-rent.jsonld"
```

## Invalid documents

Each invalid example breaks exactly one rule. `_comment` explains which one,
and `_expect` states the error a JSON Schema validator reports — the JSON
Pointer of the failing value and the failing keyword. They are meant as test
cases for importers.

| Example | Broken rule | Expected error |
|---------|-------------|----------------|
| [`missing-gps-fallback.jsonld`](https://github.com/erdif-org/erdif-spec/blob/main/examples/invalid/missing-gps-fallback.jsonld) | `geo` is required on `Location` | `/realty/location` — `required` |
| [`price-without-amount.jsonld`](https://github.com/erdif-org/erdif-spec/blob/main/examples/invalid/price-without-amount.jsonld) | `price-or-on-request` | `/prices/0` — `anyOf` |
| [`room-feature-on-realty.jsonld`](https://github.com/erdif-org/erdif-spec/blob/main/examples/invalid/room-feature-on-realty.jsonld) | `accessibility-level` | `/realty/accessibility/0` — `not` |
| [`land-with-rooms.jsonld`](https://github.com/erdif-org/erdif-spec/blob/main/examples/invalid/land-with-rooms.jsonld) | `land-has-no-rooms` | `/realty/rooms` — `maxItems` |

All examples are checked in CI by `scripts/validate_examples.py`: valid
documents must pass the schema and expand as JSON-LD, invalid ones must fail
with exactly the expected error and no other.
