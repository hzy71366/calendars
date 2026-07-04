"""二十四节气模块（预留）。

TODO: 利用 lunar-python 的 getJieQi() 实现节气标记。
"""

import datetime


def is_observance(solar_date: datetime.date) -> bool:
    """判断是否为二十四节气（暂未实现）。"""
    raise NotImplementedError("二十四节气尚未实现")


def get_lunar_desc(solar_date: datetime.date) -> str:
    """获取农历描述（暂未实现）。"""
    raise NotImplementedError("二十四节气尚未实现")
