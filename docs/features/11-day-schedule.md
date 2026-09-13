# 今日日程（富日程）

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app`（存储 / overlay / LLM）+ `:reef` HabitHook 时段拦截 |

## 1. 用户能看到什么

- 打开闪记时：**左侧今日日程胶囊** + **右侧闪记**（同开同关）
- 左右叠层：点哪边（或音量加减语音输入）哪边在上层；切上层时，将变下层的一侧先收到屏幕边缘，再从边缘展开到另一边下面
- 左侧开合动画：从左向右展开、收起向左收回（Overshoot / Accelerate）；卡片上下展开与右侧闪记相同
- 手动拖拽选时间（`ScheduleTimePickActivity`）时**隐藏左右悬浮窗**，关掉时间页再恢复（语音补时间不隐藏）
- 录入：
  - 左侧「从日历导入」（需 `READ_CALENDAR`）
  - 闪记分类选「日程」→ 按钮「保存日程」→ AI 可拆出**多天**条目；**只写 DayScheduleStore，不进闪记列表**；补时间面板可改每条日期
- 日程页「AI 整理」同样可创建/修改非今天日程
- 颜色：新建从 Google Calendar 风格**亮色表**随机取色；列表点色条 / overlay「换色」/ 编辑对话框色点可改
- 缺时间：补时间面板——**日期** / **时间选择器** 或 **按住语音**
- App 策略：展开卡片后 **多选允许/禁止**，或 **按住语音让 AI 填**；写入前合理性审查，不合理拒绝
- 锁定：仅**当天**且 `now >= start - 1h` 后不可再改时间/App 策略；未来日期可自由改（颜色仍可改）
- 完成：卡片变绿，`foodCount +1`
- 未完成色：亮色表随机（完成态强制绿）

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 存储 | `DayScheduleStore` / `DaySchedule`（`day_schedules.db`）；色板 `DayScheduleColor` |
| 日历 | `CalendarScheduleImporter`、`CalendarPermissionActivity` |
| AI | `ScheduleLlmClient`（复用 `HabitLlmClient`） |
| 左侧 UI | `ScheduleHud` / `ScheduleOverlay`、`overlay_day_schedules.xml` |
| 单窗宿主 | `DualOverlayShell` + `PassthroughFrameLayout`（左右共一个 overlay） |
| 叠层协调 | `OverlayLayerCoordinator`（elevation 切层 / 收边再展开 / 选时间隐藏） |
| 手动选时 | `ScheduleTimePickActivity`（隐藏 overlay） |
| 闪记接入 | `FlashNoteHud` 打开时拉起日程；`FlashNoteOverlay.saveComposer` 日程分类只走 AI / `DayScheduleStore` |
| 拦截 | `HabitGuardian.evaluateActiveDaySchedule` |
| 初始化 | `GuardInitProvider` → `DayScheduleStore.init` |

## 3. 权限

- `READ_CALENDAR`（导入时经 `CalendarPermissionActivity` 申请）
- 悬浮窗（与闪记相同）
- 麦克风（语音补时间/策略，复用闪记录音 + SenseVoice）

## 4. 不要做的事

- 不新开 specialUse FGS / 第二个无障碍
- 左侧窗不单独再挂一条 TYPE_APPLICATION_OVERLAY（必须进 `DualOverlayShell`）
- **不要为左右切层做 `WindowManager.removeView`+`addView`**（会闪、丢 IME、点不动）
- 不把审查逻辑写进 `BlockerService`
- 不要用全屏 overlay 挡选时间；用 Activity + `hideForTimePicker`

## 5. 实现要点

- 交互：根布局 `OverlaySideRoot.dispatchTouchEvent` 任意 `ACTION_DOWN` 即 `noteUserOn`（不要求业务有反馈）；已在顶层则直接忽略
- 切层：`retractToEdge` → `DualOverlayShell.bringSideToFront`（elevation）→ `expandFromEdge`
- 宿主全屏透明，空白触摸放行（`PassthroughFrameLayout`）；IME focus 改宿主 flags
- 左滑入：`translationX = -slideDistance`；右滑入为正；插值器与闪记一致

## 6. 搜索关键词

`DualOverlayShell`、`PassthroughFrameLayout`、`DayScheduleStore`、`DayScheduleColor`、`ScheduleHud`、`ScheduleDateParse`、`ScheduleLlmClient`、`retractToEdge`、`bringSideToFront`、`save_schedule`

相关排障：见 `docs/TROUBLESHOOTING.md`（双窗 remove/add 闪烁、顶层再点丢焦点）
