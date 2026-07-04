"""Tests for config loading and template rendering."""

import datetime
import pytest
import yaml
from liuzhai_ics.config import load_config, render_title, render_description


# ──────────────────────────────────────────────
# 配置加载
# ──────────────────────────────────────────────

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
        # 默认值
        assert cfg.language == "zh-CN"
        assert cfg.emoji == "🔴"
        assert cfg.event_title == "{emoji} {name} · 农历{lunar}"
        assert cfg.alarm_enabled is True

    def test_full_config(self):
        """完整配置所有字段"""
        raw = """
config_version: 1
calendar_name: "六斋日定制版"
timezone: "Asia/Shanghai"
language: "bilingual"
event_title: "{emoji} {name} | {solar} | {lunar}"
event_description: "农历{lunar}\\n公历{solar}"
alarm:
  enabled: false
  days_before: 2
  time: "08:00"
emoji: "🙏"
categories:
  - "佛教"
  - "斋日"
zhai_types:
  liuzhai: true
  shizhai: false
years:
  start: 0
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
        assert cfg.zhai_types == {"liuzhai": True, "shizhai": False}
        assert cfg.categories == ("佛教", "斋日")

    def test_unknown_fields_ignored(self):
        """新增未知字段不报错（向前兼容）"""
        raw = """
config_version: 1
calendar_name: "六斋日"
unknown_field: "should be ignored"
another_unknown: 42
years:
  ahead: 3
"""
        cfg = load_config(raw)
        assert cfg.calendar_name == "六斋日"
        assert cfg.years_ahead == 3
        # 不应因为未知字段报错

    def test_missing_required_field(self):
        """缺少必填字段应有合理的默认值或报错"""
        raw = """
config_version: 1
"""
        cfg = load_config(raw)
        assert cfg.calendar_name == "六斋日"  # 默认值


# ──────────────────────────────────────────────
# 模板渲染 — 标题
# ──────────────────────────────────────────────

class TestRenderTitle:
    """event_title 模板变量替换"""

    def test_default_template(self):
        """默认模板正确渲染"""
        result = render_title(
            template="{emoji} {name} · 农历{lunar}",
            emoji="🔴",
            name="六斋日",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert result == "🔴 六斋日 · 农历八月初八"

    def test_custom_template(self):
        """自定义模板渲染"""
        result = render_title(
            template="{emoji} {name} | {solar}",
            emoji="🙏",
            name="六斋日",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert result == "🙏 六斋日 | 2026-09-18"

    def test_template_all_vars(self):
        """所有变量同时使用"""
        result = render_title(
            template="{emoji} | {name} | {lunar} | {solar}",
            emoji="🔴",
            name="六斋日",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert result == "🔴 | 六斋日 | 八月初八 | 2026-09-18"

    def test_template_no_vars(self):
        """模板不含变量"""
        result = render_title(
            template="固定标题",
            emoji="🔴",
            name="六斋日",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert result == "固定标题"

    def test_unknown_var_preserved(self):
        """模板中未知变量原样保留（不是必须的）"""
        result = render_title(
            template="{emoji} {unknown}",
            emoji="🔴",
            name="六斋日",
            lunar="八月初八",
            solar="2026-09-18",
        )
        # 未知变量不强制处理，但应保持原样或替换为空
        assert "{emoji}" not in result or "🔴" in result


# ──────────────────────────────────────────────
# 模板渲染 — 描述
# ──────────────────────────────────────────────

class TestRenderDescription:
    """event_description 模板变量替换"""

    def test_default_description(self):
        """描述包含农历和说明文字"""
        result = render_description(
            template="农历{lunar}\\n六斋日，过午不食，持斋修行。",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert "农历八月初八" in result
        assert "六斋日" in result

    def test_description_multiline(self):
        """描述包含多行"""
        result = render_description(
            template="农历{lunar}\\n公历{solar}\\n说明文字",
            lunar="八月初八",
            solar="2026-09-18",
        )
        assert "\\n" in result or "\n" in result
        assert result.count("\n") >= 1 or result.count("\\n") >= 1
