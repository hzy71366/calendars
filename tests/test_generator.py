"""Tests for ICS generator — RFC 5545 compliance and round-trip safety."""

import datetime
import pytest
from icalendar import Calendar
from liuzhai_ics.generator import (
    collect_liuzhai_dates,
    build_liuzhai_calendar,
    _make_lunar_description,
    _make_uid,
)
from liuzhai_ics.config import AppConfig


_DEFAULT_CONFIG = AppConfig()
"""默认配置用于测试"""


# 每个农历月恰好6天，一年12~13个月，太阳年约72~78天
_REASONABLE_RANGE = range(70, 82)


# ──────────────────────────────────────────────
# 辅助函数测试
# ──────────────────────────────────────────────

class TestHelperFunctions:
    """日期收集与描述生成"""

    def test_collect_dates_reasonable_count(self):
        """一年内斋日数量在合理范围内"""
        dates = collect_liuzhai_dates(2026, 2026)
        assert len(dates) in _REASONABLE_RANGE

    def test_collect_dates_multi_year(self):
        """跨多年收集数量合理"""
        dates = collect_liuzhai_dates(2026, 2028)
        assert len(dates) in range(210, 250)  # ~72-78 * 3

    def test_collect_dates_structure(self):
        """返回值格式 = [(date, lunar_desc), ...]"""
        dates = collect_liuzhai_dates(2026, 2026)
        solar, desc = dates[0]
        assert isinstance(solar, datetime.date)
        assert isinstance(desc, str)
        assert "农历" in desc

    def test_lunar_description(self):
        """农历描述格式"""
        d = datetime.date(2026, 9, 18)  # 八月初八
        desc = _make_lunar_description(d)
        assert "八月初八" in desc
        assert "农历" in desc


# ──────────────────────────────────────────────
# UID 稳定性
# ──────────────────────────────────────────────

class TestUID:
    """UID 基于日期和域名的哈希，永不改变"""

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


# ──────────────────────────────────────────────
# ICS 合规（RFC 5545）
# ──────────────────────────────────────────────

class TestICSCompliance:
    """RFC 5545 合规性 — 使用小范围数据集避免超时"""

    @pytest.fixture(scope="class")
    def calendar(self):
        """生成2026~2027年ICS供测试"""
        dates = collect_liuzhai_dates(2026, 2027)
        return build_liuzhai_calendar(dates, _DEFAULT_CONFIG)

    @pytest.fixture
    def events(self, calendar):
        """提取所有VEVENT"""
        return [c for c in calendar.walk() if c.name == 'VEVENT']

    def test_calendar_has_components(self, calendar):
        """Calendar包含正确的基本组件"""
        assert calendar.get('VERSION') == '2.0'
        assert calendar.get('PRODID') is not None

    def test_event_count_reasonable(self, events):
        """事件数量在合理范围内"""
        assert len(events) in range(140, 170)  # ~72-78 * 2

    def test_each_event_has_uid(self, events):
        """每个VEVENT必须有UID"""
        for e in events:
            assert e.get('UID') is not None, f"Event missing UID"

    def test_each_event_has_dtstart(self, events):
        """每个VEVENT必须有DTSTART"""
        for e in events:
            assert e.get('DTSTART') is not None

    def test_each_event_has_dtstamp(self, events):
        """每个VEVENT必须有DTSTAMP"""
        for e in events:
            dtstamp = e.get('DTSTAMP')
            assert dtstamp is not None
            assert bool(dtstamp) is True

    def test_each_event_has_summary(self, events):
        """每个VEVENT必须有SUMMARY"""
        for e in events:
            assert e.get('SUMMARY') is not None

    def test_each_event_has_description(self, events):
        """每个VEVENT必须有DESCRIPTION"""
        for e in events:
            desc = e.get('DESCRIPTION')
            assert desc is not None
            assert "六斋日" in str(desc)

    def test_description_multiline(self, events):
        """DESCRIPTION 包含多行文本"""
        for e in events:
            desc = str(e.get('DESCRIPTION'))
            assert '\\n' in desc or '\n' in desc, "DESCRIPTION应为多行"

    def test_calendar_has_calscale(self, calendar):
        """Calendar 包含 CALSCALE:GREGORIAN"""
        assert calendar.get('CALSCALE') == 'GREGORIAN'

    def test_dtstart_is_date(self, events):
        """DTSTART是全天事件（VALUE=DATE）"""
        for e in events:
            dtstart = e.get('DTSTART')
            assert not hasattr(dtstart.dt, 'hour'), f"DTSTART不应包含时间"

    def test_dtend_is_dtstart_plus_one(self, events):
        """DTEND = DTSTART + 1天（全天事件约定）"""
        for e in events:
            dtstart = e.get('DTSTART').dt
            dtend = e.get('DTEND').dt
            assert dtend == dtstart + datetime.timedelta(days=1)

    def test_uid_uniqueness(self, events):
        """所有UID唯一"""
        uids = [e.get('UID') for e in events]
        assert len(uids) == len(set(uids))


# ──────────────────────────────────────────────
# Round-trip 验证（仅单年，性能考虑）
# ──────────────────────────────────────────────

class TestRoundTrip:
    """生成→解析→验证"""

    def test_round_trip_preserves_count(self):
        """序列化后重新解析，事件数不变"""
        dates = collect_liuzhai_dates(2026, 2026)
        cal = build_liuzhai_calendar(dates, _DEFAULT_CONFIG)
        ics_bytes = cal.to_ical()

        parsed = Calendar.from_ical(ics_bytes)
        events = [c for c in parsed.walk() if c.name == 'VEVENT']
        assert len(events) == len(dates)

    def test_round_trip_preserves_uids(self):
        """序列化后重新解析，UID不变"""
        dates = collect_liuzhai_dates(2026, 2026)
        cal = build_liuzhai_calendar(dates, _DEFAULT_CONFIG)
        ics_bytes = cal.to_ical()

        parsed = Calendar.from_ical(ics_bytes)
        original_uids = {e.get('UID') for e in cal.walk() if e.name == 'VEVENT'}
        parsed_uids = {e.get('UID') for e in parsed.walk() if e.name == 'VEVENT'}
        assert original_uids == parsed_uids

    def test_round_trip_preserves_dates(self):
        """序列化后重新解析，日期不变"""
        dates = collect_liuzhai_dates(2026, 2026)
        cal = build_liuzhai_calendar(dates, _DEFAULT_CONFIG)
        ics_bytes = cal.to_ical()

        parsed = Calendar.from_ical(ics_bytes)
        parsed_dates = {
            e.get('DTSTART').dt for e in parsed.walk() if e.name == 'VEVENT'
        }
        original_dates = {d for d, _ in dates}
        assert parsed_dates == original_dates

    def test_ics_byte_order(self):
        """to_ical() 返回合法 ICS"""
        dates = collect_liuzhai_dates(2026, 2026)
        cal = build_liuzhai_calendar(dates, _DEFAULT_CONFIG)
        ics_bytes = cal.to_ical()
        assert isinstance(ics_bytes, bytes)
        assert len(ics_bytes) > 0
        assert ics_bytes.startswith(b'BEGIN:VCALENDAR')
