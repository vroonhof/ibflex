"""Exhaustive parametrized tests for every IBKR date/time/datetime format
combination. The IBKR Flex Query Reference documents these as user-selectable;
real reports come back with whichever combination the user picked.

This file deliberately exercises *every* documented combination so locale
differences (e.g. `%B` month names on macOS/Windows) and edge values (`MULTI`,
trailing TZ offsets, the legacy `", "` separator) surface in CI matrix runs.
"""
import datetime
import unittest

from ibflex import parser

REFERENCE_DATE = datetime.date(2016, 2, 29)
REFERENCE_TIME = datetime.time(14, 35, 29)
REFERENCE_DATETIME = datetime.datetime(2016, 2, 29, 14, 35, 29)


# Every (length, slash-count, format) tuple from parser.DATE_FORMATS together
# with the canonical string IBKR sends for the reference date.
DATE_CASES = [
    ("20160229", "%Y%m%d"),
    ("2016-02-29", "%Y-%m-%d"),
    ("02/29/2016", "%m/%d/%Y"),
    ("02/29/16", "%m/%d/%y"),
    ("29-Feb-16", "%d-%b-%y"),
]

TIME_CASES = [
    ("143529", "%H%M%S"),
    ("14:35:29", "%H:%M:%S"),
]

DATETIME_SEPARATORS = [";", ",", " ", "T"]


class DateMatrixTestCase(unittest.TestCase):
    """Every supported date format parses to the same date."""

    def test_every_date_format(self):
        for raw, fmt in DATE_CASES:
            with self.subTest(raw=raw, fmt=fmt):
                self.assertEqual(parser.convert_date(raw), REFERENCE_DATE)

    def test_blank_date_returns_none(self):
        self.assertIsNone(parser.make_optional(parser.convert_date)(""))

    def test_multi_returns_none(self):
        self.assertIsNone(parser.prep_date("MULTI"))


class TimeMatrixTestCase(unittest.TestCase):
    def test_every_time_format(self):
        for raw, fmt in TIME_CASES:
            with self.subTest(raw=raw, fmt=fmt):
                self.assertEqual(parser.convert_time(raw), REFERENCE_TIME)


class DatetimeMatrixTestCase(unittest.TestCase):
    """Every (date_format, time_format, separator) combination round-trips."""

    def test_every_combination(self):
        for date_str, _ in DATE_CASES:
            for time_str, _ in TIME_CASES:
                for sep in DATETIME_SEPARATORS:
                    raw = f"{date_str}{sep}{time_str}"
                    with self.subTest(raw=raw):
                        self.assertEqual(
                            parser.convert_datetime(raw), REFERENCE_DATETIME
                        )

    def test_no_separator_two_format_combos(self):
        """No-separator path requires brute-force time-length detection."""
        for date_str, _ in DATE_CASES:
            for time_str, _ in TIME_CASES:
                raw = f"{date_str}{time_str}"
                with self.subTest(raw=raw):
                    self.assertEqual(
                        parser.convert_datetime(raw), REFERENCE_DATETIME
                    )

    def test_legacy_comma_space_separator(self):
        """Some old reports used ", " (comma-space). Parser strips the space."""
        raw = "20160229, 143529"
        self.assertEqual(parser.convert_datetime(raw), REFERENCE_DATETIME)

    def test_trailing_tz_offset_dropped(self):
        """Some old reports used 'T' separator and appended a TZ offset."""
        for offset in ("-0500", "+0000", "-0400"):
            raw = f"20160229T143529{offset}"
            with self.subTest(offset=offset):
                self.assertEqual(
                    parser.convert_datetime(raw), REFERENCE_DATETIME
                )

    def test_multi_returns_none(self):
        self.assertIsNone(parser.prep_datetime("MULTI"))

    def test_bare_date_no_time(self):
        """Bare date (no separator, no time) parses as a date."""
        self.assertEqual(
            parser.prep_datetime("20160229"),
            (2016, 2, 29),
        )

    def test_multiple_separators_raises(self):
        """A value with two different separators is rejected."""
        with self.assertRaises(parser.FlexParserError):
            parser.prep_datetime("20160229; 14:35:29")  # ';' AND ' '


class OptionalEmptyValueTestCase(unittest.TestCase):
    """Sentinel empty values used by IBKR to indicate null."""

    def test_empty_string_treated_as_null(self):
        for sentinel in ("", "-", "--", "N/A"):
            with self.subTest(sentinel=sentinel):
                opt_decimal = parser.make_optional(parser.convert_decimal)
                self.assertIsNone(opt_decimal(sentinel))


if __name__ == "__main__":
    unittest.main()
