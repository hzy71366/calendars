#!/usr/bin/env python3
"""Calendar Engine — 多日历 ICS 生成器入口脚本。

读取 config.yaml，遍历 CALENDAR_REGISTRY 生成所有启用的 ICS 文件。

用法:
    python scripts/generate_ics.py
    python scripts/generate_ics.py --output-dir ./dist
"""

import os
import sys
import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calendar Engine — ICS 日历生成器")
    parser.add_argument(
        "--config",
        default=os.path.join(REPO_ROOT, "config.yaml"),
        help="配置文件路径",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(REPO_ROOT, "docs"),
        help="输出目录（默认: docs/）",
    )
    args = parser.parse_args()

    # 加载配置
    from calendar_engine.core.config import load_config
    from calendar_engine.core.generator import generate_all
    from calendar_engine.core.registry import CALENDAR_REGISTRY

    config_text = open(args.config, "r", encoding="utf-8").read()
    cfg = load_config(config_text)

    now = datetime.datetime.now()
    print(f"📅 Calendar Engine — {now.year} ~ {now.year + cfg.years_ahead}")
    print(f"📋 配置: {args.config}")
    print(f"🔤 语言: {cfg.language}")
    print()

    enabled = [k for k, v in cfg.calendars.items() if v and k in CALENDAR_REGISTRY]
    if not enabled:
        print("❌ 未启用任何日历类型")
        sys.exit(1)

    print(f"📋 启用的日历: {', '.join(enabled)}")

    generated = generate_all(cfg, output_dir=args.output_dir)
    print(f"\n✅ 共生成 {len(generated)} 个 ICS 文件")
    print(f"📁 输出目录: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
