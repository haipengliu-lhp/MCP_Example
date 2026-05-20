"""MCP stdio server exposing Gaode weather tools."""

from __future__ import annotations

from typing import Any

from city_resolver import CityResolutionError, resolve_city
from config import get_gaode_api_key
from gaode_weather_api import GaodeWeatherClient, WeatherApiError

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - depends on optional runtime package.
    raise SystemExit("缺少 MCP Python SDK，请先运行：pip install -r requirements.txt") from exc


mcp = FastMCP("gaode-weather")


@mcp.tool()
def get_weather(city: str, extensions: str = "base") -> dict[str, Any]:
    """查询高德地图天气，支持中文或常见英文城市名，返回中文字段。"""
    try:
        resolved_city = resolve_city(city)
        client = GaodeWeatherClient(api_key=get_gaode_api_key())
        return client.get_weather(resolved_city, extensions=extensions)
    except (CityResolutionError, WeatherApiError) as exc:
        raise ValueError(str(exc)) from exc


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
