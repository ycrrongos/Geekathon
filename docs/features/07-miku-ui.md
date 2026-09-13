# MikuUI 现代主页 chrome

| 项 | 内容 |
|----|------|
| 状态 | 启动壳已由 [14-md3-home-merge.md](14-md3-home-merge.md) 取代；控制小窗仍用本套 sage 资源 |
| 日期 | 2026-09-12（修订 2026-09-13） |
| 模块 | `:app` |

## 1. 用户能看到什么

- 功能一句话：控制小窗仍用 sage 色板卡片式 UI（品牌「守伴」）。**启动主页**已改为 Reef MD3 底栏壳，见文档 14。
- 入口：待办 / 控制小窗 `PetPanelActivity` / `PetPanelOverlay`。
- 不做什么（边界）：**不改**闪记 overlay/列表布局与行为；**不改**大爆炸透明 Activity 与词块布局。

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| ~~主类 MainActivity XML~~ | 已迁 Compose，见 `14-md3-home-merge.md` |
| 控制窗 | `PetPanelOverlay.kt`、`PetPanelActivity.kt` |
| 预览画布 | `PetCanvas.kt`（`fitPreviewToCanvas()`） |
| 布局 / 资源 | `activity_pet_panel.xml`、`item_todo.xml`；`values/colors.xml`、`themes.xml`、`strings.xml`、`styles.xml`（`Widget.GuardPet.Button.*`）；`activity_main.xml` 仅历史对照 |

其他 agent 会碰到的路径：

| 路径 | 改动类型 | 说明 |
|------|----------|------|
| `res/drawable/`（hero_/card_/primary_button 等） | 已复制 | 来自 MikuUI modern 分支；控制窗仍用 |
| `overlay_flash_notes.xml` 等闪记布局 | **禁止改** | 闪记 UI 独立 |
| `activity_big_bang.xml` 等 | **禁止改** | 大爆炸 UI 独立 |

## 3. 权限

- 无新权限。缺权仍走 Reef `PermissionsCheckActivity`。

## 4. 实现要点

- 源分支：https://github.com/zhangan526/AI-/tree/codex/ui-miku-modern（对照树 `/tmp/ui-miku-modern/MikuUI/`）
- `PetPanelOverlay` 用 `ContextThemeWrapper(service, Theme_DesktopPet)` inflate
- 品牌字符串全部「守伴」，不出现 Miku

## 5. 不要做的事

- 不要把闪记 HUD / 大爆炸迁到主页样式体系里
- 不要新增第二条 specialUse FGS 或第二个无障碍服务
- 不要把可见品牌改回 Reef / Miku
- 不要把 `activity_main.xml` 重新绑成启动页（除非明确回退 MD3 壳）

## 6. 验证

- 编译：`./gradlew :app:assembleDebug`（在 `GuardPet/`）
- 真机：控制小窗竖向待办 + 番茄钟按钮；桌宠 overlay 仍可开；启动页见文档 14

## 7. 搜索关键词

`PetPanelOverlay`、`Widget.GuardPet.Button`、`fitPreviewToCanvas`、`todoEmpty`、`ContextThemeWrapper`、`Theme_DesktopPet`

## 8. 相关文档

- `docs/features/14-md3-home-merge.md`
- `docs/TROUBLESHOOTING.md`：若 overlay inflate 再踩 `?attr/`，追加「PetPanelOverlay 无主题 inflate」
- `AGENTS.md`：可见品牌是「守伴」；闪记/大爆炸硬性规则
