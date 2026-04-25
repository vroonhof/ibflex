"""Walks every .xml file under tests/fixtures/ and verifies it parses into
a valid FlexQueryResponse. Use this directory to drop anonymized real-world
Flex reports — they get parsing coverage automatically.

Per-fixture assertions live in dedicated `test_<fixture>` functions below
when a fixture exists to pin a specific code path (e.g. the new dataclasses
or legacy separator).
"""
import unittest
from pathlib import Path

from ibflex import Types, parser

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_FILES = sorted(FIXTURES.glob("*.xml"))


class FixtureCorpusTestCase(unittest.TestCase):
    """Every fixture parses without raising."""

    def test_all_fixtures_parse(self):
        self.assertGreater(
            len(FIXTURE_FILES), 0,
            "No fixtures found under tests/fixtures/",
        )
        for path in FIXTURE_FILES:
            with self.subTest(fixture=path.name):
                response = parser.parse(str(path))
                self.assertIsInstance(response, Types.FlexQueryResponse)
                self.assertGreaterEqual(len(response.FlexStatements), 0)


class StockGrantFixtureTestCase(unittest.TestCase):
    """Pin StockGrantActivity parsing via the dedicated fixture."""

    def test_stock_grant(self):
        response = parser.parse(str(FIXTURES / "stock_grant.xml"))
        stmt = response.FlexStatements[0]
        self.assertEqual(len(stmt.StockGrantActivities), 1)
        grant = stmt.StockGrantActivities[0]
        self.assertEqual(grant.symbol, "IBKR")
        self.assertEqual(grant.activityDescription,
                         "Stock Award Grant for Cash Deposit")


class CryptoTransferFixtureTestCase(unittest.TestCase):
    """Pin Transfer with CRYPTO + OTC + new fields."""

    def test_crypto_transfer(self):
        response = parser.parse(str(FIXTURES / "crypto_transfer.xml"))
        stmt = response.FlexStatements[0]
        self.assertEqual(len(stmt.Transfers), 1)
        tx = stmt.Transfers[0]
        self.assertEqual(tx.assetCategory.name, "CRYPTOCURRENCY")
        self.assertEqual(tx.type.name, "OTC")
        self.assertEqual(tx.levelOfDetail, "TRANSFER")


class LegacySeparatorFixtureTestCase(unittest.TestCase):
    """Pin the legacy ', ' (comma-space) datetime separator regression."""

    def test_legacy_separator(self):
        response = parser.parse(str(FIXTURES / "legacy_separator.xml"))
        stmt = response.FlexStatements[0]
        self.assertEqual(len(stmt.CashTransactions), 1)
        tx = stmt.CashTransactions[0]
        self.assertEqual(tx.dateTime.year, 2017)
        self.assertEqual(tx.dateTime.month, 1)


if __name__ == "__main__":
    unittest.main()
