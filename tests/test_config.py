"""Tests for config loading."""

import datetime
import pytest
from calendar_engine.core.config import AppConfig, load_config, get_calendar_alarm


class TestConfigLoading:
    """config.yaml 加载与默认值"""

    def test_minimal_config(self):
        """最小配置使用默认值"""
        raw = """
config_version: 1
calendar_name: "六斋日"
years:
  ahead: 5
"""
        cfg = load_config(raw)
        assert cfg.calendar_name == "六斋日"
        assert cfg.years_ahead == 5
        assert cfg.language == "zh-CN"
        assert cfg.alarm_enabled is True
        assert cfg.calendars == {"liuzhai": True}

    def test_full_config(self):
        """完整配置所有字段"""
        raw = """
config_version: 1
calendar_name: "六斋日定制版"
timezone: "Asia/Shanghai"
language: "bilingual"
event_title: "{emoji} {name} | {solar} | {lunar}"
event_description: "农历{lunar}\n公历{solar}"
alarm:
  enabled: false
  days_before: 2
  time: "08:00"
emoji: "🙏"
calendars:
  liuzhai: true
  shizhai: false
years:
  ahead: 10
"""
        cfg = load_config(raw)
        assert cfg.calendar_name == "六斋日定制版"
        assert cfg.language == "bilingual"
        assert cfg.emoji == "🙏"
        assert cfg.alarm_enabled is False
        assert cfg.alarm_days_before == 2
        assert cfg.alarm_time == "08:00"
        assert cfg.years_ahead == 10
        assert cfg.calendars == {"liuzhai": True, "shizhai": False}

    def test_unknown_fields_ignored(self):
        """新增未知字段不报错（向前兼容）"""
        raw = """
config_version: 1
calendar_name: "六斋日"
unknown_field: "should be ignored"
years:
  ahead: 3
"""
        cfg = load_config(raw)
        assert cfg.calendar_name == "六斋日"
        assert cfg.years_ahead == 3

    def test_old_zhai_types_field(self):
        """旧版 zhai_types 字段映射到 calendars"""
        raw = """
config_version: 1
calendar_name: "六斋日"
zhai_types:
  liuzhai: true
years:
  ahead: 5
"""
        cfg = load_config(raw)
        assert cfg.calendars.get("liuzhai") is True

    def test_calendar_override_global_alarm(self):
        """日历独立 alarm 覆盖全局"""
        raw = """
alarm:
  enabled: true
calendars:
  liuzhai:
    alarm:
      enabled: true
  shizhai:
    alarm:
      enabled: false
years:
  ahead: 5
"""
        cfg = load_config(raw)
        lz = get_calendar_alarm(cfg, "liuzhai")
        sz = get_calendar_alarm(cfg, "shizhai")
        assert lz["enabled"] is True
        assert sz["enabled"] is False

    def test_calendar_fallback_global_alarm(self):
        """日历未指定 alarm 时回退到全局"""
        raw = """
alarm:
  enabled: true
  days_before: 2
calendars:
  liuzhai: true
years:
  ahead: 5
"""
        cfg = load_config(raw)
        alarm = get_calendar_alarm(cfg, "liuzhai")
        assert alarm["enabled"] is True
        assert alarm["days_before"] == 2

    def test_calendar_bool_true_uses_global_alarm(self):
        """旧式 calendars[liuzhai]: true 格式使用全局 alarm"""
        raw = """
alarm:
  enabled: true
calendars:
  liuzhai: true
years:
  ahead: 5
"""
        cfg = load_config(raw)
        alarm = get_calendar_alarm(cfg, "liuzhai")
        assert alarm["enabled"] is True
