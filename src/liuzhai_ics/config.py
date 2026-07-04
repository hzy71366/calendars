"""配置加载与模板渲染。

从 config.yaml 加载用户配置，支持模板变量替换。
新增配置项全部在 dataclass 中有默认值，确保向前兼容。
"""

import dataclasses
from typing import Any
import yaml


@dataclasses.dataclass
class AppConfig:
    """应用程序配置。

    所有字段都有默认值，新增字段只需在 dataclass 中添加，
    旧版 config.yaml 不包含该字段时自动使用默认值。
    """

    # 版本（仅用于脚本判断格式兼容性）
    config_version: int = 1

    # 日历元信息
    calendar_name: str = "六斋日"
    timezone: str = "Asia/Shanghai"

    # 语言
    language: str = "zh-CN"  # zh-CN / en / bilingual

    # 事件标题模板（可用变量: {emoji} {name} {lunar} {solar}）
    event_title: str = "{emoji} {name} · 农历{lunar}"

    # 事件描述模板（可用变量: {lunar} {solar}）
    event_description: str = "农历{lunar}\n六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。"

    # 提醒
    alarm_enabled: bool = True
    alarm_days_before: int = 1
    alarm_time: str = "09:00"

    # 图标
    emoji: str = "🔴"

    # 分类标签
    categories: tuple[str, ...] = ("佛教", "斋日")

    # 斋日类型
    zhai_types: dict[str, bool] = dataclasses.field(
        default_factory=lambda: {"liuzhai": True}
    )

    # 年份范围
    years_ahead: int = 5


def load_config(yaml_text: str) -> AppConfig:
    """从 YAML 文本加载配置。

    未知字段被忽略（向前兼容），缺失字段使用默认值。

    Args:
        yaml_text: config.yaml 文件内容。

    Returns:
        AppConfig 实例。
    """
    raw = yaml.safe_load(yaml_text)
    if raw is None:
        raw = {}

    # 提取已知字段，忽略未知（向前兼容）
    known_fields = {f.name for f in dataclasses.fields(AppConfig)}
    kwargs: dict[str, Any] = {}

    for field in known_fields:
        if field == "zhai_types":
            # 特殊处理：从嵌套结构提取
            zt = raw.get("zhai_types", {})
            if isinstance(zt, dict):
                kwargs["zhai_types"] = zt
            continue
        if field == "categories":
            cats = raw.get("categories", ("佛教", "斋日"))
            if isinstance(cats, list):
                kwargs["categories"] = tuple(cats)
            continue
        if field == "years_ahead":
            years = raw.get("years", {})
            if isinstance(years, dict):
                kwargs["years_ahead"] = years.get("ahead", 5)
            continue
        if field == "calendar_name":
            kwargs["calendar_name"] = raw.get("calendar_name", "六斋日")
            continue
        if field == "language":
            kwargs["language"] = raw.get("language", "zh-CN")
            continue
        if field == "event_title":
            kwargs["event_title"] = raw.get("event_title", "{emoji} {name} · 农历{lunar}")
            continue
        if field == "event_description":
            kwargs["event_description"] = raw.get(
                "event_description",
                "农历{lunar}\n六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。",
            )
            continue
        if field == "emoji":
            kwargs["emoji"] = raw.get("emoji", "🔴")
            continue
        if field == "alarm_enabled":
            alarm = raw.get("alarm", {}) or {}
            kwargs["alarm_enabled"] = alarm.get("enabled", True)
            continue
        if field == "alarm_days_before":
            alarm = raw.get("alarm", {}) or {}
            kwargs["alarm_days_before"] = alarm.get("days_before", 1)
            continue
        if field == "alarm_time":
            alarm = raw.get("alarm", {}) or {}
            kwargs["alarm_time"] = alarm.get("time", "09:00")
            continue

    return AppConfig(**kwargs)


def _substitute(template: str, **variables: str) -> str:
    """替换模板中的 {variable} 占位符。

    Args:
        template: 包含 {var} 占位符的模板字符串。
        **variables: 变量名 → 值的映射。

    Returns:
        替换后的字符串。
    """
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", value)
    return result


def render_title(
    template: str,
    emoji: str = "",
    name: str = "",
    lunar: str = "",
    solar: str = "",
) -> str:
    """渲染事件标题。

    Args:
        template: 标题模板。
        emoji: 图标。
        name: 日历名称。
        lunar: 农历描述。
        solar: 公历日期字符串。

    Returns:
        渲染后的标题。
    """
    return _substitute(template, emoji=emoji, name=name, lunar=lunar, solar=solar)


def render_description(
    template: str,
    lunar: str = "",
    solar: str = "",
) -> str:
    """渲染事件描述。

    Args:
        template: 描述模板。
        lunar: 农历描述。
        solar: 公历日期字符串。

    Returns:
        渲染后的描述。
    """
    return _substitute(template, lunar=lunar, solar=solar)
