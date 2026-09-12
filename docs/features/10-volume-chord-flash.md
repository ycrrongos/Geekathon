# 音量加减和弦打开闪记

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:reef`（共用 `BlockerService`） |

## 1. 用户能看到什么

- 功能一句话：同时按下音量加 + 音量减，短按打开闪记写作窗；长按（约 450ms）直接进入录音，松开两键后结束录音并走原有转写逻辑。
- 入口：任意界面（需已开启守伴无障碍）；不占用桌宠快捷手势位。
- 不做什么：不新开无障碍 / FGS；和弦路径不调系统音量、不弹音量条。单独音量由本类经 `AudioManager` 代调（因需成对消费按键）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 和弦检测 | `GuardPet/app/.../VolumeChordFlashNote.kt` |
| 闪记入口 | `FlashNoteHud.beginVolumeHoldRecord` / `endVolumeHoldRecord` |
| Hook | `GuardPet/reef/.../KeyEventHook.kt` |
| 无障碍 | `BlockerService.onKeyEvent` + `blocker_configuration.xml`（`flagRequestFilterKeyEvents`） |

不要改、以及为什么：

- 不要再注册第二个 AccessibilityService。
- 不要对音量键「只消费 DOWN 不消费 UP」（或反过来）：系统会认为键一直按着。
- 不要在和弦已成立后还 `adjustSuggestedStreamVolume(..., FLAG_SHOW_UI)`。

## 3. 权限

- 无障碍（读键）：已有 `BlockerService`；改 XML 后可能需用户关开一次无障碍。
- 悬浮窗 + 麦克风：与闪记相同；缺麦时走 `MicPermissionActivity`。

## 4. 实现要点

- `GuardInitProvider` 注册 `KeyEventHook.filter` → `VolumeChordFlashNote.onKeyEvent`。
- **所有**音量 DOWN/UP 都 `return true` 消费，再用 `AudioManager.adjustSuggestedStreamVolume` 代发单键音量（约 160ms 检测窗：窗内出现第二键则进和弦，不调音量、不弹条）。
- 过滤键后系统往往不再发 `repeatCount`，单键长按由本类 `Handler` 每 ~85ms 连调，松手 `stopVolumeRepeat`。
- 和弦 450ms 后 `beginVolumeHoldRecord`；两键都 UP → 短按 `startCapture`，长按 `endVolumeHoldRecord`。
- `volumeHoldRecording` 标记避免与普通录音按钮互相干扰。

## 5. 不要做的事

- 不要用 MediaSession / Notification 监听音量替代无障碍（后台不可靠）。
- 不要把模型 / ASR 逻辑塞进 `:reef`。

## 6. 验证

- 编译：`./gradlew :app:assembleDebug`
- 真机：开无障碍与悬浮窗 → 同时点按音量加减 → 闪记写作窗；长按两键说话 → 松开后停止并转写（有模型包时）。单独按音量仍应调音量。

## 7. 搜索关键词

`VolumeChordFlashNote`、`KeyEventHook`、`FLAG_REQUEST_FILTER_KEY_EVENTS`、`beginVolumeHoldRecord`、`volume_chord`、`volume_hold`

## 8. 相关文档

- `docs/features/04-flash-note.md`
- `docs/TROUBLESHOOTING.md`：`2026-09-12 — 音量和弦闪记需关开无障碍`
- `AGENTS.md`：全应用只有一个无障碍服务
