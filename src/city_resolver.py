"""City name normalization for Gaode weather queries."""


class CityResolutionError(ValueError):
    """Raised when a city name cannot be resolved."""


ENGLISH_CITY_MAP = {
    "beijing": "北京",
    "peking": "北京",
    "shanghai": "上海",
    "guangzhou": "广州",
    "shenzhen": "深圳",
    "hangzhou": "杭州",
    "nanjing": "南京",
    "suzhou": "苏州",
    "chengdu": "成都",
    "chongqing": "重庆",
    "wuhan": "武汉",
    "xian": "西安",
    "xi'an": "西安",
    "tianjin": "天津",
    "qingdao": "青岛",
    "changsha": "长沙",
    "zhengzhou": "郑州",
    "ningbo": "宁波",
    "xiamen": "厦门",
    "fuzhou": "福州",
    "jinan": "济南",
    "kunming": "昆明",
    "hefei": "合肥",
    "shenyang": "沈阳",
    "dalian": "大连",
    "harbin": "哈尔滨",
    "changchun": "长春",
    "haikou": "海口",
    "sanya": "三亚",
    "lhasa": "拉萨",
    "urumqi": "乌鲁木齐",
    "hohhot": "呼和浩特",
    "taiyuan": "太原",
    "nanchang": "南昌",
    "guiyang": "贵阳",
    "lanzhou": "兰州",
    "xining": "西宁",
    "yinchuan": "银川",
    "nanning": "南宁",
}


def resolve_city(city: str) -> str:
    """Return a Gaode-compatible Chinese city name."""
    normalized = (city or "").strip()
    if not normalized:
        raise CityResolutionError("无法识别城市：城市名称不能为空")

    if _contains_chinese(normalized):
        return normalized

    key = " ".join(normalized.lower().split())
    if key in ENGLISH_CITY_MAP:
        return ENGLISH_CITY_MAP[key]

    raise CityResolutionError(f"无法识别城市：{city}。请使用中文城市名，或扩展英文城市映射。")


def _contains_chinese(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)
