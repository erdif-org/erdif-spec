# ERDIF — European Real Estate Data Interchange Format

Specification of an open data format for exchanging real estate listings
across Europe. Based on JSON-LD, the schema.org vocabulary and a custom
`erdif:` namespace for European specifics.

Documentation: <https://erdif-org.github.io/erdif-spec/>

## Repository layout

| Path          | Contents                                                        |
|---------------|-----------------------------------------------------------------|
| `schema/`     | Term registry, JSON-LD context and JSON Schema                  |
| `codelists/`  | Domain codelists in JSON                                        |
| `examples/`   | Example documents (valid and invalid)                           |
| `docs/`       | Documentation site sources (MkDocs Material)                    |
| `scripts/`    | Documentation generators and the MkDocs build hook              |

## Source vs. generated files

Only the sources are edited and committed. Generated files are listed in
`.gitignore` and rebuilt on every docs build.

| Source (edit these)             | Generated (never edit, not committed)        | Generator                          |
|---------------------------------|----------------------------------------------|------------------------------------|
| `codelists/*.json`              | `docs/codelists/*.md`                        | `scripts/build_codelist_docs.py`   |
| `schema/terms/*.json`            | `docs/_partials/*.md`, `docs/vocabulary.md`  | `scripts/build_term_docs.py`       |
| `schema/terms/*.json`, `codelists/*.json` | `schema/<class>.schema.json` (**committed**) | `scripts/build_schemas.py` |
| `docs/**/*.md` (all other pages)| `site/`                                      | `mkdocs build`                     |

Hand-written model pages embed the generated property table and validation
rules with `--8<-- "_partials/terms-<class>.md"` and
`--8<-- "_partials/rules-<class>.md"`. Rules that cardinality cannot express
are defined in the `rules` array of a class in `schema/terms/<class>.json`.

### JSON Schema

The class schemas are generated, but committed, because they are published
artifacts. After changing `schema/terms/` or `codelists/`, run
`python scripts/build_schemas.py`; CI fails when the committed schemas are
out of date. Constraints the term registry cannot express are stored next to
the term as a `jsonSchema` fragment (on a property or a rule), or as
`appliesTo` on a rule that is enforced through a codelist's `appliesTo`.
`schema/common.schema.json` (language maps and the reused schema.org types)
is hand-written.

`python scripts/validate_examples.py` validates `examples/` against the
schemas and runs in CI — see [`examples/README.md`](examples/README.md).

### JSON-LD context

`schema/context.jsonld` is maintained by hand and must be kept in sync with
`schema/terms/`. `scripts/check_context.py` enforces that — it fails when a
term is missing, expands to a different IRI or lacks a datatype coercion —
and runs in CI before the docs build.

### Languages

The documentation is written in English. Human-readable text in the JSON
sources is stored as language maps (`{"en": "...", "cs": "..."}`) so that
further European languages can be added just by adding keys; codelist pages
show a column for every language present in the data.

## Building the documentation locally

```bash
pip install -r requirements.txt
mkdocs serve
```

The hook `scripts/mkdocs_hooks.py` runs both generators before every build,
and `mkdocs serve` rebuilds when `codelists/` or `schema/` change. The
generators can also be run on their own:

```bash
python scripts/build_codelist_docs.py
python scripts/build_term_docs.py
```

## License

TODO
