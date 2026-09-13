# 守伴 Agent Guide

给后续 agent 的工作约定。改代码前先读本文件、对应功能文档、以及 `docs/TROUBLESHOOTING.md`。

本仓库是 Geekathon 项目 **守伴**：陪伴守护形 Android 桌宠。  
对外应用名 **守伴**，包名 `com.geekathon.guardpet`，工程目录 `GuardPet/`。

产品主线是「桌宠 overlay + 专注拦截 + 夜间作息 + 大爆炸抓字」。专注/拦截能力来自开源 **Reef**（MIT 副本在 `GuardPet/reef/`）。Reef 只是库，不是产品名。

---

## 硬性规则

1. **不要把 `MIKU-仅参考/` 当成要改的工程。** 那是桌宠骨架对照树，只读。产品代码只写 `GuardPet/`。
2. **可见品牌是「守伴」，不是 Reef、不是 MIKU。** 不得把 Reef 名称或官方图标当应用名/启动图标。设置或关于页必须保留 Reef MIT 署名与仓库链接：`https://github.com/aload0/Reef`。
3. **每做一个功能，必须写一篇功能开发文档**（`docs/features/_TEMPLATE.md`）。文档要让没读过本次对话的 agent 能独立改对模块。详情见「记笔记」。
4. **每次卡住、踩坑、误判，必须记入 `docs/TROUBLESHOOTING.md`。** 记症状、试过的方法、最终原因、解决办法。不要只记在聊天里。
5. **不要新开第二条 `specialUse` 前台服务。** `PetService` 已经占用该类型。番茄钟倒计时在 overlay 里跑，拦截只写 `prefs["focus_mode"]`。不要从桌宠再 `startForegroundService(FocusModeService)`。闪记录音时可以给**同一条** `PetService` 临时加上 `microphone` 类型，播放录音时临时加上 `mediaPlayback`，用完改回只有 `specialUse`。
6. **全应用只有一个无障碍服务：`BlockerService`。** 抓字、拦截、夜间守护共用它。不要再注册第二个 AccessibilityService。
7. **大爆炸不是悬浮窗。** 用独立 `taskAffinity` 的透明 Activity（NovaText 做法），让下层应用画面仍可见。禁止用 `TYPE_APPLICATION_OVERLAY` 做整页选词。
8. **不要提交 git commit，除非用户明确要求。**
9. **不要改** `~/.cursor/plans/` 里的计划文件。功能范围以本文件、思维导图和 `docs/features/` 为准。
10. **遇到不知道的东西，先查本仓库上下文，再上网搜。** 顺序：本文件 → `docs/features/` → `docs/TROUBLESHOOTING.md` → 代码与最近对话。查不到再 WebSearch / 对照开源仓库。不要凭记忆把行为归到某个 OEM（验证真机是后刷的原生 Android 16，不是 ColorOS）。
11. **记笔记不得只留在聊天里。** 约定见下方「记笔记」。

---

## 目录与真相源

| 路径 | 角色 |
|------|------|
| `GuardPet/` | **产品工程**（Gradle 工程名 GuardPet） |
| `GuardPet/app/` | 守伴 UI、桌宠、大爆炸、闪记、夜间规则、番茄钟 overlay |
| `GuardPet/sensevoice-pack/` | 离线 SenseVoice 模型独立 APK（`com.geekathon.guardpet.sensevoice`），不含 ASR 逻辑 |
| `GuardPet/reef/` | Reef MIT 副本：拦截、用量、白名单、配置页、权限页 |
| `GuardPet/appintro/` | Reef 引导库，随 `:reef` 编译 |
| `GuardPet/third_party/reef/` | 上游说明与许可证原文，只读 |
| `MIKU-仅参考/` | 桌宠对照工程，**只读** |
| `守伴桌宠-功能思维导图.drawio` | 产品功能图（飞书可导入） |
| `docs/features/` | **每个功能一篇开发文档** |
| `docs/TROUBLESHOOTING.md` | **固定排障日志** |

`GuardPet/app` 的 Application 是 `dev.pranav.reef.App`（manifest `tools:replace`）。守伴自己的初始化走 `GuardInitProvider`（闪记库、`HabitHook`、jieba 目录），不要再强行换 Application 子类，除非同时改 Reef `App` 与清单。

---

## 模块边界（必须）

### `:app`（`com.geekathon.guardpet`）

桌宠、手势、闪记、大爆炸、夜间 `HabitGuardian`、番茄钟 **外观 overlay**。  
入口：`MainActivity`。桌宠：`PetService`。

当前手势（主页「快捷手势」可改绑定；括号内为默认）：

- 拖拽：移动桌宠并记位置（固定，不占用快捷项）
- 单击：换样式
- 双击：功能菜单（提取 / 开始闪记 / 闪记列表 / 番茄钟 / 控制小窗）；菜单右上角 X 关闭
- 摇晃桌宠：摸摸
- 双击后长按：控制小窗
- 拖拽时摇手机：提取文字（框选）
- 自由行走：`PetSettings.edgeWalkEnabled`，默认开

可绑功能：`PetAction`（换样式、功能菜单、控制小窗、提取文字、开始闪记、闪记列表、番茄钟、摸摸）。手势检测在 `PetService.PetTouchListener`；手机摇晃在拖拽时经加速度计。

闪记是右侧胶囊悬浮窗，不是全屏 Activity。一个手势打开列表，另一个打开「在悬浮窗写作」（录音或手动）。卡片可换色，主页日记列表同步色点；有录音的卡片可重放 / 暂停 / 继续。overlay 在其他 App 上层播放时必须经 1px `FlashNotePlayActivity`（独立 taskAffinity），不要在纯 Service/overlay 里出声，也不要把闪记 HUD 迁到第二条无障碍服务。IME 需要暂时去掉 overlay 的 `FLAG_NOT_FOCUSABLE`。不要把闪记做成 MATCH_PARENT 全屏 overlay。同时按音量加减也可打开闪记（短按写作 / 长按录音），经 `BlockerService.onKeyEvent` + `VolumeChordFlashNote`，见 `docs/features/10-volume-chord-flash.md`。

离线语音转写：SenseVoice 模型在独立 APK `:sensevoice-pack`（`com.geekathon.guardpet.sensevoice`），**不要**打进 `:app`。运行时用 `SenseVoiceModelStore` + `SenseVoiceAsr`（sherpa-onnx AAR）。见 `docs/features/09-sensevoice-asr.md`。

### `:reef`（`dev.pranav.reef`）

拦截、用量、白名单、网站、Reef 配置页、`PermissionsCheckActivity`。  
对外入口保留在守伴主页「专注配置」：`FocusLauncher.openSettings()` → `navigate_to_settings`。

改拦截逻辑时走 `HabitHook`，不要在 `BlockerService` 里写死守伴规则。`GuardInitProvider` 已注册：

```kotlin
HabitHook.evaluator = { host, pkg -> HabitGuardian.evaluate(host, pkg) }
```

无障碍说明文案用守伴口吻（「守伴守护」），不要显示成 Reef 应用。

---

## 关键交互约定（必须）

### 大爆炸（提取文字）

1. `PetService.extractText()` 打开桌宠旁 `TextCropOverlay`（初始 16:9，长边=屏幕短边，可自由改框）。
2. 确定后藏桌宠，延迟后 `BlockerService.captureVisibleTextInRect(rect)`（中心点在框内）。
3. `TextTokenizer` 写入 `TextCaptureHolder`，启动 `BigBangActivity`（透明、独立 `taskAffinity`）。
4. 词块点选/拖选/反选；MD3 底栏；可 AI 整理后再选；复制 / 搜索 / 闪记。
5. 结束后 `ACTION_SHOW_PET` 再显示桌宠。

拖拽桌宠时摇手机：`PetGesture.DRAG_PHONE_SHAKE`（默认绑提取文字）。

不要改回全屏 overlay 选词页。透明 Activity 必须自己的 task。

### 番茄钟 overlay

桌宠打开后启动 **透明独立 task** `FocusTimerActivity`（暗幕 + 圆角窗，外观对齐提取文字/大爆炸）；窗内嵌 Reef `TimerContent`（`OverlayFocusTimerView`）。

倒计时在 `OverlayFocusSession` 跑。开始时 `focus_mode=true`，结束/关闭时清掉。  
**不要** `startForegroundService(FocusModeService)`（与 `PetService` 抢第二条 specialUse FGS）。  
**不要**再把 Compose 专注 UI 挂到 `PetService` 的 `TYPE_APPLICATION_OVERLAY`（易因 SavedState/Lifecycle 崩溃）。

### 权限

缺权时弹出 Reef 的 `PermissionsCheckActivity`（已含悬浮窗项）。守伴 `MainActivity.onResume` 会调 `checkAndRequestMissingPermissions()`。新增权限要同时改 `PermissionType`、`checkAllPermissions()`、授权页 `when`。

---

## 记笔记（必须）

文档要让**没读过本次对话**的 agent 能独立改对模块。对照工程 `/mnt/data/ArtistAOSP` 的同一套规矩：一篇功能一篇文档、排障只追加到固定文件。

### 功能开发文档

- **每做一个功能，必须写一篇** `docs/features/<id>-<slug>.md`。
- 新功能：复制 [`docs/features/_TEMPLATE.md`](docs/features/_TEMPLATE.md) → 填完 → 在 [`docs/features/README.md`](docs/features/README.md) **加一行索引**。尚未动手的能力不要空造一篇。
- 改已有功能：更新对应文档（入口、关键类、不要做的事、验证步骤、搜索关键词）。只改代码不改文档 = 没做完。
- 文档必须写清：用户可见行为、入口、模块与关键类、权限、不要做的事、实现要点、验证、给后续 agent 用的搜索关键词、相关排障条目标题。

### 排障日志

- **所有 agent 只往 [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) 追加。** 不要按功能再开新的排障文件。
- **每次卡住、踩坑、误判都必须记。** 记症状、试过的方法、最终原因、解决办法。不要只记在聊天里。
- 新条目放在「条目」区**最上方**（时间倒序）。同一问题再次出现时，在原条目下加「复现 / 修订」，不要删旧结论。
- 复制该文件顶部的条目模板，不要改模板本身。

### 查资料顺序

不知道就先查，再搜网，再改代码：

1. 本文件、`docs/features/`、`docs/TROUBLESHOOTING.md`
2. 代码与最近对话
3. 上网搜 / 对照开源实现（例如声物记）

真机是后刷原生 Android 16。日志里出现 `AudioHardening` 等字样，按 AOSP 行为记，不要写成 ColorOS。

---

## 新功能标准流程

1. 查重：`docs/features/README.md`、思维导图、现有 `:app` / `:reef` 类
2. 复制 `_TEMPLATE.md` 写 `docs/features/<id>-<slug>.md` 草稿，并在索引占一行
3. 实现到对应模块（桌宠/闪记/大爆炸 → `:app`；拦截/用量/配置 → `:reef` + hook）
4. 补全文档与索引（含搜索关键词、相关排障标题）
5. 验证：`./gradlew :app:assembleDebug`（在 `GuardPet/`）；UI 改动要在真机把相关页面走一遍
6. 踩坑写入 `docs/TROUBLESHOOTING.md`（最新条目置顶）

---

## 日常命令

在 `GuardPet/` 下：

```bash
./gradlew :app:assembleDebug
./gradlew :app:installDebug
```

JDK 17、compileSdk 37、minSdk 26。Gradle 代理写在 `GuardPet/gradle.properties`（`127.0.0.1:7890`）。

真机验证优先：桌宠 overlay、透明大爆炸、番茄钟下层可点，模拟器经常看不到完整悬浮窗行为。

---

## 完成前自检

- [ ] 改的是 `GuardPet/`，没有动 `MIKU-仅参考/`
- [ ] 用户可见名仍是 **守伴**；Reef 署名仍在
- [ ] 没有新增第二条 specialUse FGS，也没有第二个无障碍服务
- [ ] 大爆炸仍是透明独立 task Activity；番茄钟为 `FocusTimerActivity`（暗幕圆角窗 + Reef 专注 UI，不启 FocusModeService）
- [ ] `docs/features/` 已更新（新功能有索引行；文档含搜索关键词）
- [ ] 坑已写入 `docs/TROUBLESHOOTING.md`（最新置顶；同一问题用「复现 / 修订」）
- [ ] 不知道的事先查了文档/代码，再上网搜，没有凭记忆写 OEM
- [ ] `./gradlew :app:assembleDebug` 通过
- [ ] 未在未要求时 commit
