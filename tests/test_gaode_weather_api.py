import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class GaodeWeatherApiTests(unittest.TestCase):
    def test_requires_api_key(self):
        from gaode_weather_api import GaodeWeatherClient, WeatherApiError

        client = GaodeWeatherClient(api_key="")

        with self.assertRaisesRegex(WeatherApiError, "GAODE_API_KEY"):
            client.get_weather("北京")

    def test_parses_base_weather_response_as_chinese_fields(self):
        from gaode_weather_api import GaodeWeatherClient

        def fake_get(url, params, timeout):
            self.assertEqual(params["city"], "上海")
            self.assertEqual(params["extensions"], "base")
            return FakeResponse(
                {
                    "status": "1",
                    "lives": [
                        {
                            "province": "上海",
                            "city": "上海市",
                            "weather": "晴",
                            "temperature": "26",
                            "humidity": "62",
                            "winddirection": "东南",
                            "windpower": "≤3",
                            "reporttime": "2026-05-20 10:00:00",
                        }
                    ],
                }
            )

        client = GaodeWeatherClient(api_key="test-key", http_get=fake_get)

        self.assertEqual(
            client.get_weather("上海"),
            {
                "城市": "上海市",
                "省份": "上海",
                "天气": "晴",
                "温度": "26℃",
                "湿度": "62%",
                "风向": "东南",
                "风力": "≤3级",
                "发布时间": "2026-05-20 10:00:00",
            },
        )

    def test_parses_forecast_response(self):
        from gaode_weather_api import GaodeWeatherClient

        def fake_get(url, params, timeout):
            self.assertEqual(params["extensions"], "all")
            return FakeResponse(
                {
                    "status": "1",
                    "forecasts": [
                        {
                            "province": "北京",
                            "city": "北京市",
                            "reporttime": "2026-05-20 10:00:00",
                            "casts": [
                                {
                                    "date": "2026-05-20",
                                    "week": "3",
                                    "dayweather": "晴",
                                    "nightweather": "多云",
                                    "daytemp": "28",
                                    "nighttemp": "18",
                                    "daywind": "东北",
                                    "nightwind": "北",
                                    "daypower": "≤3",
                                    "nightpower": "≤3",
                                }
                            ],
                        }
                    ],
                }
            )

        client = GaodeWeatherClient(api_key="test-key", http_get=fake_get)

        self.assertEqual(
            client.get_weather("北京", extensions="all"),
            {
                "城市": "北京市",
                "省份": "北京",
                "发布时间": "2026-05-20 10:00:00",
                "预报": [
                    {
                        "日期": "2026-05-20",
                        "星期": "3",
                        "白天天气": "晴",
                        "夜间天气": "多云",
                        "白天温度": "28℃",
                        "夜间温度": "18℃",
                        "白天风向": "东北",
                        "夜间风向": "北",
                        "白天风力": "≤3级",
                        "夜间风力": "≤3级",
                    }
                ],
            },
        )

    def test_converts_gaode_failure_to_chinese_error(self):
        from gaode_weather_api import GaodeWeatherClient, WeatherApiError

        def fake_get(url, params, timeout):
            return FakeResponse({"status": "0", "info": "INVALID_USER_KEY", "infocode": "10001"})

        client = GaodeWeatherClient(api_key="test-key", http_get=fake_get)

        with self.assertRaisesRegex(WeatherApiError, "高德天气接口调用失败"):
            client.get_weather("北京")


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


if __name__ == "__main__":
    unittest.main()
