# 六斋日 ICS 日历订阅项目 · 设计文档

> 开源项目，生成可订阅的 iPhone/iCal 六斋日 ICS 日历，自动更新，永久可用。

---

## 目錄

1. [产品需求分析](#1-产品需求分析)
2. [技术方案设计](#2-技术方案设计)
3. [GitHub 项目目录结构](#3-github-项目目录结构)
4. [数据来源方案](#4-数据来源方案)
5. [六斋日算法](#5-六斋日算法)
6. [ICS 事件设计](#6-ics-事件设计)
7. [用户配置设计](#7-用户配置设计)
8. [iPhone 兼容性](#8-iphone-兼容性)
9. [GitHub Pages 发布方案](#9-github-pages-发布方案)
10. [GitHub Actions 自动更新方案](#10-github-actions-自动更新方案)
11. [可扩展性](#11-可扩展性)
12. [README 结构规划](#12-readme-结构规划)
13. [许可证与发布](#13-许可证与发布)
14. [版本与升级保障](#14-版本与升级保障)

---

## 1. 产品需求分析

### 1.1 核心需求

生成一个 iOS / macOS / Google Calendar 可直接订阅的 ICS 日历，标记每月的六斋日。

### 1.2 六斋日规则

依据《增一阿含经》《毗婆沙论》，每月六斋日为：

| 农历日期 | 说明 |
|:--------:|:----|
| 初八 | 恒定 |
| 十四 | 恒定 |
| 十五 | 恒定 |
| 二十三 | 恒定 |
| 二十九 | 大月（30天）时取廿九 |
| 三十 | 大月取三十，小月（29天）取廿八 |

### 1.3 用户故事

| 角色 | 场景 |
|:----|:-----|
| 佛教居士 | 在 iPhone 日历上订阅六斋日，到日子自动提醒 |
| 寺院管理 | 需要查看未来数年的六斋日安排 |
| 开发者 | Fork 项目自定义提醒时间或添加其他斋日类型 |

### 1.4 功能清单

| 功能 | 优先级 | 说明 |
|:----|:----:|:-----|
| ICS 文件生成 | P0 | 根据农历计算，输出标准 ICS |
| GitHub Pages 发布 | P0 | 提供可订阅的 HTTPS URL |
| GitHub Actions 自动更新 | P0 | 定期重新生成，保持最新 |
| iPhone 直接订阅 | P0 | ICS 格式兼容 iOS 日历 |
| 提前 N 分钟提醒（VALARM） | P1 | 用户通过 config.yaml 自定义 |
| 多语言标题 | P1 | 中文/英文/双语 |
| 支持多年份（当前+5年） | P1 | 一次订阅覆盖未来 |
| 多斋日类型扩展 | P2 | 十斋日、观音斋、佛菩萨圣诞、节气 |

---

## 2. 技术方案设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Python 生成脚本 (scripts/generate_ics.py)        │   │
│  │   ↓  使用 lunar-python 计算农历 → 公历            │   │
│  │   ↓  使用 icalendar 生成 ICS 文件                │   │
│  │   ↓  输出到 docs/ (GitHub Pages 根目录)          │   │
│  └──────────────────────────────────────────────────┘   │
│                        │                                  │
│  ┌─────────────────────┴────────────────────────────────┐ │
│  │  GitHub Actions (每周一 00:00 UTC)                    │ │
│  │  .github/workflows/update-ics.yml                    │ │
│  │  1. checkout → 2. pip install → 3. python generate   │ │
│  │  4. git add docs/*.ics → 5. git commit → 6. git push │ │
│  └──────────────────────────────────────────────────────┘ │
│                        │                                  │
│  ┌─────────────────────┴────────────────────────────────┐ │
│  │  GitHub Pages (docs/ 目录)                            │ │
│  │  https://<user>.github.io/liuzhai-ics/liuzhai.ics    │ │
│  │  https://<user>.github.io/liuzhai-ics/shizhai.ics    │ │
│  └──────────────────────────────────────────────────────┘ │
│                        │                                  │
│                        ▼                                  │
│              ┌─────────────────────┐                      │
│              │  iPhone / Mac 日历   │                      │
│              │  → 添加订阅日历      │                      │
│              │  → 输入 ICS URL     │                      │
│              │  → 自动接收更新      │                      │
│              └─────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 组件 | 选择 | 理由 |
|:----|:----|:-----|
| 农历计算 | **lunar-python**（6tail/lunar-python） | 最成熟的 Python 农历库，1.8k stars，无第三方依赖 |
| ICS 生成 | **icalendar** | Python 标准 ICS 库，支持 VALARM、时区、重复事件 |
| 自动构建 | **GitHub Actions** | 免费，与仓库天然集成 |
| 静态托管 | **GitHub Pages** | 免费 HTTPS，支持 .ics MIME 类型 |
| 测试验证 | **pytest** | 轻量，适合验证日期计算 |

### 2.3 关键依赖

```txt
# requirements.txt
lunar-python>=3.0.0      # 农历/公历转换
icalendar>=5.0.0         # ICS 文件生成
pyyaml>=6.0              # 读取 config.yaml
pytest>=8.0.0            # 测试（仅开发需要）
```

---

## 3. GitHub 项目目录结构

```
liuzhai-ics/
├── .github/
│   └── workflows/
│       └── update-ics.yml         ← GitHub Actions 自动更新
│
├── scripts/
│   ├── generate_ics.py            ← 主脚本：生成 ICS
│   ├── zhai_types.py              ← 斋日判定函数（可扩展）
│   └── __init__.py                ← 包标记
│
├── tests/
│   ├── test_zhai_types.py         ← 斋日判定测试
│   └── test_generate_ics.py       ← ICS 生成测试
│
├── docs/                          ← GitHub Pages 根目录
│   ├── index.html                 ← 项目主页（使用说明）
│   ├── liuzhai.ics                ← 六斋日日历
│   ├── shizhai.ics                ← 十斋日日历（未来扩展）
│   └── buddhist.ics               ← 佛教节日合集（未来扩展）
│
├── config.yaml                    ← 用户配置
├── requirements.txt               ← Python 依赖
├── LICENSE                        ← MIT
├── README.md                      ← 项目说明
├── CHANGELOG.md                   ← 版本历史
├── CONTRIBUTING.md                ← 贡献指南
└── .gitignore
```

---

## 4. 数据来源方案

### 4.1 方案选择

```
方案 A：lunar-python 库（选择）
  优点：无第三方依赖，纯算法计算，不依赖网络，内置 1900-2100 年农历数据
  
方案 B：预计算 JSON 数据源
  缺点：数据源需要维护，更新滞后

方案 C：调用外部 API
  缺点：依赖外部服务，可能限流或下线
```

**选择方案 A**：`lunar-python` 内置了完整的农历数据，纯算法计算。

### 4.2 核心 API

```python
from lunar_python import Lunar

# 公历 → 农历
lunar = Lunar.fromDate(solar_date)
lunar.getYear()               # 农历年
lunar.getMonth()              # 农历月
lunar.getDay()                # 农历日
lunar.getDayCountInMonth()    # 当月总天数（29 或 30）
```

---

## 5. 六斋日算法

### 5.1 算法规则

每月六斋日为**固定的农历日期**，跨月份转换为公历后标记。

```
每月固定六天：
  初八、十四、十五、二十三、二十九、三十

但农历月有两种长度：
  大月 = 30 天 → 有三十，斋日为 8, 14, 15, 23, 29, 30
  小月 = 29 天 → 无三十，斋日调整为 8, 14, 15, 23, 28, 29
```

### 5.2 伪代码

```
function is_liuzhai_day(solar_date):
    lunar = Lunar.fromDate(solar_date)
    day = lunar.getDay()                # 农历日
    month_total = lunar.getDayCountInMonth()  # 当月总天数

    # 恒定斋日
    if day in {8, 14, 15, 23}:
        return True

    # 月尾斋日
    if month_total == 30:               # 大月
        return day in {29, 30}
    else:                               # 小月（29天）
        return day in {28, 29}

    return False
```

### 5.3 算法来源

| 来源 | 内容 |
|:----|:-----|
| **《增一阿含经》** | 原始经典依据，定义每月六斋日 |
| **《毗婆沙论》** | 补充说明大月小月的处理方式 |
| **灵隐寺官方文档** | 明确记载："初八、十四、十五、二十三、二十九、三十（小月二十八、二十九）" |

### 5.4 边界情况

| 场景 | 处理 |
|:----|:-----|
| 闰月 | 闰月正常计算，斋日规则不变 |
| 小月+闰月 | 同时存在，仍按小月规则处理月尾 |
| 农历新年跨月 | 不受影响，公历二月对应农历正月或腊月 |

---

## 6. ICS 事件设计

### 6.1 事件属性

| 属性 | 值 | 说明 |
|:----|:---|:-----|
| DTSTART | `VALUE=DATE:20260708` | **全天事件**，不包含时间 |
| DTEND | `VALUE=DATE:20260709` | 结束日期 = 开始 + 1 天 |
| SUMMARY | `🔴 六斋日` | 标题，格式见下方 |
| DESCRIPTION | 农历日期 + 说明 | 详细描述 |
| CATEGORIES | `佛教, 斋日` | 分类，iOS 可按分类筛选 |
| UID | `liuzhai-20260708@liuzhai-ics` | 稳定 UUID，**永不改变** |
| RRULE | 不使用 | 每个斋日单独事件，不重复 |
| SEQUENCE | 0 | 序列号，更新时递增 |
| TRANSP | TRANSPARENT | 斋日为透明事件，不影响忙闲状态 |

### 6.2 标题格式

用户可通过 `config.yaml` 选择标题格式：

| 语言选项 | 示例 |
|:--------|:-----|
| `zh-CN` | `🔴 六斋日 · 农历六月初八` |
| `en` | `LiuZhai Day · 6th Month 8th Day` |
| `bilingual` | `🔴 六斋日 · 农历六月初八 / LiuZhai Day` |

### 6.3 描述格式

```
农历六月初八
六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。

Lunar: 6th Month, 8th Day
LiuZhai (Six Vegetarian Days) — A day for practicing vegetarianism,
refraining from eating after noon, and cultivating mindfulness.
```

### 6.4 全天事件 vs 定时事件

| 方案 | 选择 | 理由 |
|:----|:----:|:-----|
| **全天事件**（VALUE=DATE）| ✅ 采用 | 斋日覆盖全天，与时区无关 |
| 定时事件（DTSTART 带时间）| ❌ 拒绝 | 斋日从凌晨到午夜，不需要具体时间 |

全天事件在 iOS/Google 日历中显示为日历顶部通栏，视觉效果最清晰。

### 6.5 提醒（VALARM）

```ics
BEGIN:VALARM
TRIGGER:-P1DT9H          ← 提前 1 天 09:00 触发
ACTION:DISPLAY
DESCRIPTION:明天（农历X月X日）是六斋日
END:VALARM
```

| 属性 | 值 | 说明 |
|:----|:---|:-----|
| TRIGGER | `-P1DT9H` 或用户自定义 | 相对事件开始的偏移量 |
| ACTION | `DISPLAY` | 弹窗提醒，iOS 原生支持 |
| DESCRIPTION | 自定义文字 | 提醒内容 |

**提醒时间计算公式：**

```
提醒触发时间 = 事件开始时间 00:00 - (提前天数 × 24h) + (提醒时刻的偏移)

示例：提前 1 天、上午 9:00 提醒
→ TRIGGER: -P1DT9H
→ 表示"事件前一天 09:00"（因为事件开始是 00:00，减1天加9小时 = -P1DT9H）
```

**用户可通过 `config.yaml` 完全自定义：**

```yaml
alarm:
  enabled: true
  days_before: 1          # 提前几天
  time: "09:00"           # 当天几点提醒
```

### 6.6 时区处理

| 决策 | 选择 | 理由 |
|:----|:----|:-----|
| 全天事件 | **不包含时区信息** | ICS 标准中全天事件与时区无关 |
| 用户时区 | **由订阅端系统日历自动处理** | iOS/Google 日历根据用户设置显示 |
| VCALENDAR | **不设 TIMEZONE 组件** | 保持 ICS 文件简洁、兼容性最佳 |

**为什么不需要时区：**
- `VALUE=DATE` 类型的 DTSTART/DTEND 不包含时间，只包含日期
- 日历应用会自动将日期映射到用户当前时区
- 这意味着不管用户在哪个时区，看到的都是正确的日期

---

## 7. 用户配置设计

### 7.1 设计原则

1. **向前兼容**：新增配置字段不影响旧版本
2. **合理默认值**：不配置也能直接使用
3. **自文档化**：配置文件中包含注释说明
4. **轻量**：纯 YAML，不需额外库

### 7.2 config.yaml 完整设计

```yaml
# ============================================================
# 六斋日 ICS 日历 · 用户配置
# 修改此文件后，GitHub Actions 会自动重新生成 ICS 文件
# ============================================================

# --- 版本（不要修改）---
# 用于脚本判断配置格式兼容性
config_version: 1

# --- 日历元信息 ---
calendar_name: "六斋日"                  # 日历名称，订阅后显示在 iOS 日历列表中
timezone: "Asia/Shanghai"                # 仅用于参考信息，全天事件不依赖时区

# --- 语言 ---
# 可选值: zh-CN / en / bilingual
language: "zh-CN"

# --- 事件标题 ---
# 可用变量:
#   {emoji}    → 图标（如 🔴）
#   {name}     → 日历名称
#   {lunar}    → 农历日期（如 "六月初八"）
#   {solar}    → 公历日期（如 "2026-07-08"）
#
# 默认: "{emoji} {name} · 农历{lunar}"
event_title: "{emoji} {name} · 农历{lunar}"

# --- 事件描述 ---
# 可用变量同 event_title
event_description: |
  农历{lunar}
  六斋日，过午不食，持斋修行，诸恶莫作，众善奉行。
  
  Lunar: {lunar_en}
  LiuZhai (Six Vegetarian Days)

# --- 提醒设置 ---
alarm:
  enabled: true                    # true=开启提醒, false=关闭
  days_before: 1                   # 提前几天提醒
  time: "09:00"                    # 提醒时刻（24小时制）

# --- 图标 ---
# 在标题前面显示的 emoji，可以换成其他符号
# 设为 "" 则不显示图标
emoji: "🔴"

# --- 分类标签（iOS 日历可按分类筛选）---
categories:
  - "佛教"
  - "斋日"

# --- 斋日类型（选择要生成的日历）---
# 设为 true 会生成对应的 .ics 文件
zhai_types:
  liuzhai: true                    # 六斋日 → liuzhai.ics
  shizhai: false                   # 十斋日（未来扩展）
  guanyinzhai: false               # 观音斋（未来扩展）
  buddhist_festivals: false        # 佛菩萨圣诞（未来扩展）

# --- 年份范围 ---
years:
  start: 0                         # 0=当前年份
  ahead: 5                         # 未来 N 年（含当前年）
```

### 7.3 向前兼容保障

```yaml
# 版本 1 → 版本 2 时：
# config_version: 2
# 新增字段带默认值处理
# 脚本读取时根据 version 决定解析逻辑
```

**原则：**

1. 新增字段必须有**合理默认值**
2. 脚本读取未知字段时**不报错，直接忽略**
3. `config_version` 只增不减

---

## 8. iPhone 兼容性

### 8.1 兼容性矩阵

| 日历应用 | 全天事件 | ICS 订阅 | VALARM 提醒 | UTF-8 中文 | Emoji |
|:--------|:-------:|:--------:|:----------:|:----------:|:----:|
| **Apple Calendar**（iOS/macOS） | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Google Calendar** | ✅ | ✅ | ✅ | ✅ | ✅（部分版本） |
| **Microsoft Outlook** | ✅ | ✅（Web 版受限） | ✅ | ✅ | ⚠️ 部分支持 |

### 8.2 各平台订阅方式

#### Apple Calendar（iPhone / Mac）

```
设置 → 日历 → 账户 → 添加订阅日历
→ 输入 URL: https://<user>.github.io/liuzhai-ics/liuzhai.ics
→ 完成
```

#### Google Calendar

```
其他日历 → 通过网址添加
→ 输入 URL: https://<user>.github.io/liuzhai-ics/liuzhai.ics
→ 完成
```

### 8.3 注意事项

| 平台 | 注意事项 |
|:----|:---------|
| iOS | 默认 24h-7d 刷新缓存，ICS 更新后不会立即生效 |
| Google Calendar | 刷新频率约 12-24h，无法强制手动刷新 |
| Outlook Web | 部分版本不支持外部 ICS 订阅，建议使用桌面版 |
| **所有人** | 订阅后由服务端推送，不在 App Store 发布 |

---

## 9. GitHub Pages 发布方案

### 9.1 URL 设计

**设计原则：URL 一旦发布，永不改变。**

```
# 核心 URL（v1.0 起提供）
https://<user>.github.io/liuzhai-ics/liuzhai.ics       ← 六斋日

# 未来扩展 URL（v2.0+）
https://<user>.github.io/liuzhai-ics/shizhai.ics        ← 十斋日
https://<user>.github.io/liuzhai-ics/buddhist.ics       ← 佛教节日合集（含六斋日、佛菩萨圣诞等）
```

### 9.2 为什么 URL 不能改

```
用户订阅日历后，iOS/Google 日历会缓存这个 URL
如果 URL 变了 → 用户需要在日历设置重新输入 → 用户体验极差
所以 liuzhai.ics 这个 URL 必须永远可用
```

### 9.3 域名与部署

| 选项 | 说明 |
|:----|:-----|
| 默认域名 | `https://<user>.github.io/liuzhai-ics/` |
| 自定义域名 | 用户可在 `docs/CNAME` 中配置（不影响 URL 结构） |
| 文件位置 | `docs/liuzhai.ics`（GitHub Pages 根目录） |

### 9.4 发布配置

```
GitHub Pages 设置：
  来源: Deploy from branch
  分支: main
  目录: /docs
```

### 9.5 文件输出

```python
# 生成脚本输出到 docs/ 目录
docs/
├── liuzhai.ics          # 六斋日
├── shizhai.ics          # 十斋日（未来）
└── buddhist.ics         # 佛教节日合集（未来）
```

---

## 10. GitHub Actions 自动更新方案

### 10.1 工作流设计

```yaml
name: 更新日历
on:
  schedule:
    - cron: "0 0 * * 1"       # 每周一 00:00 UTC
  workflow_dispatch:           # 手动触发
  push:
    paths:
      - "config.yaml"          # 配置变更时触发

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python scripts/generate_ics.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update ICS calendar files"
          file_pattern: "docs/*.ics"
```

### 10.2 触发策略

| 触发方式 | 频率 | 作用 |
|:--------|:----|:-----|
| 每周一定时 | 每周 | 常规更新，保持未来日期覆盖 |
| 手动触发 | 按需 | 修复数据或立即发布 |
| config.yaml 变更 | 配置修改时 | 用户改配置后立即生效 |

### 10.3 生成范围

默认生成 **当前年份 + 未来 5 年**，通过 `config.yaml` 的 `years.ahead` 配置。

---

## 11. 可扩展性

### 11.1 扩展架构

核心设计思想：**新增斋日类型 = 新增判定函数，不改核心代码。**

```
scripts/
├── generate_ics.py        ← 核心生成逻辑（不变）
└── zhai_types.py          ← 斋日判定函数（可扩展）
```

### 11.2 斋日类型注册

```python
# zhai_types.py
# 新增斋日类型只需在 ZHAI_TYPES 字典中注册一个函数

def is_liuzhai(lunar):
    """六斋日判定"""
    day = lunar.getDay()
    total = lunar.getDayCountInMonth()
    if day in (8, 14, 15, 23):
        return True
    if total == 30:
        return day in (29, 30)
    return day in (28, 29)


def is_shizhai(lunar):
    """十斋日判定：
    初一、初八、十四、十五、十八、二十三、二十四、二十八、二十九、三十
    """
    day = lunar.getDay()
    total = lunar.getDayCountInMonth()
    fixed = (1, 8, 14, 15, 18, 23, 24)
    if day in fixed:
        return True
    if total == 30:
        return day in (28, 29, 30)
    return day in (28, 29)


# 注册表 —— 新增斋日类型只在这里加一行
ZHAI_TYPES = {
    "liuzhai": {
        "name": "六斋日",
        "file": "liuzhai.ics",
        "check": is_liuzhai,
    },
    "shizhai": {
        "name": "十斋日",
        "file": "shizhai.ics",
        "check": is_shizhai,
    },
}
```

### 11.3 未来扩展清单

| 类型 | 文件 | 实现难度 | 说明 |
|:----|:----|:-------:|:-----|
| **十斋日** | `shizhai.ics` | ⭐ 低 | 月初一、初八、十四、十五、十八、二十三、二十四、二十八、二十九、三十 |
| **观音斋** | `guanyinzhai.ics` | ⭐⭐ 中 | 农历二月十九、六月十九、九月十九等，有固定的观音纪念日 |
| **佛菩萨圣诞** | `buddhist.ics` | ⭐⭐⭐ 高 | 各佛菩萨圣诞日需要数据表 |
| **二十四节气** | `jieqi.ics` | ⭐ 低 | lunar-python 直接支持节气查询 |

### 11.4 配置联动

用户只需在 `config.yaml` 中启用：

```yaml
zhai_types:
  liuzhai: true                    # → 生成 liuzhai.ics
  shizhai: true                    # → 生成 shizhai.ics
  guanyinzhai: false               # → 暂时不生成
  buddhist_festivals: false
```

脚本自动识别 `ZHAI_TYPES` 注册表中的 `"shizhai"` 配置项，生成相应的 ICS 文件。**不需要改一行核心代码。**

---

## 12. README 结构规划

### 12.1 结构

```markdown
# 🔴 六斋日 ICS 日历

> 一句话介绍
> 鼠标悬停提示

---

## 目录

---

## 📖 简介

- 项目定位
- 适用人群
- 主要功能

---

## 🚀 快速订阅

- 订阅链接（复制即可用）
- iPhone 操作步骤（配截图）
- Mac 操作步骤
- Google Calendar 操作步骤

---

## ⚙️ 自定义配置

- Fork 仓库
- 修改 config.yaml
- 等待 Actions 运行
- 订阅你自己的 Pages 链接

---

## 📅 六斋日说明

- 什么是六斋日
- 日期规则
- 经典依据

---

## 🗺️ 项目路线图

- v1.0 六斋日
- v1.1 自定义提醒
- v1.2 十斋日
- v2.0 佛教节日合集

---

## ❓ FAQ

**Q: 订阅后多久更新？**
A: iOS 约 24h 自动刷新，也可手动下拉刷新。

**Q: 会永久免费吗？**
A: GitHub Pages 和 Actions 对开源项目永久免费。

**Q: 支持 Outlook 吗？**
A: 支持，但 Web 版可能存在兼容性问题。

**Q: 如何反馈问题？**
A: 在 GitHub Issues 提交。

---

## 🤝 贡献指南

- 提交 Issue
- Fork + PR
- 开发指南

---

## 📄 许可证

MIT License
```

---

## 13. 许可证与发布

### 13.1 许可证

**选择 MIT License**，理由：

| 理由 | 说明 |
|:----|:-----|
| 开源友好 | 最宽松的许可证，任何人可自由使用、修改、再发布 |
| 企业友好 | 无任何限制，可商用 |
| 社区共识 | GitHub 上最流行的许可证之一 |

### 13.2 GitHub Release 策略

```
每次 Release 包含：
  - 版本标签（v1.0.0）
  - 生成的 .ics 文件（附件形式）
  - ChangeLog
  - 项目源码快照
```

**发布流程：**

```
1. 更新 CHANGELOG.md
2. 打 tag：git tag v1.0.0 && git push --tags
3. GitHub Actions 自动构建 Release
4. Release 包含：liuzhai.ics + shizhai.ics（如有）
```

**为什么 Release 中也要包含 .ics 文件？**

```
用户即使不搭建 Pages，也可以：
  1. 下载 Release 中的 .ics 文件
  2. 手动导入 iPhone 日历（一次性的，不会自动更新）
```

---

## 14. 版本与升级保障

### 14.1 核心承诺

> **liuzhai.ics 的 URL 永远不变。无论项目如何升级，已订阅的用户不需要做任何操作。**

### 14.2 保障措施

| 场景 | 保障方式 |
|:----|:---------|
| 项目升级 | URL 不变，ICS 文件名不变 |
| 新增斋日类型 | 新增 `shizhai.ics`，不影响已有 `liuzhai.ics` |
| ICS 内容更新 | 使用**稳定的 UID**，日历应用自动合并更新，不会重复显示 |
| config.yaml 升级 | `config_version` 字段控制兼容性，新增字段有默认值 |
| GitHub 用户更名 | Pages URL 会变，但在仓库中提供说明 + 备用方案 |

### 14.3 UID 稳定性

```python
# UID 生成策略：基于日历类型 + 公历日期，永不改变
# 即使项目升级、描述修改，同一个斋日事件的 UID 不变
uid = f"{calendar_type}-{solar_date_str}@{domain}"
# 示例：liuzhai-20260708@liuzhai-ics
```

### 14.4 版本号规范

```
v1.0.0  → 六斋日基础功能
v1.1.0  → 新增 VALARM 自定义
v1.2.0  → 新增十斋日
v2.0.0  → 新增佛教节日合集（重大更新）
```

**版本号对用户透明** — 用户不需要知道版本号，只需要知道订阅 URL 永远有效。

---

## 附录：参考项目

| 项目 | 参考价值 |
|:----|:---------|
| [lanceliao/china-holiday-calender](https://github.com/lanceliao/china-holiday-calender) | ICS + Pages + Actions 成熟架构 |
| [6tail/lunar-python](https://github.com/6tail/lunar-python) | 农历计算核心库 |
| [infinet](https://infinet.github.io/) | 农历 ICS 项目参考 |

---

*文档版本：v2.0 · 设计阶段 · 待实现*
