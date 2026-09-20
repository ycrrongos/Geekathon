# MD3 主页合入 Reef 壳

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` + `:reef` |

## 1. 用户能看到什么

- 功能一句话：守伴启动页为五栏 MD3 底栏——**首页 / 日程 / 统计 / 专注 / 设置**。
- 首页：桌宠陪伴 + 分组行（好友 / 作息 / 闪记 / 定制形象）+ 闪记列表。
- 日程：嵌入原多日日程页（`ScheduleWorkbench`），页内有「习惯守护」入口。
- 统计：Reef **应用用量**（`UsageScreenWrapper`），不是专注统计大卡片。
- 专注：Reef 专注枢纽（长按环、用量/白名单、计划/网站/正念/番茄钟入口）；点番茄钟进 `TimerContent` + `OverlayFocusSession`。
- 设置：Reef 设置 + 脚注分组。**桌宠**（定制形象、待办、陪伴偏好、快捷手势）、**好友**、**习惯**、**AI**（接口 `AiApiActivity`，快捷整理 `BigBangShortcutsActivity`）、**闪记**（只打开已有写作入口，不改闪记界面）、**权限与关于**。同一项在对应功能页也能进：好友页有形象卡和习惯守护入口；日程页有习惯守护；待办是 `PetPanelActivity` 全页。提取文字词块页齿轮也进快捷整理。
- 习惯守护、待办小窗已换成 MD3（`ReefTheme` + `Scaffold`）。透明工具页（大爆炸、番茄钟窗、选时/选麦、闪记播放）保持原样。
- 不做什么：不启 `FocusModeService`；不跳 AppIntro/Discord/捐赠；品牌「守伴」；**不要改闪记 overlay / 卡片 / 胶囊按钮的布局与 drawable**。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 主壳 | `MainActivity.kt`（`AppCompatActivity` + NavHost） |
| 五栏 | `ui/GuardBottomNavBar.kt` |
| 首页 | `ui/GuardCompanionHome.kt` → `GuardHomeScreen` |
| 日程 Tab | `ui/ScheduleTabScreen.kt` + `ScheduleWorkbench.kt` |
| 专注枢纽 | `Screen.FocusHub` → `HomeContent(skipPromos)` |
| 设置脚注 | `GuardSettingsFooter` → `SettingsContent(mainFooter=…)` |

## 3. 权限

- 与旧主页相同；权限状态文案在**设置**页底部。

## 4. 实现要点

- 底栏索引：0 Home / 1 Schedule / 2 Usage / 3 FocusHub / 4 Settings
- 功能行用 `HomeNavigationRow` + `spacedBy(2.dp)` 贴合
- 专注统计仍可从 Timer 顶栏图表进入 `FocusStatsScreen`（非底栏）

## 5. 不要做的事

- 不要把底栏「统计」改回 `FocusStatsScreen(embedded)`
- 不要在 Focus 页 `startForegroundService(FocusModeService)`
- 不要把陪伴偏好再堆回首页（设置「桌宠」分组里即可）
- 不要改闪记 UI（`FlashNoteOverlay`、`overlay_flash_*.xml`、`flash_chip_button*.xml`）

## 6. 验证

- `./gradlew :app:assembleDebug`
- 真机：五栏切换；首页无番茄钟/日程入口；统计为用量；专注页有 Reef 功能堆；设置里有手势/偏好

## 7. 搜索关键词

`GuardBottomNavBar`、`GuardHomeScreen`、`FocusHub`、`ScheduleTabScreen`、`GuardSettingsFooter`、`mainFooter`、`settings_section_pet`、`HabitGuardianScreen`、`PetPanelActivity`

## 8. 相关文档

- `12-schedule-page.md`、`13-home-focus-stats.md`、`03-focus-timer.md`
