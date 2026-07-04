"""日历引擎 — 六斋日判定模块。

六斋日定义（依据《增一阿含经》《毗婆沙论》）：
  每月固定六天：初八、十四、十五、二十三、二十九、三十
  小月（29天）无三十，调整为二十八、二十九

lunar-python 中闰月以负月份号表示（如 -6 = 闰六月），
本模块正确处理了这一情况。
"""

import datetime
from lunar_python import Lunar


_FIXED_LIUZHAI_DAYS = frozenset({8, 14, 15, 23})
"""每月固定不变的六斋日（农历日）"""


def _is_large_month(lunar_year: int, lunar_month: int) -> bool:
    """判断农历月是否为大月（30天）。

    lunar-python 的 fromYmd 在日期不存在时抛出异常，
    利用这一行为判断月份大小。闰月以负月份号表示，同样支持。
    """
    try:
        Lunar.fromYmd(lunar_year, lunar_month, 30)
        return True
    except Exception:
        return False


def is_liuzhai_day(solar_date: datetime.date) -> bool:
    """判断公历日期是否为六斋日。

    Args:
        solar_date: 公历日期。

    Returns:
        该日期是六斋日返回 True，否则 False。
    """
    dt = datetime.datetime.combine(solar_date, datetime.time.min)
    lunar = Lunar.fromDate(dt)

    year = lunar.getYear()
    month = lunar.getMonth()
    day = lunar.getDay()

    # 固定斋日：初八、十四、十五、廿三
    if day in _FIXED_LIUZHAI_DAYS:
        return True

    # 月尾斋日：廿九、三十（小月调整为廿八、廿九）
    if day in (28, 29):
        if _is_large_month(year, month):
            return day == 29  # 大月只有廿九是斋日
        return True  # 小月廿八和廿九都是斋日

    # 大月三十
    if day == 30 and _is_large_month(year, month):
        return True

    return False
