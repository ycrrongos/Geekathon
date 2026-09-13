# MikuUI 现代主页 chrome

| 项 | 内容 |
|----|------|
| 状态 | 已接入 |
| 日期 | 2026-09-12 |
| 模块 | `:app` |

## 1. 用户能看到什么

- 功能一句话：主页与控制小窗换成 sage 色板的现代卡片式 UI（品牌「守伴」），底部固定开启/暂停陪伴 CTA。
- 入口：`MainActivity` 主页；待办入口 `todoButton` → `PetPanelActivity` / 桌宠控制小窗 `PetPanelOverlay`。
- 不做什么（边界）：**不改**闪记 overlay/列表布局与行为；**不改**大爆炸透明 Activity 与词块布局；Reef 专注配置与权限流保持原入口。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 主类 | `GuardPet/app/src/main/java/com/geekathon/guardpet/MainActivity.kt` |
| 控制窗 | `PetPanelOverlay.kt`、`PetPanelActivity.kt` |
| 预览画布 | `PetCanvas.kt`（`fitPreviewToCanvas()`） |
| 布局 / 资源 | `activity_main.xml`、`activity_pet_panel.xml`、`item_todo.xml`；`values/colors.xml`、`themes.xml`、`strings.xml`、`styles.xml`（`Widget.GuardPet.Button.*`） |

其他 agent 会碰到的路径：

| 路径 | 改动类型 | 说明 |
|------|----------|------|
| `res/drawable/`（hero_/card_/primary_button 等） | 已复制 | 来自 MikuUI modern 分支 |
| `res/color/control_text.xml`、`switch_track.xml` | 已复制 | 按钮/开关着色 |
| `overlay_flash_notes.xml` 等闪记布局 | **禁止改** | 闪记 UI 独立 |
| `activity_big_bang.xml` 等 | **禁止改** | 大爆炸 UI 独立 |

不要改、以及为什么：闪记与大爆炸是产品主线交互，本次只换主页/控制窗 chrome。

## 3. 权限

- 无新权限。缺权仍走 Reef `PermissionsCheckActivity`；主页 `permissionStatus` 展示悬浮窗/用量/无障碍/麦克风状态。

## 4. 实现要点

- 源分支：https://github.com/zhangan526/AI-/tree/codex/ui-miku-modern（对照树 `/tmp/ui-miku-modern/MikuUI/`）
- 主页：`FrameLayout` + `NestedScrollView` + 底部 sticky CTA；`DecorFitsSystemWindows(false)` + insets padding；`contentColumn` 最大宽 600dp
- 品牌字符串全部「守伴」，不出现 Miku
- 样式名 `Widget.GuardPet.Button.*`（非 Widget.Miku）
- `PetPanelOverlay` 用 `ContextThemeWrapper(service, Theme_DesktopPet)` inflate，避免 Service 无主题导致 `?attr/` 崩溃；面板按钮背景已用 `@android:color/transparent`
- 保留 MainActivity 既有 ID：手势 Spinner、focus/reef/flash、`flashNoteContainer`、`focusAttribution` 等；主页另有 `focusStatsCard` 嵌入 Reef 专注统计（见 `13-home-focus-stats.md`）

## 5. 不要做的事

- 不要把闪记 HUD / 大爆炸迁到主页样式体系里
- 不要新增第二条 specialUse FGS 或第二个无障碍服务
- 不要把可见品牌改回 Reef / Miku

## 6. 验证

- 编译：`./gradlew :app:assembleDebug`（在 `GuardPet/`）
- 真机：主页 sage 背景与 sticky 开启按钮；展开「陪伴偏好」；闪记列表与按钮仍可用；控制小窗竖向待办 + 番茄钟按钮；桌宠 overlay 仍可开

## 7. 搜索关键词

`pageRoot`、`statusBadge`、`companionMessage`、`settingsDetails`、`Widget.GuardPet.Button`、`fitPreviewToCanvas`、`todoEmpty`、`ContextThemeWrapper`、`Theme_DesktopPet`

## 8. 相关文档

- `docs/TROUBLESHOOTING.md`：若 overlay inflate 再踩 `?attr/`，追加「PetPanelOverlay 无主题 inflate」
- `AGENTS.md`：可见品牌是「守伴」；闪记/大爆炸硬性规则
