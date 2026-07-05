"""Calendar Engine — 日历注册表。

所有日历类型在此注册，生成器通过遍历注册表来生成 ICS 文件。
"""
from __future__ import annotations

import datetime
from calendar_engine.core.types import CalendarType


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
    """六斋日判定"""
    import calendar_engine.calendars.liuzhai as lz
    return lz.is_liuzhai_day(solar_date)


def _is_shizhai(solar_date: datetime.date) -> bool:
    """十斋日判定"""
    import calendar_engine.calendars.shizhai as sz
    return sz.is_observance(solar_date)


def _is_buddhist(solar_date: datetime.date) -> bool:
    """佛菩萨圣诞日判定"""
    import calendar_engine.calendars.buddhist as bd
    return bd.is_observance(solar_date)


def _buddhist_lunar_desc(solar_date: datetime.date) -> str:
    """佛菩萨圣诞日农历描述（直接返回节日名）"""
    import datetime as dt
    from lunar_python import Lunar
    import calendar_engine.calendars.buddhist as bd

    d = dt.datetime.combine(solar_date, dt.time.min)
    lunar = Lunar.fromDate(d)
    return bd.get_lunar_desc(lunar.getMonth(), lunar.getDay())


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
    "shizhai": CalendarType(
        key="shizhai",
        name="十斋日",
        file_name="shizhai.ics",
        uid_prefix="shizhai",
        is_observance=_is_shizhai,
        get_lunar_desc=_make_lunar_description,
        emoji="🪷",
        categories=("佛教", "斋日"),
    ),
    "buddhist": CalendarType(
        key="buddhist",
        name="佛菩萨圣诞",
        file_name="buddhist.ics",
        uid_prefix="buddhist",
        is_observance=_is_buddhist,
        get_lunar_desc=_buddhist_lunar_desc,
        emoji="🙏",
        categories=("佛教", "圣诞"),
    ),
}


def get_calendar_type(key: str) -> CalendarType | None:
    """按 key 获取日历类型。"""
    return CALENDAR_REGISTRY.get(key)
