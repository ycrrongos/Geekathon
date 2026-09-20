# 闪记

## 用户可见行为

右侧胶囊悬浮窗，贴在屏幕右边，不挡住下层应用。打开时关闭钮、写作条/写作卡、笔记卡片从上到下依次从右往左非线性弹出；关闭时反向（自下而上滑出消失）。点开/收起单条速记、打开/关闭「开始闪记」写作卡也有展开与收回动画（列表刷新不重播整窗进场）。

- **闪记列表**：按分类固定配色的圆角卡片叠放。点卡片展开看全文和日期。打开列表/写作时**左侧同时出现今日日程**（见 `11-day-schedule.md`）。
- **按钮形状**：录音 / 语音输入 / 保存、卡片内「重放」「转为日程 / 待办」是胶囊（左右半圆、上下直线，`corners` 半径 1000dp），高度 40dp。不要用 `oval`（拉宽会变成尖椭圆），也不要只给很小的圆角。收起行上的 ▶ 仍是小圆标。
- **开始闪记 / 在悬浮窗写作**：悬浮窗里输入，右上角 × 关闭写作窗。可录音，可手动打字，也可「语音输入」。录音停止后若已安装「守伴语音模型」会离线 SenseVoice 转写并写入输入框（仍保留录音路径）；未安装则 Toast 提示，纯录音仍可保存为「语音速记」。有模型时「语音输入」= 短录+转写；无模型时回退系统 SpeechRecognizer。
- **分类固定配色**（用户不可自选整盘色板）：
  - **灵感**：黄→绿对角渐变（Telegram 聊天背景参考，`#E8EA8A` → `#82BC87`）
  - **日记**：太阳黄（`#FFC107`）
  - **待办**：黄→红 6 档紧急度（写作时可选色点；列表可点色点切换）
  - **其他**：银灰
  - **日程**：见下；不出现在闪记列表
- 分类选「日程」时按钮为 **「保存日程」**；其它分类为 **「AI 整理保存」**——按类型（灵感/日记/待办/其他）经 `FlashNoteLlmClient` 整理后再写入闪记（无 API Key 时本地启发式）。
- **展开卡片转换**：
  - **待办** →「转为日程」：走日程 AI 管线；成功入库后删除该待办
  - **灵感** →「转为日程」/「转为待办」：生成日程或新待办，**不删除**原灵感
- 带录音的卡片有播放按钮：重放 / 暂停 / 继续。展开后右上角 × 收起卡片。
- 主 App 日记列表每条左侧有同步色点（按分类固定色 / 待办紧急度）。
- 主页权限状态含「离线语音模型：已安装/未安装」。

分类（日程/灵感/日记/待办/其他）仍保留；日程默认今天。分类不再拦截保存：未改分类时记为「其他」。

## 入口（手势 / 主页按钮 / 配置页）

- 桌宠快捷手势：`FLASH_NOTE` 开始闪记，`FLASH_NOTE_LIST` 闪记列表（需在主页「快捷手势」里绑定）
- 功能菜单：开始闪记、闪记列表
- 主页「闪记」：有悬浮窗权限则打开写作 overlay，否则回退 `FlashNoteActivity`
- 大爆炸「闪记」：把选中文字送进写作 overlay
- **音量加减同时按**：短按打开写作窗；长按开始录音，松开结束（需无障碍；见 `10-volume-chord-flash.md`）

## 模块与关键类

- `FlashNoteHud` / `FlashNoteOverlay`：右侧 overlay（打开时联动 `ScheduleHud`）
- `FlashNoteLlmClient`：非日程分类 AI 整理
- `FlashNoteColors`：`FlashNoteCategory` / `FlashNoteColor` / `DayScheduleColor`
- `FlashNoteStore`（SQLite，含 `color`、`audio_path`）；`all()` 过滤掉 `SCHEDULE`
- 富日程：`DayScheduleStore` / `ScheduleOverlay`（见 `11-day-schedule.md`）；`ScheduleHud.showFillTimes(..., afterCommit)`
- `FlashNoteRecorder` / `FlashNotePlayer`：录音与回放
- `FlashNotePlayActivity`：1px 透明独立 task
- `MicPermissionActivity`：独立 task 申请麦克风
- `GuardInitProvider` 里 `FlashNoteStore.init`、`DayScheduleStore.init`
- 离线 ASR：见 `docs/features/09-sensevoice-asr.md`

## 权限

- 显示：`SYSTEM_ALERT_WINDOW`
- 录音 / 听写：麦克风。从 overlay 申请时走 `MicPermissionActivity`
- 日程日历导入：`READ_CALENDAR`
- AI 整理：设置「AI 接口」的 DeepSeek Key（`HabitPolicyStore.llmApiKey`，改完即保存）；缺 Key 本地规则。千问 Key 只给形象生成。

## 不要做的事

- 不要用 `MATCH_PARENT` 全屏 overlay 盖住下层触摸。
- 不要新增 `microphone` 类型的**第二条** FGS。
- 不要再注册第二个无障碍服务。
- **不要把「日程」分类再写入 `FlashNoteStore`**；只进 `DayScheduleStore`。
- **灵感转日程/待办后不要删原灵感**；待办转日程成功后可删待办。
- 左右叠层重叠区不要用几何中心抢命中（见 `PassthroughFrameLayout`：上层优先）。

## 验证步骤

1. 非日程分类写一段话 →「AI 整理保存」→ 列表为整理后文案。
2. 展开待办 →「转为日程」→ 左侧出现日程，待办消失（需补时间时确认后消失）。
3. 展开灵感 →「转为待办」→ 多一条待办，灵感仍在；「转为日程」同理保留灵感。
4. 左右叠层：点上层控件（即使压在下层位置上）不应先收下层再弹回；只有点下层露出区域才切层。

## 搜索关键词

`FlashNoteHud`、`FlashNoteOverlay`、`FlashNoteLlmClient`、`flash_convert_to_schedule`、`flash_note_organize_save`、`convertIdeaToTodo`、`PassthroughFrameLayout`、`save_schedule`、`ScheduleHud.showFillTimes`

## 相关文档

- `docs/features/11-day-schedule.md`
- `docs/TROUBLESHOOTING.md`：左右切层误抬下层
- `AGENTS.md`
