"""Small Gaode weather API wrapper with Chinese output fields."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Callable


GAODE_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
SUPPORTED_EXTENSIONS = {"base", "all"}


class WeatherApiError(RuntimeError):
    """Raised when weather data cannot be fetched or parsed."""


class GaodeWeatherClient:
    def __init__(
        self,
        api_key: str,
        http_get: Callable[[str, dict[str, str], float], Any] | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.http_get = http_get or urllib_get
        self.timeout = timeout

    def get_weather(self, city: str, extensions: str = "base") -> dict[str, Any]:
        if not self.api_key:
            raise WeatherApiError("缺少 GAODE_API_KEY，请先在环境变量中配置高德地图 API Key。")
        if extensions not in SUPPORTED_EXTENSIONS:
            raise WeatherApiError("extensions 参数只支持 base 或 all。")

        payload = self._fetch(city=city, extensions=extensions)
        if extensions == "base":
            return parse_base_weather(payload)
        return parse_forecast_weather(payload)

    def _fetch(self, city: str, extensions: str) -> dict[str, Any]:
        params = {
            "key": self.api_key,
            "city": city,
            "extensions": extensions,
            "output": "JSON",
        }

        try:
            response = self.http_get(GAODE_WEATHER_URL, params, self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # noqa: BLE001 - normalize third-party failures.
            raise WeatherApiError(f"高德天气接口请求失败：{exc}") from exc

        if payload.get("status") != "1":
            info = payload.get("info") or "未知错误"
            infocode = payload.get("infocode") or "无错误码"
            raise WeatherApiError(f"高德天气接口调用失败：{info}（{infocode}）")

        return payload


def parse_base_weather(payload: dict[str, Any]) -> dict[str, str]:
    lives = payload.get("lives") or []
    if not lives:
        raise WeatherApiError("高德天气接口未返回实时天气数据。")

    live = lives[0]
    return {
        "城市": _text(live, "city"),
        "省份": _text(live, "province"),
        "天气": _text(live, "weather"),
        "温度": _with_suffix(_text(live, "temperature"), "℃"),
        "湿度": _with_suffix(_text(live, "humidity"), "%"),
        "风向": _text(live, "winddirection"),
        "风力": _with_suffix(_text(live, "windpower"), "级"),
        "发布时间": _text(live, "reporttime"),
    }


def parse_forecast_weather(payload: dict[str, Any]) -> dict[str, Any]:
    forecasts = payload.get("forecasts") or []
    if not forecasts:
        raise WeatherApiError("高德天气接口未返回天气预报数据。")

    forecast = forecasts[0]
    casts = forecast.get("casts") or []
    return {
        "城市": _text(forecast, "city"),
        "省份": _text(forecast, "province"),
        "发布时间": _text(forecast, "reporttime"),
        "预报": [_parse_cast(cast) for cast in casts],
    }


def urllib_get(url: str, params: dict[str, str], timeout: float) -> "UrllibResponse":
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(f"{url}?{query}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        body = response.read().decode("utf-8")
    return UrllibResponse(status=status, body=body)


class UrllibResponse:
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise WeatherApiError(f"HTTP {self.status}")

    def json(self) -> dict[str, Any]:
        return json.loads(self.body)


def _parse_cast(cast: dict[str, Any]) -> dict[str, str]:
    return {
        "日期": _text(cast, "date"),
        "星期": _text(cast, "week"),
        "白天天气": _text(cast, "dayweather"),
        "夜间天气": _text(cast, "nightweather"),
        "白天温度": _with_suffix(_text(cast, "daytemp"), "℃"),
        "夜间温度": _with_suffix(_text(cast, "nighttemp"), "℃"),
        "白天风向": _text(cast, "daywind"),
        "夜间风向": _text(cast, "nightwind"),
        "白天风力": _with_suffix(_text(cast, "daypower"), "级"),
        "夜间风力": _with_suffix(_text(cast, "nightpower"), "级"),
    }


def _text(source: dict[str, Any], key: str) -> str:
    value = source.get(key)
    if value is None or value == "":
        return "未知"
    return str(value)


def _with_suffix(value: str, suffix: str) -> str:
    if value == "未知" or value.endswith(suffix):
        return value
    return f"{value}{suffix}"
