# 主页专注统计大卡片

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` MainActivity + `:reef` FocusStats |

## 1. 用户能看到什么

- 守伴主页在「喂食/摸摸/小憩」下方有一张约 520dp 高的大卡片，内嵌 Reef **专注统计**（日/周/月、图表、会话列表）
- 点会话可进详情；卡片内可独立滚动，不与主页 NestedScrollView 抢手势
- 无返回键（`embedded=true`）；标题用「统计」

## 2. 入口

主页滚动即见；数据来自 `FocusStats`（与 Reef 专注配置里统计同源）。

## 3. 模块与关键类

| 角色 | 路径 |
|------|------|
| 嵌入 View | `dev.pranav.reef.ui.FocusStatsEmbedView` |
| UI | `FocusStatsScreen(embedded = true)` |
| 宿主 | `MainActivity.bindFocusStatsCard()` / `activity_main.xml` `@id/focusStatsCard` |

## 4. 不要做的事

- 不要在 `:app` 里直接写 Compose（用 EmbedView）
- 不要把统计改成跳转 Reef MainActivity 代替嵌入
- 品牌仍是「守伴」；Reef MIT 署名仍在主页底部

## 5. 验证

1. `./gradlew :app:assembleDebug`
2. 打开主页，下滑见统计大卡片；切换 Daily/Weekly/Monthly
3. 卡片内列表可滑；主页外层仍可滑

## 6. 搜索关键词

`FocusStatsEmbedView`、`focusStatsCard`、`FocusStatsScreen`、`embedded`

## 7. 相关文档

- `docs/features/06-reef-focus.md`
- `docs/features/07-miku-ui.md`
