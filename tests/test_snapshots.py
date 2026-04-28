"""Snapshot tests: parse each fixture under tests/fixtures/ and compare its
serialized form against a committed snapshot under tests/snapshots/. Catches
silent behavioral regressions in parsing or representation.

Update workflow:
    pytest tests/test_snapshots.py -v
    # On failure, inspect the diff. If the new output is correct:
    SNAPSHOT_UPDATE=1 pytest tests/test_snapshots.py
    git add tests/snapshots/
    git commit
"""
import os
import unittest
from pathlib import Path

from ibflex import parser

FIXTURES = Path(__file__).parent / "fixtures"
SNAPSHOTS = Path(__file__).parent / "snapshots"
FIXTURE_FILES = sorted(FIXTURES.glob("*.xml"))


def _serialize(response) -> str:
    """Stable, diff-friendly representation of a parsed FlexQueryResponse.

    Uses the dataclasses' own __repr__ which we've validated elsewhere.
    Each FlexStatement is on its own line; sequences are grouped per type.
    """
    lines = [repr(response)]
    for stmt in response.FlexStatements:
        lines.append("")
        lines.append(repr(stmt))
        for name in stmt.__annotations__:
            value = getattr(stmt, name, None)
            if isinstance(value, tuple) and value:
                lines.append(f"  {name}:")
                for item in value:
                    lines.append(f"    {item!r}")
            elif value is not None and not isinstance(value, tuple):
                # Scalar fields like fromDate / accountId are already shown
                # in the FlexStatement repr; skip to avoid duplication.
                pass
    return "\n".join(lines) + "\n"


class SnapshotTestCase(unittest.TestCase):
    """Each fixture's parsed output must match its committed snapshot."""

    def test_fixture_snapshots(self):
        update = os.environ.get("SNAPSHOT_UPDATE") == "1"
        SNAPSHOTS.mkdir(exist_ok=True)

        for path in FIXTURE_FILES:
            with self.subTest(fixture=path.name):
                response = parser.parse(str(path))
                actual = _serialize(response)
                snap_path = SNAPSHOTS / f"{path.stem}.snap"

                if update or not snap_path.exists():
                    snap_path.write_text(actual)
                    continue

                expected = snap_path.read_text()
                self.assertEqual(
                    actual, expected,
                    f"\nSnapshot mismatch for {path.name}.\n"
                    f"To accept the new output, run:\n"
                    f"    SNAPSHOT_UPDATE=1 pytest tests/test_snapshots.py\n"
                )


if __name__ == "__main__":
    unittest.main()
