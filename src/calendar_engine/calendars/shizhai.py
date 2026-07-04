"""十斋日模块（预留）。

十斋日定义（源自《地藏菩萨本愿经》）：
  每月初一、初八、十四、十五、十八、二十三、二十四、二十八、二十九、三十
  小月（29天）无三十，调整为二十八、二十九

TODO: 实现 is_observance() 判定函数
"""

import datetime


def is_observance(solar_date: datetime.date) -> bool:
    """判断是否为十斋日（暂未实现）。"""
    raise NotImplementedError("十斋日尚未实现")


def get_lunar_desc(solar_date: datetime.date) -> str:
    """获取农历描述（暂未实现）。"""
    raise NotImplementedError("十斋日尚未实现")
