"""
MkDocs hook: regenerate the documentation and the RDFS/OWL vocabulary
from codelists/*.json and schema/terms/*.json before every build.

This way `mkdocs serve` / `mkdocs build` is all that is needed; the
generators do not have to be run by hand. Changes to the JSON sources
are picked up through `watch` in mkdocs.yml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_codelist_docs  # noqa: E402
import build_term_docs  # noqa: E402
import build_vocabulary  # noqa: E402


def on_config(config):
    if build_codelist_docs.main() or build_term_docs.main() or build_vocabulary.main():
        raise SystemExit("Documentation generation failed")
    return config
