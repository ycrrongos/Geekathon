# `<功能短名>`

> 复制本文件为 `docs/features/<id>-<slug>.md` 后填写。`<id>` 建议下一位数字（`07-...`）或 `YYYYMMDD-slug`。  
> 写完后把链接加到 `docs/features/README.md`。

| 项 | 内容 |
|----|------|
| 状态 | 草稿 / 开发中 / 已接入 / 暂停 |
| 日期 | YYYY-MM-DD |
| 模块 | `:app` / `:reef` / 两者 |

## 1. 用户能看到什么

- 功能一句话：
- 入口（手势 / 主页按钮 / 配置页 / 菜单）：
- 不做什么（边界）：

## 2. 模块与关键类

| 角色 | 路径 |
|------|------|
| 主类 | `GuardPet/app/src/main/java/com/geekathon/guardpet/...` |
| 布局 / 资源 | |
| 存储 | |

其他 agent 会碰到的路径：

| 路径 | 改动类型 | 说明 |
|------|----------|------|
| | | |

不要改、以及为什么：

## 3. 权限

- 需要哪些权限、缺权时走哪条 Activity / 设置页：

## 4. 实现要点

- 关键类 / 方法 / 资源名：
- overlay / FGS / 无障碍约束（如有）：
- 独立 `taskAffinity`（如有）：

## 5. 不要做的事

- 

## 6. 验证

- 编译：`./gradlew :app:assembleDebug`（在 `GuardPet/`）
- 真机检查步骤：

## 7. 搜索关键词

给其他 agent 在仓库里定位用，例如：`FlashNotePlayActivity`、`TYPE_APPLICATION_OVERLAY`。

## 8. 相关文档

- `docs/TROUBLESHOOTING.md` 条目标题：
- `AGENTS.md` 相关硬性规则：
