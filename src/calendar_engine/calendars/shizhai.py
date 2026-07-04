"""十斋日判定模块。

十斋日定义（源自《地藏菩萨本愿经》）：
  每月初一、初八、十四、十五、十八、二十三、二十四、二十八、二十九、三十
  小月（29天）无三十
"""

import datetime
from lunar_python import Lunar


_FIXED_SHIJAI_DAYS = frozenset({1, 8, 14, 15, 18, 23, 24, 28, 29})
"""每月固定不变的十斋日（农历日），含廿八廿九"""


def _is_large_month(lunar_year: int, lunar_month: int) -> bool:
    try:
        Lunar.fromYmd(lunar_year, lunar_month, 30)
        return True
    except Exception:
        return False


def is_observance(solar_date: datetime.date) -> bool:
    """判断公历日期是否为十斋日。

    Args:
        solar_date: 公历日期。

    Returns:
        该日期是十斋日返回 True，否则 False。
    """
    dt = datetime.datetime.combine(solar_date, datetime.time.min)
    lunar = Lunar.fromDate(dt)

    year = lunar.getYear()
    month = lunar.getMonth()
    day = lunar.getDay()

    # 固定斋日
    if day in _FIXED_SHIJAI_DAYS:
        return True

    # 大月三十
    if day == 30 and _is_large_month(year, month):
        return True

    return False


def get_lunar_desc(solar_date: datetime.date) -> str:
    """获取农历描述。"""
    import datetime as dt
    d = dt.datetime.combine(solar_date, dt.time.min)
    lunar = Lunar.fromDate(d)
    month_str = lunar.getMonthInChinese()
    day_str = lunar.getDayInChinese()
    return f"农历{month_str}月{day_str}"
