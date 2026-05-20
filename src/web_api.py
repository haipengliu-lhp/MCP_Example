"""HTTP bridge that lets a browser call the MCP weather server."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

try:
    from .weather_client import call_weather
except ImportError:  # pragma: no cover - supports direct test imports from src path.
    from weather_client import call_weather


ROOT = Path(__file__).resolve().parents[1]
WEB_INDEX = ROOT / "web" / "index.html"

app = FastAPI(title="MCP 高德天气 Web API")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_INDEX)


@app.get("/api/weather")
async def weather(
    city: str = Query(..., description="城市名，支持中文或常见英文"),
    extensions: str = Query("base", pattern="^(base|all)$", description="base 实时天气，all 天气预报"),
) -> dict[str, Any]:
    if not city.strip():
        raise HTTPException(status_code=400, detail="城市不能为空")

    result = await call_weather(city.strip(), extensions)
    payload = _extract_payload(result)
    if _is_error_result(result):
        raise HTTPException(status_code=502, detail=_extract_error_text(result))
    return payload


def _extract_payload(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result

    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured

    if hasattr(result, "model_dump"):
        dumped = result.model_dump()
        if isinstance(dumped.get("structuredContent"), dict):
            return dumped["structuredContent"]
        return dumped

    raise HTTPException(status_code=502, detail="MCP Server 返回了无法解析的数据。")


def _is_error_result(result: Any) -> bool:
    if isinstance(result, dict):
        return False
    return bool(getattr(result, "isError", False))


def _extract_error_text(result: Any) -> str:
    content = getattr(result, "content", None) or []
    if content:
        first = content[0]
        text = getattr(first, "text", None)
        if text:
            return text
    return "MCP Server 调用失败。"
