"""Calendar Engine — Registry-driven ICS generator.

Iterates over CALENDAR_REGISTRY and generates ICS files
for each enabled calendar type.  The generator has NO
hardcoded knowledge of any specific calendar.
"""

import datetime
from pathlib import Path
from icalendar import Calendar, Event, Alarm
from calendar_engine.core.config import AppConfig, get_calendar_alarm
from calendar_engine.core.registry import CALENDAR_REGISTRY, CalendarType


_UID_DOMAIN = "liuzhai-ics"
"""UID 域名后缀（永不改变，向后兼容）"""


def _make_uid(
    solar_date: datetime.date,
    uid_prefix: str,
) -> str:
    """生成稳定唯一的 UID。

    基于日期和前缀，在同一域名下永不改变。
    """
    date_str = solar_date.strftime("%Y%m%d")
    return f"{uid_prefix}-{date_str}@{_UID_DOMAIN}"


def _make_event(
    solar_date: datetime.date,
    lunar_desc: str,
    cal_type: CalendarType,
    config: AppConfig,
) -> Event:
    """创建单个 VEVENT。

    Args:
        solar_date: 公历日期。
        lunar_desc: 农历描述。
        cal_type: 日历类型。
        config: 用户配置。

    Returns:
        RFC 5545 合规的 VEVENT。
    """
    solar_str = solar_date.strftime("%Y-%m-%d")
    emoji = config.emoji
    cal_cfg = config.calendars.get(cal_type.key)
    if isinstance(cal_cfg, dict):
        emoji = cal_cfg.get("emoji", emoji)
    emoji = emoji or "🔴"

    # 模板渲染：标题
    title = config.event_title
    title = title.replace("{emoji}", emoji)
    title = title.replace("{name}", cal_type.name)
    title = title.replace("{lunar}", lunar_desc)
    title = title.replace("{solar}", solar_str)

    # 模板渲染：描述
    desc = config.event_description
    desc = desc.replace("{lunar}", lunar_desc)
    desc = desc.replace("{solar}", solar_str)

    event = Event()
    event.add("uid", _make_uid(solar_date, cal_type.uid_prefix))
    event.add("dtstart", solar_date)
    event.add("dtend", solar_date + datetime.timedelta(days=1))
    event.add("summary", title)
    event.add("description", desc)
    event.add("dtstamp", datetime.datetime.utcnow())

    # VALARM — 按日历配置（优先于全局）
    alarm_cfg = get_calendar_alarm(config, cal_type.key)
    if alarm_cfg["enabled"]:
        alarm = Alarm()
        trigger_minutes = alarm_cfg["days_before"] * 24 * 60
        hour, minute = (alarm_cfg["time"].split(":") + ["0", "0"])[:2]
        trigger_minutes -= int(hour) * 60 + int(minute)
        alarm.add("trigger", datetime.timedelta(minutes=-trigger_minutes))
        alarm.add("action", "DISPLAY")
        alarm.add(
            "description",
            f"提醒：明天（{lunar_desc}）是{cal_type.name}",
        )
        event.add_component(alarm)

    return event


def collect_dates(
    cal_type: CalendarType,
    start_year: int,
    end_year: int,
) -> list[tuple[datetime.date, str]]:
    """收集某日历在指定年份范围内的所有纪念日。

    Args:
        cal_type: 日历类型。
        start_year: 起始年。
        end_year: 结束年。

    Returns:
        [(solar_date, lunar_desc), ...] 列表。
    """
    results: list[tuple[datetime.date, str]] = []
    current = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)

    while current <= end:
        if cal_type.is_observance(current):
            desc = cal_type.get_lunar_desc(current)
            results.append((current, desc))
        current += datetime.timedelta(days=1)

    return results


def build_calendar(
    cal_type: CalendarType,
    dates: list[tuple[datetime.date, str]],
    config: AppConfig,
) -> Calendar:
    """为某日历类型构建 ICS Calendar。

    Args:
        cal_type: 日历类型。
        dates: collect_dates() 返回值。
        config: 用户配置。

    Returns:
        可序列化的 Calendar 对象。
    """
    cal = Calendar()
    cal.add("prodid", f"-//{cal_type.name}//{_UID_DOMAIN}//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", cal_type.name)
    cal.add("x-wr-caldesc", f"{cal_type.name}日历 — 自动更新")

    for solar_date, lunar_desc in dates:
        event = _make_event(solar_date, lunar_desc, cal_type, config)
        cal.add_component(event)

    return cal


def generate_all(
    config: AppConfig,
    output_dir: str | Path = "docs",
    current_year: int | None = None,
) -> list[Path]:
    """遍历注册表，为所有启用的日历生成 ICS 文件。

    Args:
        config: 用户配置。
        output_dir: 输出目录。
        current_year: 起始年份（默认当前年）。

    Returns:
        生成的 ICS 文件路径列表。
    """
    if current_year is None:
        current_year = datetime.datetime.now().year
    end_year = current_year + config.years_ahead

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []

    for key, cal_type in CALENDAR_REGISTRY.items():
        if not config.calendars.get(key, True):
            continue

        dates = collect_dates(cal_type, current_year, end_year)
        cal = build_calendar(cal_type, dates, config)

        file_path = output_path / cal_type.file_name
        with open(file_path, "wb") as f:
            f.write(cal.to_ical())

        generated.append(file_path)
        event_count = len(dates)
        print(f"  ✅ {cal_type.file_name} — {event_count} 个事件")

    return generated
