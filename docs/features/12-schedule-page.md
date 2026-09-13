# 多日日程页（内嵌 Calendar）

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` `ScheduleActivity` + `DayScheduleStore` / AI / HabitHook |

## 1. 用户能看到什么

- 独立「日程」页：月历选日 + 当日列表 + 新建/编辑/完成/删除
- 月历组件**内嵌** MIT 开源库 [kizitonwose/Calendar](https://github.com/kizitonwose/Calendar)（Gradle `com.kizitonwose.calendar:view`），不是外链另一个日历 App
- AI 整理：自然语言创建/改/完成/删除，**可指定其他日期**（复用 DeepSeek；无 Key 则本地启发式 + `ScheduleDateParse`）
- 系统日历导入：未来约 30 天
- 习惯守护：日程上的 allow/block 包名仍由 `HabitGuardian.evaluateActiveDaySchedule` 在**进行中**时段优先拦截
- 开场前 1 小时锁定时间与 App 策略（与今日 overlay 一致）

入口：

- 主页「日程」按钮
- 桌宠功能菜单「日程」
- 页内可跳转「习惯守护设置」

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 页面 | `ScheduleActivity`、`activity_schedule.xml`、`item_schedule_row.xml`、`item_schedule_calendar_day.xml`、`dialog_schedule_edit.xml` |
| 月历库 | `com.kizitonwose.calendar:view:2.10.1`（MIT） |
| 存储 | `DayScheduleStore.forDate` / `countsBetween` / `between` |
| 导入 | `CalendarScheduleImporter.importUpcoming` |
| AI | `ScheduleLlmClient.applyInstruction` |
| 拦截 | `HabitGuardian.evaluateActiveDaySchedule`（今日进行中） |
| 今日 overlay | 仍见 `11-day-schedule.md`（闪记旁左侧胶囊） |

## 3. 不要做的事

- 不要只加「打开外部日历 App」的 Intent 冒充内嵌
- 不要为切层/月历再开第二条 specialUse FGS 或第二个无障碍
- 不要把审查写进 `BlockerService`

## 4. 实现要点

- 选中日点 → `DayScheduleStore.forDate`；月点 → `countsBetween`
- 保存走 `ScheduleLlmClient.reviewChange`（create/time/policy）
- 权限：`CalendarPermissionActivity.EXTRA_RETURN_TO_SCHEDULE` 时不回调 overlay 导入，由日程页 `onResume` 导入

## 5. 验证

1. `./gradlew :app:assembleDebug`
2. 主页/桌宠菜单打开日程页，翻月、选日、新建、AI 一句「明天 10:00 开会」
3. 给进行中日程填禁止包名，确认 Habit 拦截话术含日程标题

## 6. 搜索关键词

`ScheduleActivity`、`kizitonwose`、`applyInstruction`、`importUpcoming`、`countsBetween`、`schedule_page_title`

相关排障：见 `docs/TROUBLESHOOTING.md`
