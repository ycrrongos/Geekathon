# 守伴 · ADB 界面检查（电脑端）

纯本机网页工具，通过 **adb** 抓取手机当前前台与 `uiautomator` 界面树。不往手机装服务、不开手机 HTTP。

## 依赖

- Python 3.10+（仅标准库）
- `adb` 在 PATH 中，手机已 USB 调试授权

## 启动

```bash
cd tools/a11y-inspect
python3 server.py
```

浏览器打开：http://127.0.0.1:8764

端口可用环境变量：`A11Y_INSPECT_PORT=9000 python3 server.py`

## 功能

1. **抓 ACTIVE**：当前焦点包名 / Activity
2. **抓界面树**：`uiautomator dump`，列表展示全部 node；点击查看 text、content-desc、class、resource-id、bounds 等
3. **记录**：把选中元素写入同目录 `records.json`（可删单条 / 清空）

## 和作息守护的关系

用来校准「朋友圈 / 视频号」等真实节点特征，再填回 `HabitPolicyStore` 面规则或手动标记，避免误拦微信聊天页。

## 注意

- dump 时手机不要熄屏；部分 OEM 上 `uiautomator dump` 较慢
- 记录文件在本地，默认不提交（见仓库 `.gitignore`）
