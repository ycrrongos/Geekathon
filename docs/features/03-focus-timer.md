# 番茄钟 overlay

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-13 |
| 模块 | `:app` `FocusTimerActivity` + `:reef` `TimerContent` / `OverlayFocusSession` |

## 1. 用户能看到什么

- 桌宠打开番茄钟：出现与**提取文字 / 大爆炸**同款的透明暗幕 + 品牌色描边圆角窗
- 窗内是和应用内「专注 → 番茄钟」**同一份**计时（`OverlayFocusSession.shared`）：开始、暂停、剩余时间、拦截状态两边一致
- 点窗外暗幕或系统返回只关掉这个窗，**不取消**正在走的番茄钟。要停掉，用窗里 Reef 底栏的「取消」
- 主页「专注配置」仍进 Reef 设置页，不是这个窗

## 2. 入口

桌宠菜单 / 控制小窗 / 主页「番茄钟」→ `PetService.openFocusTimer()` → `FocusTimerActivity`。

## 3. 模块与关键类

| 角色 | 路径 |
|------|------|
| 透明独立 task 窗 | `FocusTimerActivity`（`taskAffinity=…focustimer`，主题 `Theme.DesktopPet.BigBang`） |
| Reef 专注面板 | `dev.pranav.reef.timer.OverlayFocusTimerView` |
| 本地会话（写 prefs） | `OverlayFocusSession.shared`（应用内与桌宠窗共用，不要再 `new` 一份） |
| UI | Reef `TimerContent` |
| 拦截 | `prefs["focus_mode"]` → `BlockerService` |

## 4. 权限

不依赖悬浮窗即可打开（Activity）。拦截另需无障碍 + 用量访问。

## 5. 不要做的事

- **不要** `startForegroundService(FocusModeService)`（与 PetService 抢 specialUse FGS）
- **不要**再把 Compose `TimerContent` 直接挂到 `PetService` 的 `TYPE_APPLICATION_OVERLAY` 上（SavedState/Lifecycle 易崩）
- **不要**关窗或 `onDestroy` 时 `cancel()` 清会话（会把应用内正在走的番茄钟一起停掉）
- 不要恢复旧的 `PullTabView` + `AnalogTimerView`

## 6. 实现要点

- Activity 自身即 Lifecycle / SavedState / OnBackPressed owner，再 `OverlayFocusTimerView.bindTreeOwners(...)`
- 开始会话：写 prefs + 本地 Handler；**不**启 FocusModeService
- 完成奖励在 `GuardInitProvider` 里注册一次，不要在两个 Activity 各挂一份（会加两次心情）
- 结束时 `ACTION_SHOW_PET` 再显示桌宠；关窗不 `cancel()`

## 7. 验证

1. `./gradlew :app:assembleDebug`
2. 开桌宠 → 番茄钟：暗幕+圆角窗，内为 Reef 专注 UI，不崩
3. 开始简单计时后分心应用被拦；取消/结束后面板可再开

## 8. 搜索关键词

`FocusTimerActivity`、`OverlayFocusTimerView`、`OverlayFocusSession`、`TimerContent`、`focus_mode`、`FocusModeService`

## 9. 相关文档

- `docs/TROUBLESHOOTING.md`：番茄钟 Service overlay Compose 崩溃；`2026-09-12 — 番茄钟 overlay 启动即崩溃`
- `docs/features/06-reef-focus.md`
- `AGENTS.md`：一条 specialUse FGS
