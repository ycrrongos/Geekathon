# 日程排序与完成复盘

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` `DayScheduleStore` / `ScheduleCompleteActivity` / `ScheduleEndScheduler` |

## 1. 用户能看到什么

- **同日排序**：列表左侧 ≡ 手柄，**长按拖动**调整未开始日程顺序；时长不变，时间窗自动重排。
- **半程后才能完成**：未到 `start + duration/2` 时点完成会提示「进行到一半后才能完成」。
- **完成页**：滑条选完成程度 0–100、必填经验；可点麦克风录音 → SenseVoice 转写 → AI（或本地规则）填程度与经验。
- **结束通知**：日程 `endMinutes` 到点发通知「日程结束了」，点通知进完成页。

入口：

- 底栏/独立日程页列表行：上下移、勾选完成 → `ScheduleCompleteActivity`
- 左侧日程 overlay 完成按钮 → 同上
- 闹钟 `ScheduleEndReceiver` → 通知 → 点进完成页

不做什么：

- 不在未过半时允许完成
- 不新增第二条 specialUse FGS / 第二个无障碍服务
- 不把完成页做成全屏 overlay

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 数据与排序/完成 | `DayScheduleStore.kt`（`movePending` / `complete` / `canCompleteNow`） |
| 完成 UI | `ScheduleCompleteActivity.kt` |
| 结束闹钟/通知 | `ScheduleEndScheduler.kt`、`ScheduleEndReceiver`、`ScheduleBootReceiver` |
| 语音填完成 | `ScheduleLlmClient.parseCompletionFromVoice` |
| 列表 UI | `ui/ScheduleTabScreen.kt` `ScheduleRowCard` |
| Overlay | `ScheduleOverlay.kt` done 按钮 |

| 路径 | 改动类型 | 说明 |
|------|----------|------|
| `day_schedules.db` v2 | 迁移 | `completion_degree`、`experience_note` |
| `AndroidManifest.xml` | 注册 | Complete Activity + End/Boot receivers；`RECEIVE_BOOT_COMPLETED`、exact alarm |
| `GuardInitProvider` | 启动 | `ScheduleEndScheduler.rescheduleAll` |

不要改：完成逻辑不要绕过 `canCompleteNow`；闹钟不要挂到 `PetService`。

## 3. 权限

- `POST_NOTIFICATIONS`（结束通知）
- `RECEIVE_BOOT_COMPLETED`（开机重挂闹钟）
- `SCHEDULE_EXACT_ALARM` / `USE_EXACT_ALARM`（到点精确提醒）
- 语音填写：`RECORD_AUDIO` + SenseVoice 模型 pack（同闪记）

## 4. 实现要点

- `movePending(date, id, ±1)`：只重排**尚未开始**的 pending；已开始条目时间固定；任一条 `isPolicyLocked()` **不再**挡住整天排序。
- `canCompleteNow`：过去日可完成；当日需 `nowMins >= midpointMinutes()`。
- `complete`：经验非空；写 DONE + degree + note；食物 +1 一次；清结束通知去重键。
- `rescheduleAll`：先取消当日全部闹钟，再只给 pending 挂；已过 end 立即 `notifyEnded`（prefs `schedule_end_notified` 去重）。
- 语音：`HabitLlmClient.chatJson`；无 Key 时 `localCompletionFromVoice`。

## 5. 不要做的事

- 不要用 `FocusModeService` / 第二条 specialUse 做日程提醒
- 不要把排序改成改时长或留空隙（产品约定：时长不变、紧挨重排）
- 不要跳过半程检查直接 `status=done`

## 6. 验证

- 编译：`./gradlew :app:assembleDebug`（在 `GuardPet/`）
- 真机：同日两条 pending → 上移下移看时间窗对调；未到半程点完成应被拦；过半程进完成页提交；等到结束或临时把 end 调到近处看通知。

## 7. 搜索关键词

`movePending`、`canCompleteNow`、`ScheduleCompleteActivity`、`ScheduleEndScheduler`、`parseCompletionFromVoice`、`completion_degree`、`schedule_complete_too_early`

## 8. 相关文档

- `docs/features/11-day-schedule.md`、`12-schedule-page.md`
- `docs/TROUBLESHOOTING.md`：日程结束通知 / 半程完成
- `AGENTS.md`：单一 specialUse FGS、文档与排障约定
