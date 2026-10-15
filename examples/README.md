# Examples

- `valid/` — documents that conform to the specification
- `invalid/` — documents that break exactly one rule; each file contains
  a `_comment` explaining which rule it breaks and why, and an `_expect`
  with the error a JSON Schema validator must report:

  ```json
  "_expect": { "path": "/realty/location", "keyword": "required" }
  ```

  `path` is the JSON Pointer of the failing value, `keyword` the failing
  JSON Schema keyword.

`python scripts/validate_examples.py` checks both directories and runs in CI:
valid documents must pass the schema and expand as JSON-LD, invalid ones must
fail with exactly the expected error and no other.
