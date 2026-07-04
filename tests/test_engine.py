"""Tests for Calendar Engine generator (registry-driven)."""

import datetime
import pytest
from pathlib import Path
from icalendar import Calendar
from calendar_engine.core.config import AppConfig
from calendar_engine.core.generator import (
    generate_all,
    collect_dates,
    build_calendar,
    _make_uid,
)
from calendar_engine.core.registry import get_calendar_type


_DEFAULT_CONFIG = AppConfig()


class TestEngineUID:
    """UID 稳定性"""

    def test_uid_format(self):
        uid = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert "@" in uid
        assert uid.endswith("@liuzhai-ics")

    def test_uid_deterministic(self):
        uid1 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        uid2 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert uid1 == uid2

    def test_uid_stability(self):
        uid = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert uid == "liuzhai-20260708@liuzhai-ics"


class TestEngineCollect:
    """日期收集"""

    def test_liuzhai_count(self):
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        assert len(dates) in range(70, 82)

    def test_liuzhai_structure(self):
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        solar, desc = dates[0]
        assert isinstance(solar, datetime.date)
        assert isinstance(desc, str)
        assert "农历" in desc


class TestEngineGenerate:
    """完整生成验证"""

    def test_generate_liuzhai_file(self, tmp_path):
        generate_all(_DEFAULT_CONFIG, output_dir=str(tmp_path), current_year=2026)
        ics_path = tmp_path / "liuzhai.ics"
        assert ics_path.exists()
        assert ics_path.stat().st_size > 0

    def test_generate_events_have_required_fields(self, tmp_path):
        generate_all(_DEFAULT_CONFIG, output_dir=str(tmp_path), current_year=2026)
        cal = Calendar.from_ical((tmp_path / "liuzhai.ics").read_bytes())
        for event in cal.walk():
            if event.name == "VEVENT":
                assert event.get("UID") is not None
                assert event.get("DTSTART") is not None
                assert event.get("DTSTAMP") is not None
                assert event.get("SUMMARY") is not None
                assert event.get("DESCRIPTION") is not None

    def test_generate_deterministic(self, tmp_path):
        """两次生成 UID 一致"""
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        cal = build_calendar(ct, dates, _DEFAULT_CONFIG)
        uids1 = {e.get("UID") for e in cal.walk() if e.name == "VEVENT"}

        cal2 = build_calendar(ct, dates, _DEFAULT_CONFIG)
        uids2 = {e.get("UID") for e in cal2.walk() if e.name == "VEVENT"}

        assert uids1 == uids2
