"""Property-based tests for the prep_date / prep_time / prep_datetime
helpers. Hypothesis generates random valid (year, month, day, hour, minute,
second) tuples, formats them in every IBKR-supported textual representation,
and asserts that the parser round-trips back to the original.

The brute-force no-separator path in `prep_datetime` is the trickiest code
in the parser (it tries every TIME_FORMATS length until one fits), so it gets
its own pass.
"""
import datetime

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings

from ibflex import parser

# IBKR-documented date formats.
DATE_FORMATTERS = [
    lambda d: d.strftime("%Y%m%d"),
    lambda d: d.strftime("%Y-%m-%d"),
    lambda d: d.strftime("%m/%d/%Y"),
    lambda d: d.strftime("%m/%d/%y"),
    # %d-%b-%y is locale-dependent (%b returns localized month name).
    # Force English so this test is locale-independent in CI.
    lambda d: d.strftime("%d-") + (
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[d.month - 1]
    ) + d.strftime("-%y"),
]

TIME_FORMATTERS = [
    lambda t: t.strftime("%H%M%S"),
    lambda t: t.strftime("%H:%M:%S"),
]

SEPARATORS = [";", ",", " ", "T"]


@st.composite
def safe_date(draw):
    """Dates within the practical IBKR Flex Query window.

    Python's `%y` strptime maps 2-digit years 00-68 to 20xx and 69-99 to 19xx,
    so the supported 2-digit-year formats are inherently lossy for years >2068.
    Cap at 2068 to keep the property test deterministic; real IBKR Flex data
    won't carry years that far in the future anyway.
    """
    return draw(st.dates(
        min_value=datetime.date(2000, 1, 1),
        max_value=datetime.date(2068, 12, 31),
    ))


@st.composite
def safe_time(draw):
    return draw(st.times(min_value=datetime.time(0, 0, 0),
                         max_value=datetime.time(23, 59, 59)))


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(d=safe_date(), formatter_idx=st.integers(min_value=0, max_value=len(DATE_FORMATTERS) - 1))
def test_prep_date_round_trip(d, formatter_idx):
    raw = DATE_FORMATTERS[formatter_idx](d)
    self_y, self_m, self_d = parser.prep_date(raw)
    assert (self_y, self_m, self_d) == (d.year, d.month, d.day), (
        f"prep_date({raw!r}) returned {(self_y, self_m, self_d)} "
        f"but expected {(d.year, d.month, d.day)}"
    )


@given(t=safe_time(), formatter_idx=st.integers(min_value=0, max_value=len(TIME_FORMATTERS) - 1))
def test_prep_time_round_trip(t, formatter_idx):
    raw = TIME_FORMATTERS[formatter_idx](t)
    h, m, s = parser.prep_time(raw)
    assert (h, m, s) == (t.hour, t.minute, t.second)


@given(
    d=safe_date(),
    t=safe_time(),
    date_idx=st.integers(min_value=0, max_value=len(DATE_FORMATTERS) - 1),
    time_idx=st.integers(min_value=0, max_value=len(TIME_FORMATTERS) - 1),
    sep_idx=st.integers(min_value=0, max_value=len(SEPARATORS) - 1),
)
def test_prep_datetime_with_separator(d, t, date_idx, time_idx, sep_idx):
    """Every (date_format, time_format, separator) combo round-trips."""
    raw = (
        DATE_FORMATTERS[date_idx](d)
        + SEPARATORS[sep_idx]
        + TIME_FORMATTERS[time_idx](t)
    )
    parts = parser.prep_datetime(raw)
    assert parts == (d.year, d.month, d.day, t.hour, t.minute, t.second), (
        f"prep_datetime({raw!r}) returned {parts} "
        f"but expected {(d.year, d.month, d.day, t.hour, t.minute, t.second)}"
    )


@given(
    d=safe_date(),
    t=safe_time(),
    date_idx=st.integers(min_value=0, max_value=len(DATE_FORMATTERS) - 1),
    time_idx=st.integers(min_value=0, max_value=len(TIME_FORMATTERS) - 1),
)
def test_prep_datetime_no_separator(d, t, date_idx, time_idx):
    """The brute-force no-separator path must reconstruct date+time correctly."""
    raw = DATE_FORMATTERS[date_idx](d) + TIME_FORMATTERS[time_idx](t)
    parts = parser.prep_datetime(raw)
    assert parts == (d.year, d.month, d.day, t.hour, t.minute, t.second), (
        f"prep_datetime({raw!r}) returned {parts}"
    )


@given(d=safe_date(), date_idx=st.integers(min_value=0, max_value=len(DATE_FORMATTERS) - 1))
def test_prep_datetime_bare_date(d, date_idx):
    """A bare date with no time component is accepted by prep_datetime."""
    raw = DATE_FORMATTERS[date_idx](d)
    parts = parser.prep_datetime(raw)
    assert parts == (d.year, d.month, d.day)
