"""日历引擎 — 配置加载。

支持 `calendars` 字段按日历独立配置（含 alarm），
同时兼容旧版 `zhai_types` 字段。
"""

import dataclasses
from typing import Any
import yaml


_DEFAULT_TITLE = "{emoji} {name} · {lunar}"
_DEFAULT_DESC = "{lunar}\n六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。"


@dataclasses.dataclass
class AppConfig:
    """应用程序配置。"""

    config_version: int = 1
    calendar_name: str = "六斋日"
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"
    event_title: str = _DEFAULT_TITLE
    event_description: str = _DEFAULT_DESC

    # 全局提醒（当日历未指定自己的提醒时使用）
    alarm_enabled: bool = True
    alarm_days_before: int = 1
    alarm_time: str = "09:00"

    emoji: str = "🔴"
    categories: tuple[str, ...] = ("佛教", "斋日")

    # 日历配置（key → bool 或 dict）
    # dict 可含: enabled, alarm.enabled, alarm.days_before, alarm.time
    calendars: dict[str, Any] = dataclasses.field(
        default_factory=lambda: {"liuzhai": True}
    )

    years_ahead: int = 10


def _get_calendar_value(raw: dict, key: str, default: Any) -> dict | bool:
    """从 calendars 字典中获取某日历的配置值。"""
    cal_section = raw.get("calendars") or {}
    if key in cal_section:
        return cal_section[key]
    # 旧版兼容
    old = raw.get("zhai_types") or {}
    if key in old:
        return old[key]
    return default


def load_config(yaml_text: str) -> AppConfig:
    """从 YAML 文本加载配置。"""
    raw = yaml.safe_load(yaml_text)
    if raw is None:
        raw = {}

    kwargs: dict[str, Any] = {}

    # 直接映射
    for field in ("calendar_name", "language", "emoji", "config_version",
                   "timezone", "years_ahead"):
        kwargs[field] = raw.get(field, getattr(AppConfig, field, None))

    # 标题/描述
    kwargs["event_title"] = raw.get("event_title", _DEFAULT_TITLE)
    kwargs["event_description"] = raw.get("event_description", _DEFAULT_DESC)

    # 全局提醒
    alarm = raw.get("alarm") or {}
    kwargs["alarm_enabled"] = alarm.get("enabled", True)
    kwargs["alarm_days_before"] = alarm.get("days_before", 1)
    kwargs["alarm_time"] = alarm.get("time", "09:00")

    # 分类
    cats = raw.get("categories", ("佛教", "斋日"))
    kwargs["categories"] = tuple(cats) if isinstance(cats, list) else cats

    # calendars — 新版支持 dict 结构，旧版支持 bool 和 zhai_types
    raw_cal = raw.get("calendars") or {}
    if not isinstance(raw_cal, dict):
        raw_cal = {}

    # 兼容旧版 zhai_types
    old_zt = raw.get("zhai_types") or {}
    if isinstance(old_zt, dict):
        for k, v in old_zt.items():
            raw_cal.setdefault(k, v)

    # 默认开启 liuzhai
    raw_cal.setdefault("liuzhai", True)

    # 规范化：bool → {enabled: bool}
    calendars: dict[str, Any] = {}
    for k, v in raw_cal.items():
        if isinstance(v, bool):
            calendars[k] = v
        elif isinstance(v, dict):
            calendars[k] = v
        else:
            calendars[k] = bool(v)
    kwargs["calendars"] = calendars

    # years_ahead
    years = raw.get("years") or {}
    if isinstance(years, dict) and "ahead" in years:
        kwargs["years_ahead"] = years["ahead"]

    return AppConfig(**kwargs)


def get_calendar_alarm(config: AppConfig, calendar_key: str) -> dict:
    """获取某日历的有效提醒配置。

    优先使用日历自己的 alarm 配置，没有则回退到全局。
    返回格式: {"enabled": bool, "days_before": int, "time": str}

    Args:
        config: 全局配置。
        calendar_key: 日历键名（如 "liuzhai"、"shizhai"）。

    Returns:
        该日历的有效提醒配置字典。
    """
    cal_cfg = config.calendars.get(calendar_key)

    # dict 结构：检查 alarm 子项
    if isinstance(cal_cfg, dict):
        alarm = cal_cfg.get("alarm") or {}
        if isinstance(alarm, dict):
            return {
                "enabled": alarm.get("enabled", config.alarm_enabled),
                "days_before": alarm.get("days_before", config.alarm_days_before),
                "time": alarm.get("time", config.alarm_time),
            }

    # 回退到全局
    return {
        "enabled": config.alarm_enabled,
        "days_before": config.alarm_days_before,
        "time": config.alarm_time,
    }
