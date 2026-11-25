"""Which tools a Plane edition can actually serve.

Cailash fork addition. Self-hosted Plane Community registers no public API route
for estimates, work item types, custom properties or customers, so every call to
those tools answers 404. Advertising them only teaches an agent to waste calls,
so on Community they are not registered at all.

`PLANE_EDITION` selects the edition. This fork defaults to `community`; any other
value (`full`, `cloud`, ...) advertises the whole catalogue, as upstream does.
"""

from __future__ import annotations

import os

DEFAULT_EDITION = "community"

COMMUNITY_HIDDEN: frozenset[str] = frozenset(
    {
        "project_estimate",
        "workitem_type",
        "workitem_property",
        "customer",
        "customer_property",
        "customer_request",
    }
)


def edition() -> str:
    return (os.getenv("PLANE_EDITION") or DEFAULT_EDITION).strip().lower()


def hidden_tools() -> frozenset[str]:
    """Tool names not to register for the configured edition."""
    return COMMUNITY_HIDDEN if edition() == "community" else frozenset()
