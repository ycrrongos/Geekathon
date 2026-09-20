# 桌宠 overlay 与手势

## 用户可见行为

守伴以 `TYPE_APPLICATION_OVERLAY` 显示在其他应用上层。可拖拽、自由行走、到点睡觉。手势在主页「快捷手势」里绑定功能。

默认：

- 单击 → 换样式
- 双击 → 功能列表（Material3 色调按钮；从桌宠一侧 Overshoot 展开，收回用 Accelerate 错开，时长与闪记入场/退场相同；右上角关闭）
- 摇晃 → 摸摸
- 双击后长按 → 控制小窗（`Theme.DesktopPet.Overlay` 的 Material3 卡片）

每个手势的下拉项包含上述原功能，以及提取文字、开始闪记、闪记列表、番茄钟。

## 入口

- 主页「开启桌宠」（需悬浮窗权限）
- 主页「快捷手势」四个 Spinner
- 待办：主页按钮、设置「桌宠」行，打开 `PetPanelActivity`（MD3 全页）。悬浮控制小窗 inflate `activity_pet_panel.xml`（`Theme.DesktopPet.Overlay`，Material3），不要删这份布局，也不要在 `PetService` 里挂 Compose。
- 定制形象：主页行、好友页卡片、设置「桌宠」行

## 模块与关键类

- `PetService`：FGS `specialUse`，唯一允许的该类型服务；`PetTouchListener` 识别手势
- `PetAction` / `PetGesture` / `PetSettings.actionFor`
- `PetCanvas` / `PetAssetRepository`
- `PetMenuOverlay`、`PetPanelOverlay`、`PetSpeechBubbleOverlay`（拦截说话气泡）

## 权限

`SYSTEM_ALERT_WINDOW`；Android 13+ 通知权限（FGS 通知）

## 不要做的事

不要再开一条 specialUse FGS。不要改 `MIKU-仅参考/`。不要把拖拽移动做成可替换快捷项（会没法挪位置）。不要在 `PetService` 的悬浮窗里挂 Compose（没有 Lifecycle，会崩）；功能列表和控制小窗用 `Theme.DesktopPet.Overlay`。

## 验证步骤

默认：单击换样式、双击菜单能按 X 关掉、摇晃摸摸、双击后长按出控制窗。改绑提取文字后，对应手势应打开大爆炸。
