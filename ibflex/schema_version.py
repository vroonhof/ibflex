"""Pinned reference for the IBKR Activity Flex Query schema.

The date below is the most recent IBKR Reference revision that the
Types.py annotations have been audited against. The schema-drift CI job
uses this to know when a manual reconciliation is overdue.

Bump this when:
- the schema-drift CI job opens an issue, you triage it, and merge any
  resulting field additions
- you manually re-read the IBKR Activity Flex Query Reference end-to-end
"""

#: ISO-8601 date of the last full audit of the IBKR Activity Flex Query
#: Reference against ibflex.Types annotations.
SCHEMA_AUDIT_DATE = "2026-04-25"

#: URL of the IBKR Activity Flex Query Reference.
SCHEMA_REFERENCE_URL = (
    "https://www.interactivebrokers.com/en/software/reportguide/"
    "reportguide.htm"
)
