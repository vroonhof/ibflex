# Contributing to ibflex2

Thanks for sending a fix or feature. The maintained fork's job is to keep
parsing IBKR Flex Query reports correctly even as IBKR adds new fields and
sections faster than upstream releases.

## Local development

```sh
# With Nix (preferred — matches CI)
nix develop
pytest --cov=ibflex --cov-fail-under=95 tests/
mypy ibflex tests
ruff check ibflex tests

# Without Nix
pip install -e .[web,dev]
pytest tests/
mypy ibflex tests
ruff check ibflex tests
```

The `make test` target chains `mypy + ruff + pytest`.

## Adding a new field to an existing dataclass

When IBKR adds an attribute to a Flex section, the type definition needs to
catch up. Checklist for a "new field" PR:

1. **Add the field** to the relevant dataclass in `ibflex/Types.py`. Keep the
   field grouped with related ones — don't blindly append at the end. Use
   `Optional[T] = None` so existing data without the attribute still parses.
2. **Add a test** in `tests/test_types.py` using a real (anonymized) XML
   snippet from your Flex report. Reuse one of the existing `*TestCase`
   patterns; the test only needs to assert the new attribute parses.
3. **Update `CHANGELOG.md`** under the `Unreleased` → `Added` section.
4. **If the type changed** (e.g. `Optional[Decimal]` -> `Optional[bool]`), add
   an entry under `Unreleased` → `Breaking changes` and explain what
   downstream code might silently misbehave.

## Adding a new dataclass for a new section

1. Add the class to `ibflex/Types.py` with `@dataclass(frozen=True)` and a
   one-line docstring noting which container element wraps it.
2. Add the class name to the module's `__all__` list (alphabetical).
3. Wire it into `FlexStatement` (replace the `Tuple = ()  # TODO` placeholder
   with the typed tuple).
4. Add a `*TestCase` in `tests/test_types.py` using real anonymized XML.
5. Update `CHANGELOG.md`.

## Adding enum values

`ibflex/enums.py` mirrors the IBKR-supplied codes. New values get added
alphabetically (or by code-letter ordering where that's the existing
convention). Add a quick parser test in `tests/test_parser.py` →
`testConvertEnum` for the new value, or a full round-trip test in
`tests/test_types.py` if the value gates parsing of a whole element.

## Anonymizing XML test data

Real Flex reports contain account numbers, names, addresses, and trade
history. Before pasting into a test:

- Account IDs → `U123456` / `U1234567`
- Account aliases → `""` or `"test"`
- Personal names → `"Test User"` etc.
- ConIDs and securityIDs are fine (public). Symbols, descriptions are fine.
- Trade IDs, order IDs, exec IDs → `"123"`, `"9876543210"`, etc.

## Unknown-attribute tolerance

The parser has an opt-in mode for shrugging off unknown attributes:

```python
import ibflex
ibflex.enable_unknown_attribute_tolerance()
```

If a user reports a `FlexParserError: NewClass has no attribute newField`,
they can use this as an immediate workaround while a fix is in flight. PRs
adding fields should not rely on or modify this feature.

## Running mutation tests

Optional but recommended for any change touching `ibflex/parser.py`:

```sh
pip install mutmut
mutmut run --paths-to-mutate ibflex/parser.py
```

## Resolving upstream sync conflicts

`.github/workflows/sync-upstream.yml` opens a daily PR from `csingley/ibflex`
master into our master. When it conflicts:

```sh
git fetch upstream
git checkout master
git merge upstream/master
# resolve conflicts; favor keeping ibflex2-specific cleanup (pyproject.toml,
# tolerance feature, etc.)
git push origin master
```

The fork's CHANGELOG entry should note any upstream changes that affected
public behavior.

## What not to do

- Don't change `Optional[X]` annotations to `X | None` syntax in `Types.py`
  or `parser.py`. The parser's `ATTRIB_CONVERTERS` table is keyed on the
  string form of the annotation, and PEP 604 syntax silently breaks the
  dispatch.
- Don't switch back to `xml.etree.ElementTree` from `defusedxml`.
- Don't add fields to `SymbolSummary` without verifying they don't already
  exist earlier in the dataclass — past PRs have introduced duplicates from
  bad merges.

## Releasing

1. Bump `ibflex/__version__.__version__`.
2. Move `Unreleased` entries in `CHANGELOG.md` under a dated heading.
3. Commit and push to master.
4. Create a GitHub Release with a tag matching the new version.
5. `publish.yml` builds and uploads to PyPI via trusted publishing.
