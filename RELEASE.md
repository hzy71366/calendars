# v1.0.0 发布说明

> 发布日期：待定
> 首个正式版本，六斋日 ICS 日历自动生成 + GitHub Pages 订阅。

---

## 新增功能

### 🎯 六斋日 ICS 日历

基于农历算法自动计算六斋日（初八、十四、十五、二十三、二十九、三十），
正确处理大月（30天）和小月（29天）的月尾差异。

- 数据来源：《增一阿含经》《毗婆沙论》
- 计算引擎：lunar-python（内置 1900-2100 年农历数据）
- 格式标准：RFC 5545，全天事件（VALUE=DATE）

### 📡 GitHub Pages 自动发布

每次更新自动生成 ICS 文件并部署到 GitHub Pages：

```
https://<用户>.github.io/liuzhai-ics/liuzhai.ics
```

- 每周一自动更新
- 修改 `config.yaml` 自动触发
- 测试失败不部署

### ⚙️ 用户配置系统

通过 `config.yaml` 自定义：

- 日历名称 / 语言 / 标题格式
- 提醒时间（VALARM）
- 生成年份范围
- 所有配置都有默认值，新增字段向前兼容

### 🧪 提醒（VALARM，实验功能）

- 支持 Apple Calendar 全天事件提醒
- 可配置提前天数 + 时刻
- 可关闭

### 🧪 全面测试

53 个自动化测试用例覆盖：

- 六斋日算法（固定日 / 月尾 / 闰月 / 跨年）
- ICS 合规性（RFC 5545 必填字段）
- Round-trip 验证（序列化 → 解析 → 对比）
- 配置加载（默认值 / 向前兼容 / 模板渲染）

---

## 已知限制

| 项目 | 说明 |
|:----|:-----|
| Apple Calendar 真机验证 | 待人工验证 |
| VALARM 兼容性 | Google Calendar / Outlook 提醒可能不触发 |
| 十斋日 | 计划 v1.1.0 |
| 双语标题 | 计划 v1.2.0 |

---

## 如何使用

### 直接订阅

```
1. 打开 iPhone → 设置 → 日历 → 账户 → 添加订阅日历
2. 输入：https://<用户>.github.io/liuzhai-ics/liuzhai.ics
3. 完成
```

### 自定义配置

```
1. Fork 本仓库
2. 编辑 config.yaml
3. 等待 GitHub Actions 自动生成
4. 订阅你的 Pages 链接
```

### 本地运行

```bash
pip install -r requirements.txt
pip install -e .
python scripts/generate_ics.py
```

---

## 文件校验

```
liuzhai.ics SHA-256: （发布时生成）
```

---

## 致谢

- [6tail/lunar-python](https://github.com/6tail/lunar-python) — 农历计算核心库
- [lanceliao/china-holiday-calender](https://github.com/lanceliao/china-holiday-calender) — 架构参考
- 灵隐寺 — 六斋日经典依据
