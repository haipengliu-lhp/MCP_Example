import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class CityResolverTests(unittest.TestCase):
    def test_keeps_chinese_city_name(self):
        from city_resolver import resolve_city

        self.assertEqual(resolve_city("北京"), "北京")
        self.assertEqual(resolve_city("上海市"), "上海市")

    def test_maps_common_english_city_name_to_chinese(self):
        from city_resolver import resolve_city

        self.assertEqual(resolve_city("Beijing"), "北京")
        self.assertEqual(resolve_city(" shanghai "), "上海")

    def test_rejects_unknown_city_with_chinese_error(self):
        from city_resolver import CityResolutionError, resolve_city

        with self.assertRaisesRegex(CityResolutionError, "无法识别城市"):
            resolve_city("not-a-real-city")


if __name__ == "__main__":
    unittest.main()
