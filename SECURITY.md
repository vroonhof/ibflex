# Security policy

## Supported versions

Security fixes land on `master`. Latest release on PyPI gets the fix.

## Reporting a vulnerability

Open a [private security advisory](https://github.com/robcohen/ibflex2/security/advisories/new) on GitHub. Please **do not** open a public issue or PR for a vulnerability.

Expect an acknowledgement within a week. If the report is valid we will:

1. Confirm the issue and its scope.
2. Prepare a fix on a private branch.
3. Coordinate disclosure timing with the reporter.
4. Release a patched version and credit the reporter (if requested).

## Threat model

`ibflex2` parses XML produced by Interactive Brokers' Flex Query system. Inputs may originate from:

- IBKR servers (via `ibflex.client.download`)
- Files saved by the user from IBKR's web UI
- Forwarded reports from third parties (less common, but possible)

The library uses [`defusedxml`](https://pypi.org/project/defusedxml/) to guard against the standard XML attack vectors:

- XML External Entity (XXE) processing
- Entity-expansion ("billion laughs") denial of service
- DTD-based attacks
- External resource fetching

The HTTP client (`ibflex.client`) only talks to the IBKR Flex Web Service endpoints (`gdcdyn.interactivebrokers.com`); it does not follow redirects to user-controlled URLs.

## What is *not* in scope

- The IBKR Flex Web Service itself
- The user's choice of where to store Flex tokens or reports
- Numerical correctness of derived values (we parse what IBKR sends; we don't recompute)
