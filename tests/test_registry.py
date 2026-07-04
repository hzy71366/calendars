"""Tests for Calendar Engine registry system."""

import datetime
import pytest
from calendar_engine.types import CalendarType
from calendar_engine.registry import CALENDAR_REGISTRY, get_calendar_type


class TestCalendarType:
    """CalendarType 数据类型"""

    def test_minimal_type(self):
        """创建最小 CalendarType"""
        ct = CalendarType(
            key="test",
            name="测试日历",
            file_name="test.ics",
            uid_prefix="test",
            is_observance=lambda d: False,
            get_lunar_desc=lambda d: "",
        )
        assert ct.key == "test"
        assert ct.file_name == "test.ics"

    def test_has_defaults(self):
        """CalendarType 有合理的默认值"""
        ct = CalendarType(
            key="test",
            name="测试日历",
            file_name="test.ics",
            uid_prefix="test",
            is_observance=lambda d: False,
            get_lunar_desc=lambda d: "",
        )
        assert ct.emoji == ""  # 默认无图标
        assert ct.categories == ()  # 默认空分类


class TestRegistry:
    """日历注册表"""

    def test_liuzhai_registered(self):
        """六斋日已在注册表中"""
        assert "liuzhai" in CALENDAR_REGISTRY

    def test_liuzhai_has_required_fields(self):
        """六斋日注册项包含所有必填字段"""
        liuzhai = CALENDAR_REGISTRY["liuzhai"]
        assert liuzhai.key == "liuzhai"
        assert liuzhai.name == "六斋日"
        assert liuzhai.file_name == "liuzhai.ics"
        assert liuzhai.uid_prefix == "liuzhai"
        assert callable(liuzhai.is_observance)
        assert callable(liuzhai.get_lunar_desc)

    def test_liuzhai_observance(self):
        """六斋日判定函数正常工作"""
        liuzhai = CALENDAR_REGISTRY["liuzhai"]
        # 2026-09-18 = 八月初八
        assert liuzhai.is_observance(datetime.date(2026, 9, 18)) is True
        # 2026-07-17 = 六月初四
        assert liuzhai.is_observance(datetime.date(2026, 7, 17)) is False

    def test_liuzhai_lunar_desc(self):
        """农历描述函数正常工作"""
        liuzhai = CALENDAR_REGISTRY["liuzhai"]
        desc = liuzhai.get_lunar_desc(datetime.date(2026, 9, 18))
        assert "八月初八" in desc

    def test_get_calendar_type(self):
        """按 key 获取日历类型"""
        ct = get_calendar_type("liuzhai")
        assert ct is not None
        assert ct.name == "六斋日"

    def test_get_nonexistent(self):
        """不存在的 key 返回 None"""
        assert get_calendar_type("nonexistent") is None

    def test_registry_keys(self):
        """注册表至少包含 liuzhai"""
        keys = set(CALENDAR_REGISTRY.keys())
        assert "liuzhai" in keys
