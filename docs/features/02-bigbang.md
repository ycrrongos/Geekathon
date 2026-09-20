# 大爆炸提取文字

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:reef`（`BlockerService.captureVisibleTextInRect`） |

## 1. 用户能看到什么

1. 触发提取 → 桌宠旁出现 **16:9 初始框选窗**（长边=屏幕短边）；可拖角/边自由改尺寸（不锁比例）。
2. 确定后只抓 **框内** 无障碍文字 → 按屏幕 Y **聚类换行**（去父子重复）→ 词块页（NovaText 式点选/拖选/反选）；**标点**灰底弱字色，正文白底。外壳是 `ReefTheme` 的 Material3（顶栏、AssistChip、底栏按钮）。词块仍是 `TokenFlowView`，不要改成 `FlowRow`。框选窗仍是悬浮层，不要改成 Compose。
3. 词块可 **复制 / 搜索 / 闪记**。AI 快捷条默认是「整理成笔记」「去重去符号」「翻译润色」，后面固定跟「自定义整理」（每次弹窗输入）和齿轮。齿轮或设置 → AI →「快捷整理」可改每一条的名称和指令，也能增删、排序、恢复默认。整理后仍可继续选词或再 AI；可「恢复原文词块」。
4. 下层应用透过透明页可见；独立 task，不把守伴主页抬到前面。

入口：功能菜单「提取文字」；快捷手势可绑；**拖拽桌宠时摇手机**默认绑提取（`DRAG_PHONE_SHAKE`）。

不做什么：不用整页 `TYPE_APPLICATION_OVERLAY` 做选词；不做 OCR（仍是无障碍树）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 框选 | `TextCropOverlay` |
| 抓字 | `PetService.extractText` / `onTextCropConfirmed`；`BlockerService.captureVisibleTextInRect`（Y 聚类行） |
| 分词 | `TextTokenizer`（`LINE_BREAK`、标点拆分）、`TextCaptureHolder` |
| 结果页 | `BigBangActivity`（`ReefTheme` 外壳）+ `TokenFlowView`（`AndroidView`，强制换行 + `token_bg_punct`） |
| AI | `BigBangAi`、`HabitLlmClient.chatText`（需设置「AI 接口」的 API Key） |
| 快捷条 | `BigBangShortcutStore`（prefs `bigbang_shortcuts` / `items`，JSON 数组）。没存过用三条默认；存过空数组就只剩「自定义整理」。`BigBangShortcutsActivity` 编辑。词块页 `AssistChip` 读这份列表，不要改回写死三个芯片，也不要改成可勾选 `FilterChip`。 |
| 手势 | `PetGesture.DRAG_PHONE_SHAKE` + 拖拽时加速度计 |

主题：窗口仍是 `Theme.DesktopPet.BigBang`（透明、暗幕、独立 task）。内容用 `ReefTheme`。不要把窗口主题改成 `Theme.Material3`，番茄钟共用这个窗口主题。不要给根布局铺不透明 `Scaffold`。

## 3. 权限

悬浮窗（框选）；无障碍「守伴守护」（抓字）；AI 需 API Key。

## 4. 不要做的事

- 框选按钮不要直接用 `PetService` 当 Context 建 `MaterialButton`（会闪退）；用 `ContextThemeWrapper(Theme.DesktopPet.Overlay)` 或 AppCompat 控件。
- 框宽高不要超过屏尺寸后再 `coerceIn`（横屏短边>宽时会崩）。
- 不要把词块拖选改成 Compose `FlowRow` / 可勾选 `FilterChip`（换行符没有芯片，拖选会和滚动抢）。
- 不要把大爆炸放进主页 `NavHost`（下层应用会被盖住，并跳回守伴任务）。
- 快捷整理的指令存在 `BigBangShortcutStore`，不要只改 `BigBangAi` 常量就以为用户看到的按钮会变。用户改过之后以 prefs 为准。
- 「自定义整理」是每次输入的临时指令，不要把它做成快捷条里的一条普通选项。

## 5. 验证

1. `./gradlew :app:installDebug`
2. 启动桌宠 → 提取文字 → 应出现框选，不闪退；取消恢复桌宠；确定打开词块页。
3. 可选：`adb shell am start -n com.geekathon.guardpet/.MainActivity --ez auto_extract true`
4. 设置 → AI → 快捷整理：改一条名称和指令，回到词块页应看到新按钮；点它走这条指令。删光后只剩「自定义整理」；恢复默认回到三条。

## 6. 搜索关键词

`TextCropOverlay`、`captureVisibleTextInRect`、`clusterTextLines`、`LINE_BREAK`、`token_bg_punct`、`BigBangAi`、`BigBangShortcutStore`、`BigBangShortcutsActivity`、`DRAG_PHONE_SHAKE`、`TokenFlowView`

## 7. 相关排障

- 「大爆炸页状态栏地球划斜线 + AI 用不了」（Restricted networking mode）
- 「拖拽摇手机闪退（与框选抢 WM）」
- 「提取文字一点就闪退（框选 Overlay）」
