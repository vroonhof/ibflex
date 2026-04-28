# Test fixtures

Each `.xml` file is a complete `FlexQueryResponse` document, stripped of any
real account/personal information. Tests in `test_fixtures.py` parse every
file in this directory and verify the result is a valid `FlexQueryResponse`.

## Files

- `minimal.xml` — empty FlexStatement; smoke test.
- `activity_basic.xml` — common Activity sections (Trades, OpenPositions,
  CashTransactions, ConversionRates, SecuritiesInfo).
- `activity_full.xml` — broad coverage including
  EquitySummaryByReportDateInBase, MTM/FIFO performance summaries, fee
  details, corporate actions, transfers, dividend accruals.
- `tradeconfirm.xml` — a TradeConfirm Flex report.
- `crypto_transfer.xml` — Transfer with assetCategory="CRYPTO" and
  TransferType="OTC" (regression test for the new fields).
- `stock_grant.xml` — StockGrantActivity (the new dataclass added in this
  fork).
- `legacy_separator.xml` — uses the old `", "` (comma-space) datetime
  separator. Regression test for the parser's `replace(", ", ",")` shim.

## Adding fixtures

1. Get a real Flex report from IBKR (Reports > Flex Queries > Run).
2. Anonymize per `CONTRIBUTING.md` — replace account IDs, names, addresses,
   account aliases. Trade IDs and order IDs should be replaced with short
   numeric stand-ins.
3. Save as `tests/fixtures/<descriptive_name>.xml`.
4. Run `pytest tests/test_fixtures.py` to confirm it parses.
5. Optionally add specific assertions in `test_fixtures.py` if the file
   exercises a particular code path worth pinning.
