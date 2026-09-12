# 大爆炸提取文字

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:reef`（`BlockerService.captureVisibleTextInRect`） |

## 1. 用户能看到什么

1. 触发提取 → 桌宠旁出现 **16:9 初始框选窗**（长边=屏幕短边）；可拖角/边自由改尺寸（不锁比例）。
2. 确定后只抓 **框内** 无障碍文字 → 按屏幕 Y **聚类换行**（去父子重复）→ MD3 词块页（NovaText 式点选/拖选/反选）；**标点**灰底弱字色，正文白底。
3. 词块可 **复制 / 搜索 / 闪记**；可 AI：整理成笔记、去重去符号、翻译润色、自定义指令；整理后仍可继续选词或再 AI；可「恢复原文词块」。
4. 下层应用透过透明页可见；独立 task，不把守伴主页抬到前面。

入口：功能菜单「提取文字」；快捷手势可绑；**拖拽桌宠时摇手机**默认绑提取（`DRAG_PHONE_SHAKE`）。

不做什么：不用整页 `TYPE_APPLICATION_OVERLAY` 做选词；不做 OCR（仍是无障碍树）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 框选 | `TextCropOverlay` |
| 抓字 | `PetService.extractText` / `onTextCropConfirmed`；`BlockerService.captureVisibleTextInRect`（Y 聚类行） |
| 分词 | `TextTokenizer`（`LINE_BREAK`、标点拆分）、`TextCaptureHolder` |
| 结果页 | `BigBangActivity`、`TokenFlowView`（强制换行 + `token_bg_punct`）、`activity_big_bang.xml` |
| AI | `BigBangAi`、`HabitLlmClient.chatText`（需作息页 API Key） |
| 手势 | `PetGesture.DRAG_PHONE_SHAKE` + 拖拽时加速度计 |

主题：`Theme.DesktopPet.BigBang`（`MaterialComponents`，勿裸用 Service 建 Material 控件）；动画：`anim/bigbang_enter|exit` + sheet Overshoot。

## 3. 权限

悬浮窗（框选）；无障碍「守伴守护」（抓字）；AI 需 API Key。

## 4. 不要做的事

- 框选按钮不要直接用 `PetService` 当 Context 建 `MaterialButton`（会闪退）；用 `ContextThemeWrapper(Theme.DesktopPet)` 或 AppCompat 控件。
- 框宽高不要超过屏尺寸后再 `coerceIn`（横屏短边>宽时会崩）。

## 5. 验证

1. `./gradlew :app:installDebug`
2. 启动桌宠 → 提取文字 → 应出现框选，不闪退；取消恢复桌宠；确定打开词块页。
3. 可选：`adb shell am start -n com.geekathon.guardpet/.MainActivity --ez auto_extract true`

## 6. 搜索关键词

`TextCropOverlay`、`captureVisibleTextInRect`、`clusterTextLines`、`LINE_BREAK`、`token_bg_punct`、`BigBangAi`、`DRAG_PHONE_SHAKE`、`TokenFlowView`

## 7. 相关排障

- 「大爆炸页状态栏地球划斜线 + AI 用不了」（Restricted networking mode）
- 「拖拽摇手机闪退（与框选抢 WM）」
- 「提取文字一点就闪退（框选 Overlay）」
