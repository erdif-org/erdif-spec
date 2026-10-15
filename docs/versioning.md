# Versioning

ERDIF distinguishes two things that both carry a version: the
**specification** and the **documents** created according to it.

## Specification version

The specification follows [Semantic Versioning](https://semver.org/):

| Change | Version bump | Examples |
|--------|--------------|----------|
| Breaking | major (`2.0.0`) | removing or renaming a property, changing a cardinality from optional to required, removing a codelist value |
| Backward compatible | minor (`1.1.0`) | adding an optional property, a class or a codelist value |
| Editorial | patch (`1.0.1`) | clarifying documentation, fixing typos |

Every release is a git tag (`v1.0.0`, `v1.0.0-beta.1`). The documentation
site keeps each major version side by side (`v1`, `v2`) together with the
`dev` version built from the main branch; use the version switcher in the
header to change between them. All changes are listed in the
[Changelog](changelog.md).

Pre-release versions (`1.0.0-beta.1`) may change in any way before the
final release.

## Namespaces

Namespace IRIs contain **only the major version**:

```text
https://erdif-org.github.io/erdif-spec/ns/v1#
https://erdif-org.github.io/erdif-spec/codelist/v1/
```

Minor and patch releases only add terms, so the IRIs stay the same and
existing data keep their meaning. A major release introduces new IRIs
(`/ns/v2#`), so data created against different major versions never mix
silently.

## Document version

Every document states the specification version it was created against in
`formatVersion` on the root `Advert`:

```json
"formatVersion": "1.0.0-beta.1"
```

The value is the full specification version, including any pre-release
label.

A consumer:

- **must** reject a document whose major version it does not support,
- **should** accept a document with a newer minor or patch version of a
  supported major version and ignore properties it does not know,
- **may** use the full version for diagnostics and statistics.
