# Price

## Description

A `Price` is a single price item of an offer. An advert carries **one or
more** price items, each with its own type, amount, currency and — for
periodic payments — unit. This lets an offer state, for example, the rent
together with service charges, a deposit and the price of a parking space,
without a dedicated property for each of them.

The currency is an [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) code
and the unit a [UN/CEFACT](https://en.wikipedia.org/wiki/UN/CEFACT)
Recommendation 20 code (`MON` per month, `ANN` per year, `MTK` per m²).

When the seller does not publish the amount, `price` is omitted and
`priceOnRequest` is set to `true`.

The entity is typed as `schema:PriceSpecification` and `erdif:Price`.

## Properties

--8<-- "_partials/terms-price.md"

## Validation rules

--8<-- "_partials/rules-price.md"

## Example

```json
"prices": [
  {
    "@type": ["PriceSpecification", "erdif:Price"],
    "priceType": "Purchase",
    "price": 8950000,
    "priceCurrency": "CZK",
    "negotiable": true
  },
  {
    "@type": ["PriceSpecification", "erdif:Price"],
    "priceType": "ServiceCharges",
    "price": 3400,
    "priceCurrency": "CZK",
    "unitCode": "MON"
  }
]
```

A price available on request only:

```json
{
  "@type": ["PriceSpecification", "erdif:Price"],
  "priceType": "Purchase",
  "priceOnRequest": true,
  "priceCurrency": "EUR"
}
```
