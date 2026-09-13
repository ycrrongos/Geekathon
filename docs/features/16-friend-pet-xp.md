# 好友同屏与习惯经验

| 项 | 内容 |
|----|------|
| 状态 | 已接入（局域网 MVP） |
| 日期 | 2026-09-13 |
| 模块 | `:app` + `tools/friend-server/` |

## 1. 用户能看到什么

- **好友房**：填写电脑上的服务器地址与房间码，连接后**最多 4 位**好友的桌宠并排出现在自己桌宠右侧；可点好友宠查看心情/饱食/等级。
- **自定义形象**：主体类型 / 画面风格 / 核心特征；**快速本地绘制**或**精细千问 AI 生图**；支持上传参考图「按图 AI 生成」或直接使用；强制透明背景。入口：好友页内嵌面板，或设置 →「定制形象」→ `PetAppearanceActivity`。
- **习惯等级**：今日同时段屏幕使用相对昨日减少时获得经验；升级曲线类似 Minecraft。
- 入口：首页「好友与等级」；桌宠需已开启悬浮窗。

不做什么：

- 不做公网账号体系、推送、加好友搜索；暂用**同房码**。
- 不新开 `specialUse` FGS；同步挂在现有 `PetService` / 前台 Activity。
- 不把好友宠做成第二条无障碍服务。
- 不把大图塞进每次 `state` 心跳；形象走独立 `avatar` / `avatar_data`。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| PC 服务端 | `tools/friend-server/server.py`（asyncio TCP JSONL + 形象缓存） |
| 协议 | `FriendProtocol.kt`（`state` / `avatar` / `avatar_need`） |
| 客户端 | `FriendClient.kt`、`FriendPrefs.kt`、`FriendAvatarCache.kt` |
| 经验 | `HabitXpStore.kt`、`HabitXpSettler.kt` |
| 自定义形象 | `AppearanceCustomizeCard` / `PetAppearanceActivity` + `PetAppearanceGenerator`（移植自 [1103-jun/AI-](https://github.com/1103-jun/AI-)） |
| 资源 | `PetAssetRepository.installGeneratedAppearance` → `custom_generated.png` |
| 多宠 | `PetService` 内 `friendPetViews`（userId → PetCanvas） |
| UI | `FriendActivity` |

## 3. 权限

- `INTERNET`（已有）
- 用量进步需「使用情况访问」（与统计页相同）；缺权时经验结算跳过并提示。

## 4. 实现要点

- 协议：一行一个 JSON。`hello` → 入房；`state` 上报本机宠状态（含 `avatarHash`）；`avatar` 推送 PNG base64；服务端 `room` / `avatar_data` 广播。
- 好友宠：`LinkedHashMap<userId, PetCanvas>`，最多 4 个，跟随本宠横向偏移；形象优先 `FriendAvatarCache`，避免每帧 `randomFileFor`。
- 自定义形象：源能力来自 [1103-jun/AI-](https://github.com/1103-jun/AI-)（参考图生成 + 强制透明背景）；Key 可写 `local.properties` 或好友页输入。
- XP：用 `ScreenUsageHelper` 算「昨日同时段」与「今日至今」总分钟差；正差转 XP；`xpToNextLevel` 对齐 MC 分段。

## 5. 不要做的事

- 不要第二条 specialUse FGS
- 不要在非关于页贴 MIT 鸣谢（服务端 README 可写依赖说明）

## 6. 验证

1. 电脑：`python3 tools/friend-server/server.py`（默认 `0.0.0.0:18765`）
2. 手机与电脑同一局域网；好友页填 `电脑IP:18765` + 房间码，两人进同房
3. 双方开桌宠，应看到对方宠站旁边（多人并排）；点对方可看状态
4. 好友页生成/上传形象后，对方 overlay 与成员横滑应显示该形象
5. 有用量权限时，好友页可「结算今日进步」涨经验

## 7. 搜索关键词

`FriendClient`、`FriendActivity`、`FriendAvatarCache`、`friendPetViews`、`PetAppearanceGenerator`、`installGeneratedAppearance`、`avatarHash`、`friend-server`、`18765`

## 8. 相关文档

- `docs/TROUBLESHOOTING.md`：好友连不上 / 双宠 / 形象不同步
- `AGENTS.md`：单一 specialUse FGS
- 源参考：[1103-jun/AI- MikuUI](https://github.com/1103-jun/AI-/tree/codex/mikuui-source-20260913/MikuUI)