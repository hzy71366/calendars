#!/usr/bin/env python3
"""六斋日 ICS 日历生成器 — 入口脚本。

读取 config.yaml，根据 zhai_types 配置生成对应的 ICS 文件。

用法:
    python scripts/generate_ics.py                              # 完整生成
    python scripts/generate_ics.py --output-dir ./dist          # 自定义输出目录
"""

import os
import sys
import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))


# 日历类型注册表
# 新增日历类型只需在 ZHAI_TYPES 中注册，config.yaml 中开启即可
ZHAI_TYPES = {
    "liuzhai": {
        "file": "liuzhai.ics",
        "get_func": lambda: __import__("liuzhai_ics.zhai_types").zhai_types.is_liuzhai_day,
        "uid_prefix": "liuzhai",
    },
}


def generate_calendar(
    config_path: str,
    output_dir: str,
    zhai_type_key: str,
) -> str:
    """生成单个日历的 ICS 文件。

    Args:
        config_path: config.yaml 路径。
        output_dir: 输出目录。
        zhai_type_key: 日历类型键（如 "liuzhai"）。

    Returns:
        生成的文件路径。
    """
    from liuzhai_ics.config import load_config
    from liuzhai_ics.generator import build_liuzhai_calendar

    config_text = open(config_path, "r", encoding="utf-8").read()
    cfg = load_config(config_text)

    zhai_cfg = ZHAI_TYPES.get(zhai_type_key)
    if zhai_cfg is None:
        raise ValueError(f"Unknown zhai type: {zhai_type_key}")

    # 收集日期
    current_year = datetime.datetime.now().year
    end_year = current_year + cfg.years_ahead

    dates = []
    d = datetime.date(current_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    is_func = zhai_cfg["get_func"]()

    while d <= end:
        if is_func(d):
            from liuzhai_ics.generator import _make_lunar_description
            dates.append((d, _make_lunar_description(d)))
        d += datetime.timedelta(days=1)

    # 生成日历
    cal = build_liuzhai_calendar(dates, cfg, uid_prefix=zhai_cfg["uid_prefix"])

    # 写入
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, zhai_cfg["file"])
    with open(output_path, "wb") as f:
        f.write(cal.to_ical())

    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="六斋日 ICS 日历生成器")
    parser.add_argument(
        "--config",
        default=os.path.join(REPO_ROOT, "config.yaml"),
        help="配置文件路径",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(REPO_ROOT, "docs"),
        help="输出目录",
    )
    args = parser.parse_args()

    config_text = open(args.config, "r", encoding="utf-8").read()
    from liuzhai_ics.config import load_config
    cfg = load_config(config_text)

    enabled_types = [k for k, v in cfg.zhai_types.items() if v]
    if not enabled_types:
        print("❌ config.yaml 中未启用任何日历类型")
        sys.exit(1)

    print(f"📅 年份范围: {datetime.datetime.now().year} ~ "
          f"{datetime.datetime.now().year + cfg.years_ahead}")
    print(f"📋 日历名称: {cfg.calendar_name}")
    print(f"🔤 语言: {cfg.language}")
    print(f"🔔 VALARM 提醒: {'开启' if cfg.alarm_enabled else '关闭'}")
    print()

    total_events = 0
    for zhai_type in enabled_types:
        output = generate_calendar(args.config, args.output_dir, zhai_type)
        # 统计事件数
        from icalendar import Calendar
        with open(output, "rb") as f:
            cal = Calendar.from_ical(f.read())
        event_count = sum(1 for _ in cal.walk() if _.name == "VEVENT")
        file_size = os.path.getsize(output)
        total_events += event_count
        print(f"  ✅ {os.path.basename(output)}")
        print(f"     • {event_count} 个事件")
        print(f"     • {file_size:,} bytes")

    print(f"\n✅ 共生成 {len(enabled_types)} 个日历文件，{total_events} 个事件")
    print(f"📁 输出目录: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
