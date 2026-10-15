# Localization

## Language maps

Text intended for people is written as a key–value map whose keys are
**[ISO 639-1](https://en.wikipedia.org/wiki/ISO_639-1)** language codes. In
the context these properties are declared with `@container: "@language"`.

```json
"description": {
  "cs": "Prostorný byt 2+kk v cihlovém domě po rekonstrukci.",
  "en": "Spacious two-room apartment in a renovated brick building."
}
```

## Codelist values

Codelist values are **not translated**. The English PascalCase identifier
is always transmitted; translating it into the user's language is the
client's responsibility. The labels in each codelist are language maps
as well, so clients can look up a translation there.
