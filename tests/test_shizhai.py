"""Tests for 十斋日 (Ten Vegetarian Days) detection.

十斋日定义：
  每月初一、初八、十四、十五、十八、二十三、二十四、二十八、二十九、三十
  小月（29天）无三十
"""

import datetime
import pytest
from lunar_python import Lunar
from calendar_engine.calendars.shizhai import is_observance, get_lunar_desc


class TestFixedDays:
    """固定斋日：初一、初八、十四、十五、十八、廿三、廿四"""

    @pytest.mark.parametrize("solar_date,desc", [
        (datetime.date(2026, 9, 11), "2026-09-11 = 八月初一"),
        (datetime.date(2026, 9, 18), "2026-09-18 = 八月初八"),
        (datetime.date(2026, 9, 24), "2026-09-24 = 八月十四"),
        (datetime.date(2026, 9, 25), "2026-09-25 = 八月十五"),
        (datetime.date(2026, 9, 28), "2026-09-28 = 八月十八"),
        (datetime.date(2026, 10, 3), "2026-10-03 = 八月廿三"),
        (datetime.date(2026, 10, 4), "2026-10-04 = 八月廿四"),
    ])
    def test_fixed_days(self, solar_date, desc):
        assert is_observance(solar_date) is True, desc

    def test_not_shizhai(self):
        """月中普通日期不是十斋日"""
        assert is_observance(datetime.date(2026, 9, 20)) is False  # 八月初十


class TestMonthEnd:
    """月尾：廿八、廿九、三十"""

    def test_large_month(self):
        """大月（30天）：廿八、廿九、三十都是十斋日"""
        # 2026年十一月 = 大月
        # 十一月廿九 = 2027-01-06
        # 十一月三十 = 2027-01-07
        assert is_observance(datetime.date(2027, 1, 5)) is True   # 十一月廿八
        assert is_observance(datetime.date(2027, 1, 6)) is True   # 十一月廿九
        assert is_observance(datetime.date(2027, 1, 7)) is True   # 十一月三十

    def test_small_month(self):
        """小月（29天）：廿八、廿九是十斋日"""
        # 2026年五月 = 小月
        # 五月廿八 = 2026-07-12
        assert is_observance(datetime.date(2026, 7, 12)) is True  # 五月廿八
        assert is_observance(datetime.date(2026, 7, 13)) is True  # 五月廿九


class TestYearlyCount:
    """每年约 10×12=120 天"""

    def _count(self, year):
        ct = 0
        d = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        while d <= end:
            if is_observance(d):
                ct += 1
            d += datetime.timedelta(days=1)
        return ct

    def test_2026_count(self):
        n = self._count(2026)
        assert n in range(115, 130), f"2026年十斋日={n}"

    def test_2027_count(self):
        n = self._count(2027)
        assert n in range(115, 130)


class TestLunarDesc:
    """农历描述"""

    def test_desc(self):
        desc = get_lunar_desc(datetime.date(2026, 9, 11))
        assert "八月初一" in desc
