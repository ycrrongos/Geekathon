# 多日日程页（内嵌 Calendar）

| 项 | 内容 |
|----|------|
| 状态 | 已接入（MD3 Compose） |
| 日期 | 2026-09-13 |
| 模块 | `:app` `ScheduleMd3Screen` + `ScheduleEditor` + `DayScheduleStore` / AI / HabitHook |

## 1. 用户能看到什么

- 「日程」页：MD3 `LargeTopAppBar` + 月历卡 + 贴合列表行 + 新建/AI/导入/习惯按钮（与首页/专注/设置同一套 Reef MD3）
- 月历：MIT [kizitonwose/Calendar](https://github.com/kizitonwose/Calendar) **Compose** 版 `HorizontalCalendar`
- AI 整理、系统日历导入、习惯守护策略、开场前 1 小时锁定：行为不变

入口：

- 底栏「日程」→ `ScheduleTabScreen` / `ScheduleMd3Screen`
- 桌宠菜单等 → `ScheduleActivity`（同一套 Compose）

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| MD3 页面 | `ui/ScheduleTabScreen.kt` → `ScheduleMd3Screen` |
| 编辑/AI/导入对话框 | `ScheduleEditor.kt`（仍用 `dialog_schedule_edit.xml` + AlertDialog） |
| 独立 Activity | `ScheduleActivity`（`setContent` + `ReefTheme`） |
| 旧 XML 工作台 | `ScheduleWorkbench` / `activity_schedule.xml`（已不作为主路径；可对照） |
| 依赖 | `com.kizitonwose.calendar:compose:2.10.1` + `:view` |

## 3. 不要做的事

- 不要只加外链日历 App Intent
- 不要再把底栏日程绑回 sage XML `activity_schedule` 作为主 UI
- 不要为月历再开第二条 specialUse FGS

## 4. 实现要点

- 选中日 → `DayScheduleStore.forDate`；月点 → `countsBetween`
- 列表行用 `HomeNavigationRow` 同款圆角拼接（`spacedBy(2.dp)`）
- 未完成行：上下箭头 → `DayScheduleStore.movePending`（时长不变、紧挨重排）；勾选 → `ScheduleCompleteActivity`（半程后才可）
- 权限返回：`Lifecycle ON_RESUME` → `ScheduleEditor.onResumeImport()`
- 排序/完成详情见 [15-schedule-complete-reorder.md](15-schedule-complete-reorder.md)

## 5. 验证

1. `./gradlew :app:assembleDebug` / `installDebug`
2. 底栏日程：顶栏、月历卡、列表与其他页 MD3 一致
3. 新建 / AI / 导入 / 完成 / 换色仍可用

## 6. 搜索关键词

`ScheduleMd3Screen`、`ScheduleEditor`、`HorizontalCalendar`、`rememberCalendarState`、`schedule_page_title`

相关排障：见 `docs/TROUBLESHOOTING.md`
