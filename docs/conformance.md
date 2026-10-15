# Conformance

The key words **MUST**, **MUST NOT**, **SHOULD** and **MAY** are to be
interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when they appear in
bold.

## Conforming document

A document conforms to ERDIF v1 when all of the following hold:

1. It is valid JSON encoded in UTF-8.
2. Its `@context` is the ERDIF context
   (`https://erdif-org.github.io/erdif-spec/ns/v1/context.jsonld`), and it is
   valid JSON-LD 1.1.
3. Its root is an `Advert` whose `formatVersion` is a v1 version of this
   specification (see [Versioning](versioning.md)).
4. Every entity carries the `erdif:` type of its class, as described in
   the [multiple typing rule](namespaces.md#multiple-typing-rule).
5. Every property satisfies the range and cardinality given in its class's
   property table.
6. Every entity satisfies the validation rules of its class.
7. Every codelist value is either listed in the codelist, or the codelist is
   open (see [Codelists](codelists.md)).
8. Values follow the referenced standards:
   language map keys are [ISO 639-1](https://en.wikipedia.org/wiki/ISO_639-1)
   codes, currencies are [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217)
   codes, units are [UN/CEFACT](https://en.wikipedia.org/wiki/UN/CEFACT)
   Recommendation 20 codes, coordinates are
   [WGS 84](https://en.wikipedia.org/wiki/World_Geodetic_System), country
   codes are [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
   and date-times are [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)
   with a time zone.

The examples in
[`examples/valid/`](https://github.com/erdif-org/erdif-spec/tree/main/examples/valid)
conform; each document in
[`examples/invalid/`](https://github.com/erdif-org/erdif-spec/tree/main/examples/invalid)
breaks exactly one of the rules above and explains which one in its
`_comment`.

## Validation with JSON Schema

The JSON Schemas in
[`schema/`](https://github.com/erdif-org/erdif-spec/tree/main/schema) check
a document in its compact form, starting from `advert.schema.json`. They
cover conditions 3–8 above, except for:

- the validation rules `renovation-after-construction` (JSON Schema cannot
  compare two values) and `parking-price` (a recommendation spanning two
  entities),
- the informative rules `advert-id-vs-source-id` and `amenity-schema-type`,
  which state no constraint,
- the codes of condition 8 (currency, unit, country, language), which are
  checked by their shape only, not against the official code lists.

Condition 2 — valid JSON-LD 1.1 — needs a JSON-LD processor. Validators
must enable `format` assertion (e-mail, URI and date-time checks); the
time zone of date-times is enforced by a pattern either way.

The schemas accept properties they do not know, so a document of a newer
minor version stays valid against an older schema (see
[Versioning](versioning.md)).

## Producers

A system that exports ERDIF documents:

- **MUST** produce conforming documents,
- **MUST** state `approximateCoordinates` truthfully,
- **SHOULD** use the most specific schema.org type available,
- **SHOULD** provide `description` in the language of the market and in
  English,
- **SHOULD** use a listed codelist value whenever one fits, and a custom code
  only when none does,
- **MUST NOT** put personal data anywhere other than in `Contact`.

## Consumers

A system that imports ERDIF documents:

- **MUST** reject documents whose major version it does not support,
- **MUST** accept unknown codes in open codelists,
- **SHOULD** ignore properties it does not know instead of rejecting the
  document,
- **SHOULD** use `exportInformation` (`sourceSystem` + `sourceAdvertId`) to
  match repeated imports of the same advert,
- **SHOULD** preserve `localIdentifiers` unchanged when passing data on,
- **MUST** be able to delete or anonymise a `Contact` independently of the
  rest of the advert.
