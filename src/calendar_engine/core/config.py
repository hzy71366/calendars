"""日历引擎 — 配置加载。

支持 `calendars` 字段（新）和 `zhai_types` 字段（旧，向后兼容）。
新增配置项全部在 dataclass 中有默认值。
"""

import dataclasses
from collections.abc import Mapping
from typing import Any
import yaml


@dataclasses.dataclass
class AppConfig:
    """应用程序配置（通用，不绑定具体日历）。"""

    config_version: int = 1
    calendar_name: str = "六斋日"
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"

    # 事件标题模板
    event_title: str = "{emoji} {name} · 农历{lunar}"
    event_description: str = (
        "农历{lunar}\n六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。"
    )

    # 提醒
    alarm_enabled: bool = True
    alarm_days_before: int = 1
    alarm_time: str = "09:00"

    # 图标
    emoji: str = "🔴"

    # 分类标签
    categories: tuple[str, ...] = ("佛教", "斋日")

    # 日历开关（key → bool）
    # 旧版 config.yaml 使用 zhai_types，新版使用 calendars
    calendars: dict[str, bool] = dataclasses.field(
        default_factory=lambda: {"liuzhai": True}
    )

    # 年份范围
    years_ahead: int = 5


def load_config(yaml_text: str) -> AppConfig:
    """从 YAML 文本加载配置。

    未知字段被忽略（向前兼容），缺失字段使用默认值。
    同时支持旧版 `zhai_types` 字段。
    """
    raw = yaml.safe_load(yaml_text)
    if raw is None:
        raw = {}

    kwargs: dict[str, Any] = {}

    # 直接映射字段
    for field in ("calendar_name", "language", "emoji", "config_version",
                   "timezone", "years_ahead"):
        kwargs[field] = raw.get(field, dataclasses.fields(AppConfig)[
            [f.name for f in dataclasses.fields(AppConfig)].index(field)
        ].default)

    # 标题/描述
    kwargs["event_title"] = raw.get(
        "event_title",
        "{emoji} {name} · 农历{lunar}",
    )
    kwargs["event_description"] = raw.get(
        "event_description",
        "农历{lunar}\n六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。",
    )

    # 提醒
    alarm = raw.get("alarm") or {}
    kwargs["alarm_enabled"] = alarm.get("enabled", True)
    kwargs["alarm_days_before"] = alarm.get("days_before", 1)
    kwargs["alarm_time"] = alarm.get("time", "09:00")

    # 分类
    cats = raw.get("categories", ("佛教", "斋日"))
    kwargs["categories"] = tuple(cats) if isinstance(cats, list) else cats

    # calendars: 新版用 calendars，旧版用 zhai_types
    calendars = raw.get("calendars") or {}
    if not isinstance(calendars, dict):
        calendars = {}
    # 旧版兼容
    zhai_types = raw.get("zhai_types") or {}
    if isinstance(zhai_types, dict) and "liuzhai" in zhai_types:
        calendars.setdefault("liuzhai", zhai_types["liuzhai"])
    # liuzhai 默认开启
    calendars.setdefault("liuzhai", True)
    kwargs["calendars"] = calendars

    # years_ahead 也从嵌套读取
    years = raw.get("years") or {}
    if isinstance(years, dict) and "ahead" in years:
        kwargs["years_ahead"] = years["ahead"]

    return AppConfig(**kwargs)
