"""ICS 日历生成器 — 基于 icalendar 库，符合 RFC 5545。

用法:
    >>> from liuzhai_ics.config import AppConfig, load_config
    >>> from liuzhai_ics.generator import collect_liuzhai_dates, build_liuzhai_calendar
    >>> cfg = load_config(open("config.yaml").read())
    >>> dates = collect_liuzhai_dates(2026, 2026 + cfg.years_ahead)
    >>> cal = build_liuzhai_calendar(dates, cfg)
    >>> cal.to_ical()
"""

import datetime
from icalendar import Calendar, Event, Alarm
from liuzhai_ics.zhai_types import is_liuzhai_day
from liuzhai_ics.config import AppConfig, render_title, render_description
from lunar_python import Lunar


_UID_DOMAIN = "liuzhai-ics"
"""UID 域名后缀（永不改变）"""


def _make_lunar_description(solar_date: datetime.date) -> str:
    """生成农历日期描述字符串。"""
    dt = datetime.datetime.combine(solar_date, datetime.time.min)
    lunar = Lunar.fromDate(dt)
    month_str = lunar.getMonthInChinese()
    day_str = lunar.getDayInChinese()
    return f"农历{month_str}月{day_str}"


def _make_uid(solar_date: datetime.date, prefix: str = "liuzhai") -> str:
    """生成稳定唯一的 UID。"""
    date_str = solar_date.strftime("%Y%m%d")
    return f"{prefix}-{date_str}@{_UID_DOMAIN}"


def _make_event(
    solar_date: datetime.date,
    lunar_desc: str,
    config: AppConfig,
    uid_prefix: str = "liuzhai",
) -> Event:
    """创建单个 VEVENT，应用配置模板。"""
    solar_str = solar_date.strftime("%Y-%m-%d")
    cal_name = config.calendar_name

    # 标题和描述使用模板渲染
    title = render_title(
        config.event_title,
        emoji=config.emoji,
        name=cal_name,
        lunar=lunar_desc,
        solar=solar_str,
    )
    description = render_description(
        config.event_description,
        lunar=lunar_desc,
        solar=solar_str,
    )

    event = Event()
    event.add("uid", _make_uid(solar_date, uid_prefix))
    event.add("dtstart", solar_date)
    event.add("dtend", solar_date + datetime.timedelta(days=1))
    event.add("summary", title)
    event.add("description", description)
    event.add("dtstamp", datetime.datetime.utcnow())

    # VALARM 提醒
    if config.alarm_enabled:
        alarm = Alarm()
        # 提前 N 天 + 指定时刻
        trigger_minutes = config.alarm_days_before * 24 * 60
        hour, minute = (config.alarm_time.split(":") + ["0", "0"])[:2]
        trigger_minutes -= int(hour) * 60 + int(minute)
        alarm.add("trigger", datetime.timedelta(minutes=-trigger_minutes))
        alarm.add("action", "DISPLAY")
        alarm.add("description", f"提醒：明天（{lunar_desc}）是{cal_name}")
        event.add_component(alarm)

    return event


def collect_liuzhai_dates(
    start_year: int,
    end_year: int,
) -> list[tuple[datetime.date, str]]:
    """收集指定年份范围内所有六斋日的公历日期。"""
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
    config: AppConfig,
    uid_prefix: str = "liuzhai",
) -> Calendar:
    """从日期列表和配置构建 ICS Calendar。

    Args:
        dates: collect_liuzhai_dates() 的返回值。
        config: 用户配置。
        uid_prefix: UID 前缀。

    Returns:
        可序列化的 Calendar 对象。
    """
    cal = Calendar()
    cal.add("prodid", f"-//{config.calendar_name}//{_UID_DOMAIN}//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", config.calendar_name)
    cal.add(
        "x-wr-caldesc",
        f"{config.calendar_name}日历订阅 — 自动更新，永久可用",
    )

    for solar_date, lunar_desc in dates:
        event = _make_event(solar_date, lunar_desc, config, uid_prefix)
        cal.add_component(event)

    return cal
