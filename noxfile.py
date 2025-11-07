"""Reusable automation sessions for json-tools."""

from __future__ import annotations

import nox

nox.options.sessions = ["tests"]


@nox.session(python=["3.10", "3.11", "3.12"])
def tests(session: nox.Session) -> None:
    """Run the pytest suite with coverage."""

    session.install(".[test]")
    session.run("pytest", "--cov=json_tools", "--cov-report=term-missing", "--cov-report=html")
