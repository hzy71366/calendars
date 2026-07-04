# Release v1.0.0 Checklist

> 发布前逐项确认。

## 代码

- [ ] 所有测试通过：`python -m pytest`
- [ ] CI 通过（GitHub Actions test.yml）
- [ ] Python 3.10、3.11、3.12 兼容
- [ ] 无未合并的 PR
- [ ] 工作区干净（`git status` 无未跟踪文件）

## 文档

- [ ] README.md 完整、准确
- [ ] CHANGELOG.md 已更新
- [ ] CONTRIBUTING.md 已更新
- [ ] SECURITY.md 已更新
- [ ] RELEASE.md 已完成

## ICS 文件

- [ ] `docs/liuzhai.ics` 已生成
- [ ] ICS 文件通过 RFC 5545 基本校验
- [ ] iOS 订阅测试通过
- [ ] Mac 订阅测试通过

## 基础设施

- [ ] GitHub Pages 已启用（Source = GitHub Actions）
- [ ] publish.yml 工作流运行成功
- [ ] Pages URL 可以访问：`https://<用户>.github.io/liuzhai-ics/liuzhai.ics`

## 发布

- [ ] 打 Tag：`git tag -a v1.0.0 -m "v1.0.0: 六斋日 ICS 日历" && git push --tags`
- [ ] GitHub Release 创建
- [ ] Release 包含：liuzhai.ics（附件）+ RELEASE.md
