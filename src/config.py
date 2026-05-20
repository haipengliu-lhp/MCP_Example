"""Runtime configuration for the Gaode weather MCP server."""

from __future__ import annotations

import os


GAODE_API_KEY_ENV = "GAODE_API_KEY"


def get_gaode_api_key() -> str:
    return os.getenv(GAODE_API_KEY_ENV, "").strip()
