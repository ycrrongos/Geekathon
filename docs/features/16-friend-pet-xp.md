# 好友同屏与习惯经验

| 项 | 内容 |
|----|------|
| 状态 | 已接入（局域网 MVP） |
| 日期 | 2026-09-13 |
| 模块 | `:app` + `tools/friend-server/` |

## 1. 用户能看到什么

- **好友房**：填写电脑上的服务器地址与房间码，连接后**最多 4 位**好友的桌宠并排出现在自己桌宠右侧；可点好友宠查看心情/饱食/等级/当前动作。对方走动、睡觉、摸摸等会反映在旁宠动效（定制形象为单图时用位移/透明度近似；无定制则切对应状态素材）。好友页成员卡显示心情、饱食与 state。
- **自定义形象**：主体类型 / 画面风格 / 核心特征；**快速本地绘制**或**精细千问 AI 生图**；支持上传参考图「按图 AI 生成」或直接使用；强制透明背景。入口：好友页内嵌面板，或设置 →「定制形象」→ `PetAppearanceActivity`。
- **习惯等级**：今日同时段屏幕使用相对昨日减少时获得经验；升级曲线类似 Minecraft。
- 入口：首页「好友与等级」；桌宠需已开启悬浮窗。

不做什么：

- 不做公网账号体系、推送、加好友搜索；暂用**同房码**。
- 不新开 `specialUse` FGS；同步挂在现有 `PetService` / 前台 Activity。
- 不把好友宠做成第二条无障碍服务。
- 不把大图塞进每次 `state` 心跳；形象走独立 `avatar` / `avatar_data`。
- 不保证定制形象像素级同步对方 GIF（单张 PNG + 本地动效近似）。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| PC 服务端 | `tools/friend-server/server.py`（asyncio TCP JSONL + 形象缓存） |
| 协议 | `FriendProtocol.kt`（`state` / `avatar` / `avatar_need`） |
| 客户端 | `FriendClient.kt`、`FriendPrefs.kt`、`FriendAvatarCache.kt` |
| 经验 | `HabitXpStore.kt`、`HabitXpSettler.kt` |
| 自定义形象 | `AppearanceCustomizeCard` / `PetAppearanceActivity` + `PetAppearanceGenerator`（移植自 [1103-jun/AI-](https://github.com/1103-jun/AI-)） |
| 资源 | `PetAssetRepository.installGeneratedAppearance` → `custom_generated.png` |
| 多宠 | `PetService`：`friendPetViews`、`pushLocalFriendState`、`layoutFriendOverlays`、`applyFriendRemoteVisual` |
| UI | `FriendActivity` |

## 3. 权限

- `INTERNET`（已有）
- 用量进步需「使用情况访问」（与统计页相同）；缺权时经验结算跳过并提示。

## 4. 实现要点

- 协议：一行一个 JSON。`hello` → 入房；`state` 上报本机宠状态（含 mood/hunger/state/`avatarHash`）；`avatar` 推送 PNG base64；服务端 `room` / `avatar_data` 广播。
- **状态推送**：`FriendClient` **写与读分离**（禁止把 write 再丢回读线程的单线程队列，否则 state 永远发不出）。入房立刻推 mood/hunger/state；2s 心跳；本机动作变化 `reportAnimState` + `sendPetState`；收 `room` 只布局 overlay。
- 好友宠：最多 4 个，跟随本宠横向偏移；形象优先 `FriendAvatarCache`；**形象 key 与 motion key 分离**，有定制图仍按对方 state 做 bob/睡觉变暗等。
- 自定义形象：源能力来自 [1103-jun/AI-](https://github.com/1103-jun/AI-)（参考图生成 + 强制透明背景）；Key 可写 `local.properties` 或好友页输入。
- XP：用 `ScreenUsageHelper` 算「昨日同时段」与「今日至今」总分钟差；正差转 XP；`xpToNextLevel` 对齐 MC 分段。

## 5. 不要做的事

- 不要第二条 specialUse FGS
- 不要在非关于页贴 MIT 鸣谢（服务端 README 可写依赖说明）
- 不要在 `FriendClient.observe` 里再 `sendPetState`（会环）
- 不要把 `writeRaw(state)` 丢进与 `readLine` 同一个单线程队列

## 6. 验证

1. 电脑：`python3 tools/friend-server/server.py`（默认 `0.0.0.0:18765`）
2. 手机与电脑同一局域网；好友页填 `电脑IP:18765` + 房间码，两人进同房
3. 双方开桌宠，应看到对方宠站旁边；点对方可看心情/饱食/state
4. 一方摸摸/行走：另一方旁宠动效应变化；好友页成员卡心/饱数字随心跳更新
5. 好友页生成/上传形象后，对方 overlay 与成员横滑应显示该形象
6. 有用量权限时，好友页可「结算今日进步」涨经验

## 7. 搜索关键词

`FriendClient`、`FriendActivity`、`FriendAvatarCache`、`friendPetViews`、`pushLocalFriendState`、`layoutFriendOverlays`、`applyFriendRemoteVisual`、`PetAppearanceGenerator`、`installGeneratedAppearance`、`avatarHash`、`friend-server`、`18765`

## 8. 相关文档

- `docs/TROUBLESHOOTING.md`：好友连不上 / 双宠 / 形象不同步 / 心情动画不同步
- `AGENTS.md`：单一 specialUse FGS
- 源参考：[1103-jun/AI- MikuUI](https://github.com/1103-jun/AI-/tree/codex/mikuui-source-20260913/MikuUI)
