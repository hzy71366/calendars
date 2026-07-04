# Changelog

## 1.0.0 (Unreleased)

### 新增
- 六斋日算法：基于 lunar-python，支持大月/小月/闰月
- ICS 生成器：RFC 5545 合规，全天事件（VALUE=DATE）
- 用户配置系统：config.yaml + 模板变量（{emoji} {name} {lunar} {solar}）
- GitHub Pages 自动发布：Actions 定时生成 + 部署
- VALARM 提醒：实验功能，Apple Calendar 支持
- 多日历架构：ZHAI_TYPES 注册表，十斋日等扩展无需改核心

### 测试
- 53 个自动化测试用例
- 算法：固定日/月尾/闰月/跨年/每月计数
- ICS：RFC 5545 必填字段/Round-trip/UID 稳定性
- 配置：默认值/向前兼容/模板渲染

### 文档
- README、CONTRIBUTING、SECURITY、RELEASE 文档
- Release Checklist
- Pages 首页（docs/index.html）
- 截图占位（docs/screenshot.svg）
