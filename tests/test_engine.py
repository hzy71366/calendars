"""Tests for Calendar Engine generator (registry-driven)."""

import datetime
import pytest
from pathlib import Path
from icalendar import Calendar
from calendar_engine.config import AppConfig
from calendar_engine.generator import (
    generate_all,
    collect_dates,
    build_calendar,
    _make_uid,
)
from calendar_engine.registry import get_calendar_type


_DEFAULT_CONFIG = AppConfig()


class TestEngineUID:
    """UID 稳定性"""

    def test_uid_format(self):
        """UID 格式正确"""
        uid = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert "@" in uid
        assert uid.endswith("@liuzhai-ics")

    def test_uid_deterministic(self):
        """相同日期生成相同 UID"""
        uid1 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        uid2 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert uid1 == uid2

    def test_uid_stability(self):
        """UID 与旧版本保持兼容（格式不变）"""
        uid = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert uid == "liuzhai-20260708@liuzhai-ics"


class TestEngineCollect:
    """日期收集"""

    def test_liuzhai_count(self):
        """六斋日收集数量在合理范围"""
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        assert len(dates) in range(70, 82)

    def test_liuzhai_structure(self):
        """收集结果结构正确"""
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        solar, desc = dates[0]
        assert isinstance(solar, datetime.date)
        assert isinstance(desc, str)
        assert "农历" in desc


class TestEngineGenerate:
    """完整生成验证"""

    def test_generate_liuzhai_file(self, tmp_path):
        """生成 liuzhai.ics 文件"""
        generate_all(_DEFAULT_CONFIG, output_dir=str(tmp_path), current_year=2026)
        ics_path = tmp_path / "liuzhai.ics"
        assert ics_path.exists()
        assert ics_path.stat().st_size > 0

    def test_generate_events_have_required_fields(self, tmp_path):
        """生成的事件包含所有必填字段"""
        generate_all(_DEFAULT_CONFIG, output_dir=str(tmp_path), current_year=2026)
        ics_path = tmp_path / "liuzhai.ics"
        cal = Calendar.from_ical(ics_path.read_bytes())
        for event in cal.walk():
            if event.name == "VEVENT":
                assert event.get("UID") is not None
                assert event.get("DTSTART") is not None
                assert event.get("DTSTAMP") is not None
                assert event.get("SUMMARY") is not None
                assert event.get("DESCRIPTION") is not None

    def test_generate_round_trip(self, tmp_path):
        """生成→解析→对比，事件数和 UID 不变"""
        # 只有一年，与旧版比较
        cfg = AppConfig(years_ahead=0)
        generate_all(cfg, output_dir=str(tmp_path), current_year=2026)
        ics_path = tmp_path / "liuzhai.ics"

        # 用旧版 generator 作为对照
        from liuzhai_ics.generator import (
            collect_liuzhai_dates as old_collect,
            build_liuzhai_calendar as old_build,
        )
        from liuzhai_ics.config import AppConfig as OldConfig
        old_dates = old_collect(2026, 2026)
        old_cal = old_build(old_dates, OldConfig())
        old_uids = {e.get("UID") for e in old_cal.walk() if e.name == "VEVENT"}

        # 新版
        new_cal = Calendar.from_ical(ics_path.read_bytes())
        new_uids = {e.get("UID") for e in new_cal.walk() if e.name == "VEVENT"}

        assert old_uids == new_uids
