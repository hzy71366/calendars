# 🔴 六斋日 ICS 日历

生成 iPhone / Google Calendar 可直接订阅的六斋日 ICS 日历。

[![Publish ICS Calendar](https://github.com/<USER>/liuzhai-ics/actions/workflows/publish.yml/badge.svg)](https://github.com/<USER>/liuzhai-ics/actions/workflows/publish.yml)

---

## 快速订阅

订阅链接（将 `<USER>` 替换为你的 GitHub 用户名）：

```
https://<USER>.github.io/liuzhai-ics/liuzhai.ics
```

### iPhone / iPad

```
设置 → 日历 → 账户 → 添加订阅日历
→ 输入上方 URL
→ 完成
```

### Mac

```
日历 App → 文件 → 新建日历订阅
→ 输入上方 URL
→ 完成
```

### Google Calendar

```
其他日历 → 通过网址添加
→ 输入上方 URL
→ 完成
```

> 日历自动更新频率：iOS 约 24h，Google Calendar 约 12h。

---

## 自定义配置

1. Fork 此仓库
2. 编辑 `config.yaml`
3. GitHub Actions 自动重新生成并发布
4. 订阅 `https://<你的用户名>.github.io/liuzhai-ics/liuzhai.ics`

### config.yaml 支持

| 配置项 | 默认值 | 说明 |
|:------|:------|:-----|
| `calendar_name` | `六斋日` | 日历名称 |
| `language` | `zh-CN` | `zh-CN` / `en` / `bilingual` |
| `event_title` | `{emoji} {name} · 农历{lunar}` | 标题模板 |
| `event_description` | `农历{lunar}\n六斋日，过午不食…` | 描述模板 |
| `emoji` | `🔴` | 标题图标 |
| `alarm.enabled` | `true` | 是否开启提醒 |
| `years.ahead` | `5` | 生成未来 N 年 |

### 标题模板变量

| 变量 | 示例 | 说明 |
|:----|:----|:-----|
| `{emoji}` | `🔴` | 图标 |
| `{name}` | `六斋日` | 日历名称 |
| `{lunar}` | `八月初八` | 农历日期 |
| `{solar}` | `2026-09-18` | 公历日期 |

---

## ⚠️ 提醒功能（VALARM）说明

ICS 文件包含 VALARM 提醒组件（默认开启），但各日历客户端的支持情况**不同**：

| 客户端 | 提醒支持 | 说明 |
|:------|:-------:|:-----|
| Apple Calendar (iOS/macOS) | ✅ 支持 | 全天事件的 VALARM 正常触发 |
| Google Calendar | ⚠️ 部分支持 | 订阅日历的提醒可能不触发 |
| Microsoft Outlook | ⚠️ 部分支持 | 依赖客户端版本 |

**VALARM 在本项目中标记为实验功能。** 如果提醒对你不是必需的，可在 `config.yaml` 中关闭：

```yaml
alarm:
  enabled: false
```

---

## 本地运行

```bash
pip install -r requirements.txt
pip install -e .
python scripts/generate_ics.py
```

输出文件位于 `docs/liuzhai.ics`。

---

## 项目结构

```
liuzhai-ics/
├── .github/workflows/         ← CI + 自动发布
│   ├── test.yml               ← 测试
│   └── publish.yml            ← 生成 + 部署到 Pages
├── src/liuzhai_ics/           ← Python 包
│   ├── __init__.py
│   ├── zhai_types.py          ← 六斋日判定
│   ├── generator.py           ← ICS 生成器
│   └── config.py              ← 配置加载 + 模板
├── scripts/generate_ics.py    ← 入口脚本
├── tests/                     ← 测试
├── config.yaml                ← 用户配置
├── docs/                      ← GitHub Pages 根目录
│   ├── liuzhai.ics            ← 生成的日历文件
│   └── VERIFY.md              ← 验证指南
├── DESIGN.md                  ← 设计文档
└── README.md
```

---

## 路线图

- [x] 六斋日 ICS 生成
- [x] 自动发布到 GitHub Pages
- [x] 用户配置系统
- [ ] 十斋日支持
- [ ] 双语标题
- [ ] 佛教节日合集

---

## 许可证

MIT
