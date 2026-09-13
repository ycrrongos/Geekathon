# 主页专注统计大卡片

| 项 | 内容 |
|----|------|
| 状态 | 底栏统计已恢复为 Reef **应用用量**；专注统计从 Timer 顶栏进入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` + `:reef` FocusStats / Usage |

## 1. 用户能看到什么

- 底栏「统计」= Reef `UsageScreenWrapper`（应用用量）
- 专注会话统计：专注页 → 番茄钟 → 顶栏图表 → `FocusStatsScreen`

## 2. 入口

底栏 Stats → Usage；Timer 顶栏 → FocusStats。

## 3. 模块与关键类

| 角色 | 路径 |
|------|------|
| 用量 | `UsageScreenWrapper` / `Screen.Usage` |
| 专注统计 | `FocusStatsScreen` / `Screen.FocusStats` |

## 4. 不要做的事

- 不要再把 `FocusStatsScreen(embedded=true)` 绑成底栏第二项

## 5. 验证

1. 底栏统计看到应用用量列表
2. 从专注→番茄钟→图表能进会话统计

## 6. 搜索关键词

`UsageScreenWrapper`、`FocusStatsScreen`、`GuardBottomNavBar`

## 7. 相关文档

- `docs/features/14-md3-home-merge.md`
