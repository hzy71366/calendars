# Calendar Engine — 架构设计

> 将 liuzhai-ics 从单一日历项目升级为日历引擎（Calendar Engine），
> 支持多日历类型：六斋日、十斋日、佛教节日、二十四节气等。

---

## 一、定位变化

```
之前：liuzhai-ics        ← 单一六斋日日历生成器
之后：buddhist-calendars  ← 多日历生成引擎（Calendar Engine）
```

每个日历类型是引擎的一个**插件**，通过注册表统一管理。

---

## 二、包结构

```
src/calendar_engine/
├── __init__.py              ← 版本号 + 关键导出
│
├── registry.py              ← CALENDAR_REGISTRY（核心注册表）
│
├── config.py                ← 配置加载（通用，不依赖具体日历）
│
├── generator.py             ← ICS 生成器（只依赖 registry，不写死日历）
│
├── calendars/               ← 日历类型模块集
│   ├── __init__.py
│   ├── liuzhai.py           ← 六斋日（从 zhai_types.py 迁移）
│   ├── shizhai.py           ← 十斋日（预留）
│   ├── buddhist.py          ← 佛教节日（预留）
│   └── solar_terms.py       ← 二十四节气（预留）
│
└── types/                   ← 通用类型定义
    └── __init__.py
```

---

## 三、注册表机制（核心）

### 3.1 日历模块接口

每个日历模块必须实现以下接口：

```python
# 必填常量
CALENDAR_KEY = "liuzhai"         # 注册键名
CALENDAR_NAME = "六斋日"         # 显示名称
FILE_NAME = "liuzhai.ics"        # 输出文件名
UID_PREFIX = "liuzhai"           # UID 前缀

# 必填函数
def is_observance(solar_date: datetime.date) -> bool:
    """判断指定公历日期是否属于本日历的纪念日。"""
    ...

def get_lunar_desc(solar_date: datetime.date) -> str:
    """生成该日期的农历描述（如"八月初八"）。"""
    ...
```

### 3.2 注册表定义

```python
CALENDAR_REGISTRY: dict[str, CalendarType] = {
    "liuzhai": CalendarType(
        key="liuzhai",
        name="六斋日",
        file_name="liuzhai.ics",
        uid_prefix="liuzhai",
        is_observance=liuzhai.is_observance,
        get_lunar_desc=liuzhai.get_lunar_desc,
    ),
    "shizhai": CalendarType(...),       # 预留
    "buddhist": CalendarType(...),      # 预留
    "solar_terms": CalendarType(...),   # 预留
}
```

### 3.3 生成器逻辑

```python
def generate_all(config: AppConfig) -> list[Path]:
    """遍历注册表，为每个启用的日历生成 ICS 文件。"""
    for key, cal_type in CALENDAR_REGISTRY.items():
        if config.calendars.get(key, True):    # 默认启用
            dates = collect_dates(cal_type, years)
            ics = build_calendar(cal_type, dates, config)
            save(ics, output_dir / cal_type.file_name)
```

---

## 四、兼容性保障

### 4.1 liuzhai.ics 内容不变

| 项 | 保障措施 |
|:--|:---------|
| 事件数据 | 逻辑从 zhai_types.py 原样迁移到 liuzhai.py，算法不变 |
| UID 规则 | `liuzhai-{YYYYMMDD}@liuzhai-ics` 不变 |
| 文件名 | 仍输出 `liuzhai.ics` |
| 配置 | config.yaml 中 `zhai_types` 兼容处理 |

### 4.2 URL 变化

仓库重命名后 GitHub Pages URL 会变化：

```
旧: https://hzy71366.github.io/liuzhai-ics/liuzhai.ics
新: https://hzy71366.github.io/buddhist-calendars/liuzhai.ics
```

**已订阅用户需更新订阅链接。** 但 ICS 内容（事件、UID、提醒）完全不变，
更新链接后不会出现重复事件。

---

## 五、配置系统

用户在 `config.yaml` 中通过 `calendars` 字段控制启用哪些日历：

```yaml
calendars:
  liuzhai: true        # 六斋日 → liuzhai.ics
  shizhai: false       # 十斋日（默认关闭）
  buddhist: false      # 佛教节日（默认关闭）
  solar_terms: false   # 二十四节气（默认关闭）
```

旧版 `zhai_types` 字段仍受支持（向后兼容），在加载时自动映射为 `calendars.liuzhai`。

---

## 六、未来扩展

| 类型 | 文件名 | 优先级 | 实现方式 |
|:----|:------|:------:|:---------|
| 十斋日 | `shizhai.ics` | 高 | 在 `calendars/shizhai.py` 实现判定函数 |
| 观音斋 | `guanyinzhai.ics` | 中 | 在 `calendars/buddhist.py` 中扩展 |
| 佛菩萨圣诞 | `buddhist.ics` | 中 | 需收集数据表，在 `calendars/buddhist.py` 中实现 |
| 二十四节气 | `solar_terms.ics` | 低 | lunar-python 直接支持节气查询，简单封装即可 |

新增日历的流程：

```
1. 在 calendars/ 下创建模块文件
2. 实现 is_observance() 和 get_lunar_desc()
3. 在 registry.py 中注册
4. 在 config.yaml 的 calendars 中添加开关
5. CI 自动生成对应 .ics 文件
```

---

## 七、迁移步骤

```
Step 1: 设计文档（本文档）
Step 2: 创建 calendar_engine 包 + registry
Step 3: 迁移 liuzhai 日历到 calendars/liuzhai.py
Step 4: 预留 shizhai/buddhist/solar_terms 模块
Step 5: 更新 Generator + Config 使用 Registry
Step 6: 更新入口脚本 + publish workflow
Step 7: 重命名仓库为 buddhist-calendars
Step 8: 验证 liuzhai.ics 输出结果一致
```
