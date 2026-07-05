# 🙏 佛教日历 ICS 订阅

> 自动生成、自动更新的佛教日历 ICS 订阅，iPhone / Mac / Google Calendar 一键订阅。
> 包含六斋日、十斋日、佛菩萨圣诞（26 个节日）三个日历。

[![CI](https://github.com/hzy71366/buddhist-calendars/actions/workflows/test.yml/badge.svg)](https://github.com/hzy71366/buddhist-calendars/actions/workflows/test.yml)
[![Publish](https://github.com/hzy71366/buddhist-calendars/actions/workflows/publish.yml/badge.svg)](https://github.com/hzy71366/buddhist-calendars/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](pyproject.toml)
[![Cal](https://img.shields.io/badge/Cal-RFC%205545-green.svg)](https://tools.ietf.org/html/rfc5545)

---

## 目录

- [快速订阅](#快速订阅)
- [自定义配置](#自定义配置)
- [本地运行](#本地运行)
- [项目结构](#项目结构)
- [提醒功能说明](#提醒功能说明)
- [路线图](#路线图)
- [许可证](#许可证)

---

## 快速订阅

| 日历 | 订阅链接 |
|:----|:---------|
| 📿 **六斋日** | `https://hzy71366.github.io/buddhist-calendars/liuzhai.ics` |
| 🪷 **十斋日** | `https://hzy71366.github.io/buddhist-calendars/shizhai.ics` |
| 🙏 **佛菩萨圣诞** | `https://hzy71366.github.io/buddhist-calendars/buddhist.ics` |

### iPhone / iPad

```
设置 → 日历 → 账户 → 添加订阅日历 → 输入 URL → 完成
```

### Mac

```
日历 App → 文件 → 新建日历订阅 → 输入 URL → 完成
```

### Google Calendar

```
其他日历 → 通过网址添加 → 输入 URL → 添加
```

> 日历自动更新频率：iOS 约 24h 自动刷新，Google Calendar 约 12h。

---

## 自定义配置

想修改提醒时间、标题格式、语言？只需三步：

```
1. Fork 本仓库
2. 编辑 config.yaml
3. GitHub Actions 自动重新生成并发布
```

### config.yaml 配置项

| 配置项 | 默认值 | 说明 |
|:------|:------|:-----|
| `calendar_name` | `六斋日` | 日历名称，显示在订阅列表中 |
| `language` | `zh-CN` | `zh-CN` / `en` / `bilingual` |
| `event_title` | `{emoji} {name} · 农历{lunar}` | 标题模板 |
| `event_description` | `农历{lunar}...` | 描述模板 |
| `alarm.enabled` | `true` | 是否开启提醒 |
| `alarm.days_before` | `1` | 提前几天提醒 |
| `alarm.time` | `09:00` | 提醒时刻 |
| `emoji` | `🔴` | 标题图标 |
| `years.ahead` | `5` | 生成未来 N 年的日历 |

### 标题模板变量

```
{emoji} → 图标 (🔴)
{name}  → 日历名称 (六斋日)
{lunar} → 农历日期 (八月初八)
{solar} → 公历日期 (2026-09-18)
```

---

## 本地运行

```bash
# 克隆
git clone https://github.com/hzy71366/buddhist-calendars.git
cd buddhist-calendars

# 安装
pip install -r requirements.txt
pip install -e .

# 生成
python scripts/generate_ics.py

# 测试
python -m pytest
```

---

## 项目结构

```
buddhist-calendars/
├── .github/workflows/
│   ├── test.yml              ← CI 测试
│   ├── publish.yml           ← 自动生成 + 发布到 Pages
│   └── release.yml           ← Release 自动上传附件
├── src/calendar_engine/
│   ├── core/
│   │   ├── config.py         ← 配置加载 + 模板
│   │   ├── generator.py      ← ICS 生成器
│   │   ├── registry.py       ← 日历注册表
│   │   └── types.py          ← 日历类型定义
│   ├── calendars/
│   │   ├── liuzhai.py        ← 六斋日判定
│   │   ├── shizhai.py        ← 十斋日判定
│   │   ├── buddhist.py       ← 佛菩萨圣诞判定
│   │   └── solar_terms.py    ← 节气
│   └── utils/
├── scripts/
│   └── generate_ics.py       ← 入口脚本
├── tests/                    ← 测试用例
├── config.yaml               ← 用户配置
├── docs/
│   ├── index.html            ← Pages 首页
│   ├── liuzhai.ics           ← 六斋日（订阅此文件）
│   ├── shizhai.ics           ← 十斋日（订阅此文件）
│   ├── buddhist.ics          ← 佛菩萨圣诞（订阅此文件）
│   └── .nojekyll
├── README.md
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

---


## 提醒功能说明

ICS 文件包含 VALARM 提醒组件。日历订阅客户端对 VALARM 的支持因实现而异。

---

## 路线图

- [x] v1.0.0 — 六斋日 ICS 生成 + GitHub Pages 自动发布
- [x] 用户配置系统（config.yaml + 模板变量）
- [x] VALARM 提醒
- [x] 十斋日支持
- [x] 佛菩萨圣诞（26 个节日）
- [ ] 双语标题（中文/英文）

---

## 许可证

[MIT](LICENSE)
