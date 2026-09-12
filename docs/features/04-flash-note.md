# 闪记

## 用户可见行为

右侧胶囊悬浮窗，贴在屏幕右边，不挡住下层应用。打开时关闭钮、写作条/写作卡、笔记卡片从上到下依次从右往左非线性弹出；关闭时反向（自下而上滑出消失）。点开/收起单条速记、打开/关闭「开始闪记」写作卡也有展开与收回动画（列表刷新不重播整窗进场）。

- **闪记列表**：彩色圆角卡片叠放。点卡片展开看全文和日期；点左侧空心圆或色点换色。
- **开始闪记 / 在悬浮窗写作**：悬浮窗里输入，右上角 × 关闭写作窗。可录音，可手动打字，也可「语音输入」。录音停止后若已安装「守伴语音模型」会离线 SenseVoice 转写并写入输入框（仍保留录音路径）；未安装则 Toast 提示，纯录音仍可保存为「语音速记」。有模型时「语音输入」= 短录+转写；无模型时回退系统 SpeechRecognizer。
- 带录音的卡片有播放按钮：重放 / 暂停 / 继续。展开后右上角 × 收起卡片。
- 主 App 日记列表每条左侧有同步色点。
- 主页权限状态含「离线语音模型：已安装/未安装」。

分类（日程/灵感/日记/待办/其他）仍保留；日程默认今天，供夜间守护读取。分类不再拦截保存：未改分类时记为「其他」。

## 入口（手势 / 主页按钮 / 配置页）

- 桌宠快捷手势：`FLASH_NOTE` 开始闪记，`FLASH_NOTE_LIST` 闪记列表（需在主页「快捷手势」里绑定）
- 功能菜单：开始闪记、闪记列表
- 主页「闪记」：有悬浮窗权限则打开写作 overlay，否则回退 `FlashNoteActivity`
- 大爆炸「闪记」：把选中文字送进写作 overlay
- **音量加减同时按**：短按打开写作窗；长按开始录音，松开结束（需无障碍；见 `10-volume-chord-flash.md`）

## 模块与关键类

- `FlashNoteHud` / `FlashNoteOverlay`：右侧 overlay
- `FlashNoteStore`（SQLite，含 `color`、`audio_path`）
- `FlashNoteRecorder` / `FlashNotePlayer`：录音与回放
- `FlashNotePlayActivity`：1px 透明独立 task。Android 16 AudioHardening 会静音没有前台 Activity 的后台播放（本机为后刷原生 AOSP，不是 ColorOS）；overlay 点播放时由无障碍服务（没有则桌宠服务）拉起这个 Activity，播完或停止后关掉。不要做成全屏窗盖住下层应用。
- `MicPermissionActivity`：独立 task 申请麦克风，避免把守伴主页抬到前台
- `GuardInitProvider` 里 `FlashNoteStore.init`
- 离线 ASR：`SenseVoiceAsr` + `SenseVoiceModelStore`；模型在独立 APK `:sensevoice-pack`（`com.geekathon.guardpet.sensevoice`），详见 `docs/features/09-sensevoice-asr.md`

音频文件在 `filesDir/flash_audio/`，WAV（AudioRecord）。播放走 AudioTrack，不经过 MediaPlayer。overlay 点播放不要直接在 Service 里出声，必须经 `FlashNotePlayActivity`。

## 权限

- 显示：`SYSTEM_ALERT_WINDOW`
- 录音 / 听写：麦克风。从 overlay 申请时走 `MicPermissionActivity`（独立 `taskAffinity`）

## 不要做的事

- 不要用 `MATCH_PARENT` 全屏 overlay 盖住下层触摸。
- 不要新增 `microphone` 类型的**第二条** FGS。录音时给已有 `PetService` 临时加上 `microphone` 类型即可。
- 不要再注册第二个无障碍服务。
- 列表浏览时 overlay 要带 `FLAG_NOT_FOCUSABLE`，避免抢走下层输入；写作时才去掉该 flag 以便 IME。
- overlay 点播放不要直接在 Service 里 `AudioTrack.play()`。必须经 `FlashNotePlayActivity`，否则 Android 16 会静音后台播放。
- overlay 布局不要用 `?attr/`（从 Service inflate 会崩）。

## 验证步骤

1. 把手势分别绑到「闪记列表」和「开始闪记」。
2. 开始闪记：打字保存一条；再录音保存一条。
3. 列表里展开卡片，点色点换色；回主页日记，左侧色点应一致。
4. 语音卡片点播放：可暂停、再点继续、播完可重放。在微信等其他 App 上层点播放也要有声音，且不要把守伴主页抬上来。
5. 写作时下层应用仍可点悬浮窗以外区域。

## 搜索关键词

`FlashNoteHud`、`FlashNoteOverlay`、`FlashNotePlayActivity`、`FlashNotePlayer`、`AudioHardening`、`FLAG_NOT_FOCUSABLE`、`audio_path`、`OvershootInterpolator`、`needsEntrance`、`playExitAnimation`、`animateCardExpand`、`SenseVoiceAsr`、`voice_transcribing`、`VolumeChordFlashNote`

## 相关文档

- `docs/TROUBLESHOOTING.md`：`2026-09-12 — 其他 App 上层点闪记播放仍无声`；`2026-09-12 — SenseVoice 模型包 / AAR / createPackageContext`
- `docs/features/09-sensevoice-asr.md`
- `AGENTS.md`：一条 FGS、一个无障碍服务、记笔记；离线模型在 sensevoice-pack
