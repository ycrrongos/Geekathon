# 拦截气泡（桌宠说话）

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:reef`（HabitHook） |

## 1. 用户能看到什么

- 作息/番茄钟拦截时，**不再弹系统通知**（有悬浮窗时），改为桌宠头顶奶油色说话气泡，文案偏软萌、随机挑一句。
- 气泡约 3.6 秒后淡出；桌宠会轻微弹一下。
- 无悬浮窗权限时仍回退到原系统通知。

不做什么：不改 FGS 常驻通知；不删 Reef 通知通道（作回退）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 文案与派发 | `PetBlockBubble` |
| 气泡 overlay | `PetSpeechBubbleOverlay`、`overlay_pet_speech_bubble.xml` |
| 桌宠入口 | `PetService.ACTION_SPEECH_BUBBLE` |
| 钩子 | `HabitHook.blockFeedback` / `notifyBlock`；`GuardInitProvider` 注册 |
| 调用点 | `BlockerService` 习惯拦截与 focus_mode 拦截 |

## 3. 权限

需已开悬浮窗（与桌宠相同）。无权限 → 系统通知回退。

## 4. 实现要点

- kind：`habit` / `focus`；按 reason 关键词选 `string-array`（娱乐/视频/面/夜间/通用）。
- 占位：`%app%`、`%surface%`。
- 短时防抖约 1.8s，避免连拦刷屏。

## 5. 验证

工作时段打开被禁 App：应出现气泡、无「习惯守护」通知；番茄钟拦截同理。关悬浮窗时仍应有通知。

## 6. 搜索关键词

`PetBlockBubble`、`PetSpeechBubbleOverlay`、`ACTION_SPEECH_BUBBLE`、`HabitHook.notifyBlock`、`pet_bubble_generic`
