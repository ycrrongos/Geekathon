# 离线 SenseVoice ASR（闪记）

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:sensevoice-pack`（独立 APK） |

## 1. 用户能看到什么

- 功能一句话：闪记录音后用离线 SenseVoice 转成文字，模型在单独的「守伴语音模型」APK 里，不进主包。
- 入口：闪记悬浮窗「录音」停止后自动转写；「语音输入」有模型时改为短录+转写，无模型时 Toast 提示安装并回退系统 SpeechRecognizer。主页权限状态多一行「离线语音模型」。
- 不做什么：不把 ~229MB onnx 打进 `:app`；不新开 FGS / 无障碍；不依赖联网 ASR（有模型时）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| ASR 单例 | `GuardPet/app/.../SenseVoiceAsr.kt` |
| 模型定位/拷贝 | `GuardPet/app/.../SenseVoiceModelStore.kt` |
| 模型包 APK | `GuardPet/sensevoice-pack/`（`com.geekathon.guardpet.sensevoice`） |
| 下载脚本 | `GuardPet/scripts/fetch-sensevoice-pack.sh` |
| 运行时库 | `GuardPet/libs/sherpa-onnx-1.13.8.aar`（gitignore） |

其他 agent 会碰到的路径：

| 路径 | 改动类型 | 说明 |
|------|----------|------|
| `FlashNoteOverlay.kt` | 接线 | 停录后 `transcribe`；听写优先离线 |
| `FlashNoteActivity.kt` | 接线 | 同上（回退页） |
| `app/build.gradle.kts` | 依赖 | `files(.../libs/sherpa-onnx-1.13.8.aar)` |
| `settings.gradle.kts` | 模块 | `include(":sensevoice-pack")` |

不要改、以及为什么：

- 不要把 `model.int8.onnx` 放进 `:app` assets。
- 不要再开第二条 AccessibilityService / specialUse FGS。

## 3. 权限

- 录音：已有麦克风；模型包通过 `createPackageContext` 读 assets，主 App Manifest 需 `<queries>` 声明 pack 包名。
- 缺模型：Toast + `getLaunchIntentForPackage` / 安装提示。

## 4. 实现要点

- 首次 `ensureLocalModel`：若 `filesDir/sensevoice/` 已有合格文件则直接用；否则从 pack 拷贝 `sensevoice/model.int8.onnx` + `tokens.txt`。
- `OfflineRecognizer(null, config)`：`AssetManager=null` 走文件路径；`provider=cpu`，`numThreads=2`，`language=auto`。
- 转写在单线程 Executor；结果回主线程 Handler。去掉 SenseVoice `<|...|>` 标签。
- AAR 已内嵌 `libonnxruntime.so`，无需再加 onnxruntime Maven 依赖。
- `:app` 使用 `ndk.abiFilters = arm64-v8a`，避免把 AAR 里四 ABI 全打进主包。

## 5. 不要做的事

- 不要在主线程 `decode`。
- 不要把模型提交进 git。
- 不要改闪记播放的 `FlashNotePlayActivity` 路径。

## 6. 验证

- 编译：`./scripts/fetch-sensevoice-pack.sh` 后 `./gradlew :app:assembleDebug :sensevoice-pack:assembleDebug`
- 真机：`adb install -r` 两个 APK → 闪记录音 → 停止应显示「转写中…」并填入文字；未装 pack 时 Toast「未安装离线语音模型」。

## 7. 搜索关键词

`SenseVoiceAsr`、`SenseVoiceModelStore`、`OfflineRecognizer`、`sherpa-onnx`、`sensevoice-pack`、`createPackageContext`、`voice_transcribing`

## 8. 相关文档

- `docs/TROUBLESHOOTING.md`：`2026-09-12 — SenseVoice 模型包 / AAR / createPackageContext`
- `docs/features/04-flash-note.md`（ASR 节）
- `AGENTS.md`：模型在 sensevoice-pack，不在 `:app`
