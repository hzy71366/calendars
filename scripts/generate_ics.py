#!/usr/bin/env python3
"""六斋日 ICS 日历生成器 — 入口脚本。

读取 config.yaml，生成 ICS 文件到 docs/ 目录。

用法:
    python scripts/generate_ics.py              # 按 config.yaml 生成
    python scripts/generate_ics.py --output custom.ics  # 输出到自定义路径
"""

import os
import sys
import argparse

# 确保能找到 src/ 包
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))


def main():
    parser = argparse.ArgumentParser(description="六斋日 ICS 日历生成器")
    parser.add_argument(
        "--config",
        default=os.path.join(REPO_ROOT, "config.yaml"),
        help="配置文件路径（默认: config.yaml）",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(REPO_ROOT, "docs", "liuzhai.ics"),
        help="输出 ICS 文件路径（默认: docs/liuzhai.ics）",
    )
    args = parser.parse_args()

    # 加载配置
    from liuzhai_ics.config import load_config
    from liuzhai_ics.generator import collect_liuzhai_dates, build_liuzhai_calendar

    config_text = open(args.config, "r", encoding="utf-8").read()
    cfg = load_config(config_text)

    # 计算年份范围
    import datetime
    current_year = datetime.datetime.now().year
    end_year = current_year + cfg.years_ahead

    print(f"📅 生成: {current_year} ~ {end_year}")
    print(f"📋 日历: {cfg.calendar_name}")
    print(f"🔤 语言: {cfg.language}")

    # 收集日期并生成
    dates = collect_liuzhai_dates(current_year, end_year)
    cal = build_liuzhai_calendar(dates, cfg)

    # 写入文件
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "wb") as f:
        f.write(cal.to_ical())

    event_count = sum(1 for _ in cal.walk() if _.name == "VEVENT")
    file_size = os.path.getsize(args.output)
    print(f"✅ 生成完成: {args.output}")
    print(f"   • {len(dates)} 个事件")
    print(f"   • {file_size:,} bytes")


if __name__ == "__main__":
    main()
