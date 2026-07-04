"""Tests for 六斋日 (Six Vegetarian Days) detection algorithm.

测试策略：
  1. 固定斋日（初八、十四、十五、廿三）→ 每月必是
  2. 月尾斋日（廿九、三十）→ 取决于大月/小月
  3. 非斋日 → 采样验证
  4. 每月正确计数 → 每个农历月恰好 6 天
  5. 连续多年 → 覆盖闰月、跨年

NOTE: 农历→公历转换均由 lunar-python 动态计算。
"""

import datetime
import pytest
from lunar_python import Lunar
from calendar_engine.calendars.liuzhai import is_liuzhai_day


# ──────────────────────────────────────────────
# 固定斋日（每月初八、十四、十五、廿三）
# ──────────────────────────────────────────────

class TestFixedDays:
    """固定斋日：初八、十四、十五、廿三"""

    @pytest.mark.parametrize("solar_date,desc", [
        (datetime.date(2026, 9, 18), "2026-09-18 = 农历八月初八"),
        (datetime.date(2026, 9, 24), "2026-09-24 = 农历八月十四"),
        (datetime.date(2026, 9, 25), "2026-09-25 = 农历八月十五"),
        (datetime.date(2026, 10, 3), "2026-10-03 = 农历八月廿三"),
        (datetime.date(2027, 3, 15), "2027-03-15 = 农历二月初八"),
        (datetime.date(2028, 4, 2),  "2028-04-02 = 农历三月初八"),
    ])
    def test_fixed_days_are_liuzhai(self, solar_date, desc):
        assert is_liuzhai_day(solar_date) is True, desc

    def test_not_liuzhai_mid_month(self):
        """月中普通日期不是斋日"""
        # 2026-07-17 = 农历六月初四
        assert is_liuzhai_day(datetime.date(2026, 7, 17)) is False

    def test_not_liuzhai_beginning(self):
        """月初（初一至初七）不是斋日"""
        # 2026年六月初一 = 2026-07-14
        for day_offset in range(0, 7):
            d = datetime.date(2026, 7, 14) + datetime.timedelta(days=day_offset)
            assert is_liuzhai_day(d) is False, f"{d} 应不是斋日"


# ──────────────────────────────────────────────
# 月尾斋日：廿九、三十（大月/小月）
# ──────────────────────────────────────────────

class TestMonthEnd:
    """月尾斋日处理：大月30天，小月29天"""

    def test_large_month_29th_and_30th(self):
        """大月（30天）：廿九和三十都是斋日，廿八不是"""
        # 2026年三月 = 大月(30天)
        # 三月廿九 = 2026-05-15 → 是斋日
        # 三月三十 = 2026-05-16 → 是斋日
        assert is_liuzhai_day(datetime.date(2026, 5, 14)) is False   # 三月廿八（大月非斋日）
        assert is_liuzhai_day(datetime.date(2026, 5, 15)) is True    # 三月廿九
        assert is_liuzhai_day(datetime.date(2026, 5, 16)) is True    # 三月三十

    def test_small_month_28th_and_29th(self):
        """小月（29天）：廿八和廿九是斋日"""
        # 2026年五月 = 小月(29天)
        # 五月廿八 = 2026-07-12 → 是斋日（小月规则）
        # 五月廿九 = 2026-07-13 → 是斋日
        assert is_liuzhai_day(datetime.date(2026, 7, 12)) is True    # 五月廿八
        assert is_liuzhai_day(datetime.date(2026, 7, 13)) is True    # 五月廿九

    def test_small_month_no_day_30(self):
        """小月之后下月初一不是斋日"""
        d = datetime.date(2026, 7, 14)  # 六月初一
        assert is_liuzhai_day(d) is False


# ──────────────────────────────────────────────
# 每月计数验证（按农历月）
# ──────────────────────────────────────────────

class TestMonthlyCount:
    """每个农历月恰好 6 天"""

    def _check_month(self, lunar_year, lunar_month):
        """验证某个农历月的六斋日计数"""
        # 从初一开始遍历到月底（最大30天）
        count = 0
        last_day = 0
        for day in range(1, 31):
            try:
                l = Lunar.fromYmd(lunar_year, lunar_month, day)
                s = l.getSolar()
                solar_date = datetime.date(s.getYear(), s.getMonth(), s.getDay())
                if is_liuzhai_day(solar_date):
                    count += 1
                last_day = day
            except Exception:
                break
        return count, last_day

    def test_2026_all_months(self):
        """2026年每个月都是6天"""
        for m in range(1, 13):
            cnt, last = self._check_month(2026, m)
            assert cnt == 6, f"2026年{m}月有{cnt}天（月底到{last}日）"

    def test_2027_all_months(self):
        """2027年（无闰月）"""
        for m in range(1, 13):
            cnt, last = self._check_month(2027, m)
            assert cnt == 6, f"2027年{m}月有{cnt}天（月底到{last}日）"

    def test_2028_leap_month(self):
        """2028年有闰五月"""
        for m in range(1, 13):
            cnt, last = self._check_month(2028, m)
            assert cnt == 6, f"2028年{m}月有{cnt}天（月底到{last}日）"
        # 闰五月
        cnt, last = self._check_month(2028, -5)
        assert cnt == 6, f"2028年闰五月有{cnt}天（月底到{last}日）"


# ──────────────────────────────────────────────
# 闰月
# ──────────────────────────────────────────────

class TestLeapMonth:
    """闰月内也应遵循同样的六斋日规则"""

    def test_leap_month_has_liuzhai(self):
        """闰月也有六斋日"""
        # 2025年闰六月初八 = 2025-08-01
        assert is_liuzhai_day(datetime.date(2025, 8, 1)) is True   # 闰六月初八
        # 闰六月十四 = 2025-08-07
        assert is_liuzhai_day(datetime.date(2025, 8, 7)) is True   # 闰六月十四

    def test_non_leap_month_adjacent(self):
        """闰月前后的正常月不受影响"""
        # 2025年六月（非闰）初八 = 2025-07-02
        assert is_liuzhai_day(datetime.date(2025, 7, 2)) is True   # 六月初八


# ──────────────────────────────────────────────
# 年份边界
# ──────────────────────────────────────────────

class TestYearBoundary:
    """跨年边界：腊月底与正月的斋日"""

    def test_year_end_liuzhai(self):
        """腊月底的斋日"""
        # 2026年腊月 = 小月(29天)
        # 腊月廿八 = 2027-02-04 → 小月，是斋日
        # 腊月廿九 = 2027-02-05 → 小月，是斋日
        assert is_liuzhai_day(datetime.date(2027, 2, 4)) is True   # 腊月廿八
        assert is_liuzhai_day(datetime.date(2027, 2, 5)) is True   # 腊月廿九

    def test_year_start_not_liuzhai(self):
        """正月初一至初七不是斋日"""
        # 2027年正月初一 = 2027-02-06
        for day_offset in range(0, 7):
            d = datetime.date(2027, 2, 6) + datetime.timedelta(days=day_offset)
            assert is_liuzhai_day(d) is False, f"正月初{day_offset+1} 应不是斋日"
