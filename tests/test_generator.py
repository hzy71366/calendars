"""Tests for ICS generator — RFC 5545 compliance and round-trip safety."""

import datetime
import pytest
from icalendar import Calendar
from calendar_engine.core.generator import (
    collect_dates,
    build_calendar,
    generate_all,
    _make_uid,
)
from calendar_engine.core.config import AppConfig
from calendar_engine.core.registry import get_calendar_type


_DEFAULT_CONFIG = AppConfig()
_LIUZHAI_TYPE = get_calendar_type("liuzhai")


class TestUID:
    """UID 稳定性"""

    def test_uid_format(self):
        """UID 包含 @ 和域名"""
        uid = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert "@" in uid
        assert uid.endswith("@liuzhai-ics")

    def test_uid_deterministic(self):
        """相同日期生成相同 UID"""
        uid1 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        uid2 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        assert uid1 == uid2

    def test_uid_different_dates_different(self):
        """不同日期生成不同 UID"""
        uid1 = _make_uid(datetime.date(2026, 7, 8), "liuzhai")
        uid2 = _make_uid(datetime.date(2026, 7, 9), "liuzhai")
        assert uid1 != uid2


class TestICSCompliance:
    """RFC 5545 合规性"""

    @pytest.fixture(scope="class")
    def events(self):
        """生成2026~2027年ICS供测试"""
        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2027)
        cal = build_calendar(ct, dates, _DEFAULT_CONFIG)
        return [c for c in cal.walk() if c.name == 'VEVENT']

    def test_event_count_reasonable(self, events):
        """事件数量在合理范围内"""
        assert len(events) in range(140, 170)

    def test_each_event_has_uid(self, events):
        for e in events:
            assert e.get('UID') is not None

    def test_each_event_has_dtstart(self, events):
        for e in events:
            assert e.get('DTSTART') is not None

    def test_each_event_has_dtstamp(self, events):
        for e in events:
            dtstamp = e.get('DTSTAMP')
            assert dtstamp is not None
            assert bool(dtstamp) is True

    def test_each_event_has_summary(self, events):
        for e in events:
            assert e.get('SUMMARY') is not None

    def test_each_event_has_description(self, events):
        for e in events:
            desc = e.get('DESCRIPTION')
            assert desc is not None
            assert "六斋日" in str(desc)

    def test_calendar_has_calscale(self, events):
        """取第一个事件的 Calendar 检查 CALSCALE"""
        # 通过 generate_all 获取完整的 Calendar 对象
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmp:
            generate_all(_DEFAULT_CONFIG, output_dir=tmp, current_year=2026)
            cal = Calendar.from_ical(open(os.path.join(tmp, "liuzhai.ics"), "rb").read())
            assert cal.get('CALSCALE') == 'GREGORIAN'

    def test_dtstart_is_date(self, events):
        for e in events:
            dtstart = e.get('DTSTART')
            assert not hasattr(dtstart.dt, 'hour')

    def test_uid_uniqueness(self, events):
        uids = [e.get('UID') for e in events]
        assert len(uids) == len(set(uids))


class TestRoundTrip:
    """生成→解析→验证"""

    def test_round_trip_preserves_uids(self, tmp_path):
        """序列化后重新解析，UID不变"""
        cfg = AppConfig(years_ahead=0)
        generate_all(cfg, output_dir=str(tmp_path), current_year=2026)

        ct = get_calendar_type("liuzhai")
        dates = collect_dates(ct, 2026, 2026)
        original_cal = build_calendar(ct, dates, cfg)
        original_uids = {e.get('UID') for e in original_cal.walk() if e.name == 'VEVENT'}

        parsed = Calendar.from_ical(open(tmp_path / "liuzhai.ics", "rb").read())
        parsed_uids = {e.get('UID') for e in parsed.walk() if e.name == 'VEVENT'}
        assert original_uids == parsed_uids

    def test_ics_byte_order(self, tmp_path):
        """to_ical() 返回合法 ICS"""
        generate_all(_DEFAULT_CONFIG, output_dir=str(tmp_path), current_year=2026)
        ics_bytes = (tmp_path / "liuzhai.ics").read_bytes()
        assert isinstance(ics_bytes, bytes)
        assert len(ics_bytes) > 0
        assert ics_bytes.startswith(b'BEGIN:VCALENDAR')
