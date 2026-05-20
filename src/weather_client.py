"""Local example MCP client for the Gaode weather server."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError as exc:  # pragma: no cover - depends on optional runtime package.
    raise SystemExit("缺少 MCP Python SDK，请先运行：pip install -r requirements.txt") from exc


SERVER_PATH = Path(__file__).with_name("weather_server.py")


async def call_weather(city: str, extensions: str) -> Any:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=os.environ.copy(),
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_weather",
                arguments={"city": city, "extensions": extensions},
            )
            return result


def main() -> None:
    parser = argparse.ArgumentParser(description="调用本地 MCP 高德天气 Server。")
    parser.add_argument("city", help="城市名，支持中文或常见英文，例如 北京 / Shanghai")
    parser.add_argument(
        "--extensions",
        choices=["base", "all"],
        default="base",
        help="base 查询实时天气，all 查询天气预报。",
    )
    args = parser.parse_args()

    result = asyncio.run(call_weather(args.city, args.extensions))
    print(json.dumps(_serialize_result(result), ensure_ascii=False, indent=2))


def _serialize_result(result: Any) -> Any:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return result


if __name__ == "__main__":
    main()
