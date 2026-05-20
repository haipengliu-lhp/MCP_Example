import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class WebApiTests(unittest.TestCase):
    def test_weather_endpoint_returns_chinese_weather_payload(self):
        from fastapi.testclient import TestClient
        from web_api import app

        async def fake_call_weather(city, extensions):
            self.assertEqual(city, "上海")
            self.assertEqual(extensions, "base")
            return {
                "城市": "上海市",
                "天气": "晴",
                "温度": "26℃",
            }

        with patch("web_api.call_weather", fake_call_weather):
            response = TestClient(app).get("/api/weather", params={"city": "上海"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "城市": "上海市",
                "天气": "晴",
                "温度": "26℃",
            },
        )

    def test_weather_endpoint_requires_city(self):
        from fastapi.testclient import TestClient
        from web_api import app

        response = TestClient(app).get("/api/weather", params={"city": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertIn("城市不能为空", response.json()["detail"])

    def test_index_page_is_served(self):
        from fastapi.testclient import TestClient
        from web_api import app

        response = TestClient(app).get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("高德天气 MCP 查询", response.text)


if __name__ == "__main__":
    unittest.main()
