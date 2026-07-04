"""Calendar Engine — 日历类型定义。"""

import datetime
from collections.abc import Callable


class CalendarType:
    """日历类型定义。

    每个日历模块通过此数据结构在注册表中声明自己。
    """

    def __init__(
        self,
        key: str,
        name: str,
        file_name: str,
        uid_prefix: str,
        is_observance: Callable[[datetime.date], bool],
        get_lunar_desc: Callable[[datetime.date], str],
        emoji: str = "",
        categories: tuple[str, ...] = (),
    ) -> None:
        self.key = key
        self.name = name
        self.file_name = file_name
        self.uid_prefix = uid_prefix
        self.is_observance = is_observance
        self.get_lunar_desc = get_lunar_desc
        self.emoji = emoji
        self.categories = categories
