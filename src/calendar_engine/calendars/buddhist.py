"""日历引擎 — 佛菩萨圣诞日判定模块。

数据来源：灵隐寺官方日历（2023 版）
节日为固定农历日期，农历月大月（30 天）则照常，
小月（29 天）时三十日节日自动调整为廿九日。
"""

import datetime
from lunar_python import Lunar

# (农历月, 农历日, 节日名)
# 来源：灵隐寺「2023年诸佛菩萨圣诞日」
BUDDHIST_FESTIVALS: list[tuple[int, int, str]] = [
    (12, 23, "监斋菩萨圣诞"),
    (12, 29, "华严菩萨圣诞"),
    (1,  1,  "弥勒菩萨圣诞"),
    (2,  8,  "释迦牟尼佛出家日"),
    (2,  15, "释迦牟尼佛涅槃日"),
    (2,  19, "观世音菩萨圣诞"),
    (2,  21, "普贤菩萨圣诞"),
    (3,  16, "准提菩萨圣诞"),
    (4,  4,  "文殊菩萨圣诞"),
    (4,  8,  "释迦牟尼佛圣诞"),
    (4,  15, "佛吉祥日（卫塞节）"),
    (4,  28, "药王菩萨圣诞"),
    (5,  13, "伽蓝菩萨圣诞"),
    (6,  3,  "韦驮菩萨圣诞"),
    (6,  19, "观世音菩萨成道日"),
    (7,  13, "大势至菩萨圣诞"),
    (7,  15, "佛欢喜日（盂兰盆节）"),
    (7,  24, "龙树菩萨圣诞"),
    (7,  30, "地藏菩萨圣诞"),   # 小月时降为廿九
    (8,  15, "月光菩萨圣诞"),
    (8,  22, "燃灯佛圣诞"),
    (9,  9,  "摩利支天菩萨圣诞"),
    (9,  19, "观世音菩萨出家日"),
    (9,  29, "药师佛圣诞"),     # 小月时降为廿九
    (11, 17, "阿弥陀佛圣诞"),
    (12, 8,  "释迦牟尼佛成道日（腊八）"),
]

# 构建快速查找表：农历 (月, 日) → 节日名
_FESTIVAL_MAP: dict[tuple[int, int], str] = {}
for lm, ld, name in BUDDHIST_FESTIVALS:
    _FESTIVAL_MAP[(lm, ld)] = name


def is_observance(solar_date: datetime.date) -> bool:
    """判断公历日期是否为佛菩萨圣诞日。

    Args:
        solar_date: 公历日期。

    Returns:
        该日期是佛菩萨圣诞日返回 True，否则 False。
    """
    dt = datetime.datetime.combine(solar_date, datetime.time.min)
    lunar = Lunar.fromDate(dt)
    month = lunar.getMonth()
    day = lunar.getDay()

    # 三十日节日：小月无三十，视为廿九
    if day == 30 and (month, 30) in _FESTIVAL_MAP:
        try:
            Lunar.fromYmd(lunar.getYear(), month, 30)
        except Exception:
            day = 29  # 小月无三十，降为廿九

    return (month, day) in _FESTIVAL_MAP


def get_lunar_desc(lunar_month: int, lunar_day: int) -> str:
    """获取佛菩萨圣诞日描述。

    Args:
        lunar_month: 农历月。
        lunar_day: 农历日。

    Returns:
        节日名称，非节日返回空字符串。
    """
    return _FESTIVAL_MAP.get((lunar_month, lunar_day), "")
