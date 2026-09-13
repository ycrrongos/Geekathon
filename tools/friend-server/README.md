# 守伴好友房服务端

局域网临时服务，供手机 App 连接。无数据库、无账号。

```bash
python3 server.py
# 默认监听 0.0.0.0:18765
```

手机「好友与等级」页填写：`你的电脑局域网IP:18765`，多人填同一房间码。

支持同步自定义桌宠形象（`avatar` / `avatar_data` JSONL）。防火墙需放行 TCP 18765。

API Key（精细生成，可选）写入 `GuardPet/local.properties`：

```
dashscope.api.key=
deepseek.api.key=
openai.api.key=
```
