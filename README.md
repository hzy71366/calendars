# 🔴 六斋日 ICS 日历

> 自动生成、自动更新的六斋日 ICS 日历，iPhone / Mac / Google Calendar 一键订阅。

[![CI](https://github.com/<USER>/liuzhai-ics/actions/workflows/test.yml/badge.svg)](https://github.com/<USER>/liuzhai-ics/actions/workflows/test.yml)
[![Publish](https://github.com/<USER>/liuzhai-ics/actions/workflows/publish.yml/badge.svg)](https://github.com/<USER>/liuzhai-ics/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](pyproject.toml)
[![Cal](https://img.shields.io/badge/Cal-RFC%205545-green.svg)](https://tools.ietf.org/html/rfc5545)

---

## 目录

- [快速订阅](#快速订阅)
- [自定义配置](#自定义配置)
- [本地运行](#本地运行)
- [项目结构](#项目结构)
- [验证](#验证)
- [提醒功能说明](#提醒功能说明)
- [路线图](#路线图)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 快速订阅

> 将以下链接（替换 `<USER>` 为你自己的 GitHub 用户名）添加到你的日历 App。

```
https://<USER>.github.io/liuzhai-ics/liuzhai.ics
```

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

### 效果预览

![日历预览](docs/screenshot.png)

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
git clone https://github.com/<USER>/liuzhai-ics.git
cd liuzhai-ics

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
liuzhai-ics/
├── .github/workflows/
│   ├── test.yml              ← CI 测试
│   └── publish.yml           ← 自动生成 + 发布到 Pages
├── src/liuzhai_ics/          ← Python 包
│   ├── zhai_types.py         ← 六斋日判定
│   ├── generator.py          ← ICS 生成器
│   └── config.py             ← 配置加载 + 模板
├── scripts/generate_ics.py   ← 入口脚本
├── tests/                    ← 53 个测试用例
├── config.yaml               ← 用户配置
├── docs/
│   ├── liuzhai.ics           ← 生成的日历文件（订阅此文件）
│   ├── screenshot.png        ← 效果截图
│   └── VERIFY.md             ← 验证指南
├── DESIGN.md                 ← 设计文档
├── RELEASE.md                ← 发布说明
├── CONTRIBUTING.md           ← 贡献指南
├── SECURITY.md               ← 安全策略
├── CHANGELOG.md              ← 版本历史
├── README.md
└── LICENSE
```

---

## 验证

完整的 Apple Calendar 验证清单请见 [docs/VERIFY.md](docs/VERIFY.md)。

验证内容：

- [x] ICS 文件符合 RFC 5545 标准
- [x] UID 稳定（同日期永不改变）
- [x] Round-trip 序列化/反序列化正确
- [x] 每个农历月恰好 6 个斋日
- [ ] ~~Apple Calendar 真机显示效果~~（待人工验证）

---

## 提醒功能说明

ICS 文件包含 VALARM 提醒组件，各客户端支持情况：

| 客户端 | 提醒支持 | 说明 |
|:------|:-------:|:-----|
| Apple Calendar (iOS/macOS) | ✅ 支持 | 全天事件提醒正常触发 |
| Google Calendar | ⚠️ 部分支持 | 订阅日历提醒可能不触发 |
| Microsoft Outlook | ⚠️ 部分支持 | 依赖客户端版本 |

> VALARM 为实验功能。不需要提醒可在 `config.yaml` 中关闭：
> ```yaml
> alarm:
>   enabled: false
> ```

---

## 路线图

- [x] v1.0.0 — 六斋日 ICS 生成 + GitHub Pages 自动发布
- [x] 用户配置系统（config.yaml + 模板变量）
- [x] VALARM 提醒（实验功能）
- [ ] v1.1.0 — 十斋日支持
- [ ] v1.2.0 — 双语标题（中文/英文）
- [ ] v2.0.0 — 佛教节日合集（佛菩萨圣诞、观音斋等）

---

## 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 安全

发现安全漏洞？请参考 [SECURITY.md](SECURITY.md) 的处理流程。

---

## 许可证

[MIT](LICENSE)
