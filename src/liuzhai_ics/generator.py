"""ICS 日历生成器 — 基于 icalendar 库，符合 RFC 5545。

用法:
    >>> from liuzhai_ics.generator import collect_liuzhai_dates, build_liuzhai_calendar
    >>> dates = collect_liuzhai_dates(2026, 2027)
    >>> cal = build_liuzhai_calendar(dates)
    >>> cal.to_ical()
"""

import datetime
from icalendar import Calendar, Event
from liuzhai_ics.zhai_types import is_liuzhai_day
from lunar_python import Lunar


_UID_DOMAIN = "liuzhai-ics"
"""UID 域名后缀（永不改变）"""


def _make_lunar_description(solar_date: datetime.date) -> str:
    """生成农历日期描述字符串。

    Args:
        solar_date: 公历日期。

    Returns:
        农历描述，如 "农历八月初八"。
    """
    dt = datetime.datetime.combine(solar_date, datetime.time.min)
    lunar = Lunar.fromDate(dt)
    month_str = lunar.getMonthInChinese()
    day_str = lunar.getDayInChinese()
    return f"农历{month_str}月{day_str}"


def _make_uid(solar_date: datetime.date, prefix: str = "liuzhai") -> str:
    """生成稳定唯一的 UID。

    基于日期和前缀，在同一域名下永不改变。
    即使项目升级，相同日期生成相同 UID。

    Args:
        solar_date: 公历日期。
        prefix: UID 前缀（如 "liuzhai"）。

    Returns:
        UID 字符串，格式: {prefix}-{YYYYMMDD}@{domain}
    """
    date_str = solar_date.strftime("%Y%m%d")
    return f"{prefix}-{date_str}@{_UID_DOMAIN}"


def _make_event(
    solar_date: datetime.date,
    lunar_desc: str,
    uid_prefix: str = "liuzhai",
) -> Event:
    """创建单个 VEVENT。

    Args:
        solar_date: 公历日期（全天事件）。
        lunar_desc: 农历描述，如 "农历八月初八"。
        uid_prefix: UID 前缀。

    Returns:
        符合 RFC 5545 的 VEVENT 组件。
    """
    event = Event()
    event.add("uid", _make_uid(solar_date, uid_prefix))
    event.add("dtstart", solar_date)
    event.add("dtend", solar_date + datetime.timedelta(days=1))
    event.add("summary", f"🔴 六斋日 · {lunar_desc}")

    # DESCRIPTION 包含农历日期 + 说明（多行，RFC 5545 允许 \n）
    description = (
        f"{lunar_desc}\n"
        "六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。"
    )
    event.add("description", description)

    event.add("dtstamp", datetime.datetime.utcnow())
    return event


def collect_liuzhai_dates(
    start_year: int,
    end_year: int,
) -> list[tuple[datetime.date, str]]:
    """收集指定年份范围内所有六斋日的公历日期。

    遍历范围内的每一天，通过 is_liuzhai_day() 判定。

    Args:
        start_year: 起始年份（含）。
        end_year: 结束年份（含）。

    Returns:
        [(solar_date, lunar_description), ...] 列表，按日期排序。
    """
    results: list[tuple[datetime.date, str]] = []
    current = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)

    while current <= end:
        if is_liuzhai_day(current):
            desc = _make_lunar_description(current)
            results.append((current, desc))
        current += datetime.timedelta(days=1)

    return results


def build_liuzhai_calendar(
    dates: list[tuple[datetime.date, str]],
    calendar_name: str = "六斋日",
    calendar_desc: str = "佛教六斋日日历订阅",
    uid_prefix: str = "liuzhai",
) -> Calendar:
    """从六斋日日期列表构建 ICS Calendar。

    Args:
        dates: collect_liuzhai_dates() 的返回值。
        calendar_name: 日历名称（显示在订阅端）。
        calendar_desc: 日历描述。
        uid_prefix: UID 前缀（不同日历类型不同前缀）。

    Returns:
        可序列化的 Calendar 对象。
    """
    cal = Calendar()
    cal.add("prodid", f"-//{calendar_name}//{_UID_DOMAIN}//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", calendar_name)
    cal.add("x-wr-caldesc", calendar_desc)

    for solar_date, lunar_desc in dates:
        event = _make_event(solar_date, lunar_desc, uid_prefix)
        cal.add_component(event)

    return cal
