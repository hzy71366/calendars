"""Calendar Engine — 日历注册表。

所有日历类型在此注册，生成器通过遍历注册表来生成 ICS 文件。
"""
from __future__ import annotations

import datetime
from calendar_engine.types import CalendarType


def _make_lunar_description(solar_date: datetime.date) -> str:
    """生成农历日期描述字符串。"""
    import datetime as dt
    from lunar_python import Lunar

    d = dt.datetime.combine(solar_date, dt.time.min)
    lunar = Lunar.fromDate(d)
    month_str = lunar.getMonthInChinese()
    day_str = lunar.getDayInChinese()
    return f"农历{month_str}月{day_str}"


def _is_liuzhai(solar_date: datetime.date) -> bool:
    """六斋日判定（与 zhai_types.py 逻辑一致）"""
    import datetime as dt
    import calendar_engine.calendars.liuzhai as lz

    return lz.is_liuzhai_day(solar_date)


# ── 注册表 ──────────────────────────────────
CALENDAR_REGISTRY: dict[str, CalendarType] = {
    "liuzhai": CalendarType(
        key="liuzhai",
        name="六斋日",
        file_name="liuzhai.ics",
        uid_prefix="liuzhai",
        is_observance=_is_liuzhai,
        get_lunar_desc=_make_lunar_description,
        emoji="🔴",
        categories=("佛教", "斋日"),
    ),
}


def get_calendar_type(key: str) -> CalendarType | None:
    """按 key 获取日历类型。

    Args:
        key: 日历键名（如 "liuzhai"）。

    Returns:
        CalendarType 或 None（不存在时）。
    """
    return CALENDAR_REGISTRY.get(key)
