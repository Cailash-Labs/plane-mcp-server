"""Pytest configuration for Plane MCP Server tests."""

import os

# The Cailash fork defaults to the Community edition, which hides tools whose routes
# Community lacks. The upstream suite asserts over the full catalogue, so it runs
# against that unless a test chooses otherwise.
os.environ.setdefault("PLANE_EDITION", "full")
