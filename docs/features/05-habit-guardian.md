# 作息与习惯守护（Habit Agent）

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` + `:reef`（仅 HabitHook / Blocker 再评估） |

## 1. 用户能看到什么

- 工作时段按**四类应用**筛选：
  1. **工作应用**：不限制
  2. **明确娱乐应用**：整包禁用
  3. **通讯应用**（微信/QQ）：按 **Active 名**（启发式 / DeepSeek）标娱乐面并禁用（返回键）；主壳（如 QQ `SplashActivity`）不拦
  4. **视频应用**：工作时段**仅允许搜索**；首页遮挡；播放页展开简介后判学习/娱乐（`VideoGuard`）
- 「重新分析」：联网查 **Google Play / iTunes 公开分类** 映射四类；商店未覆盖的再用 AI；本地启发式兜底
- 应用规则可改模式 / 删除重分析
- 入口：主页「作息守护」
- 拦截反馈：桌宠头顶可爱气泡（见 `08-pet-block-bubble.md`），有悬浮窗时不发系统通知

不做什么：不新开无障碍 / specialUse FGS；**不再**分析时批量打开全部 Active 探测；不依赖需鉴权的酷安私有 API。  
**硬依赖**：系统设置里必须启用无障碍「守伴守护」（`BlockerService`），否则策略再正确也不拦截。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 商店分类 | `AppStoreMetaFetcher`、`StoreCategoryMapper` |
| 策略清洗 | `HabitPolicyStore.sanitizePolicy` / `coerceKnownPackageRule`（防桌面/微信误标） |
| AI 补全 / Active 名 | `AppActiveCatalog.classifyPackageKindsWithAi`、`classifyCommunicationActives` / `classifyVideoActives` |
| 本地兜底 | `AppTierClassifier`；通讯种子 `seedCommActivities` |
| 主壳白名单 | `CommActiveLists` |
| 壳层防误拦 | `PageEntertainmentJudge`（SHELL_MIXED）、`SurfaceMatcher` |
| 视频 | `HabitGuardian.evaluateVideo`、`VideoGuard`、`HabitPolicyStore.defaultVideoSurfaces` |
| 判定 | `HabitGuardian`（`isAlwaysAllowed` / `isHomeLauncher`） |
| 归档对照 | `GuardPet/archived/video-content-judge/`（曾一刀切整包禁，已恢复） |

## 3. 不要做的事

- 不要用裸 `"social"` 映射娱乐（会伤 `Social Networking`→微信）
- 不要把 launcher / `com.android.*` 送进商店按名字匹配
- 不要对通讯/视频把空 `[]` Active 当成已分析
- 不要在商店/映射修好前随意「重新分析」污染策略

## 4. 搜索关键词

`VideoGuard`、`SEARCH_ONLY`、`evaluateVideo`、`matchBlockingActive`、`AppStoreMetaFetcher`、`sanitizePolicy`、`seedCommActivities`、`isHomeLauncher`

相关排障：`Active 拦截无效 + 重新分析极慢`、`桌面被标娱乐 + 微信整包禁`、`还原到视频一刀切之前`
