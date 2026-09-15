#!/usr/bin/env python3
"""守伴好友房 — 局域网 TCP JSONL 服务（标准库，无第三方依赖）。

用法:
  python3 server.py                 # 0.0.0.0:18765
  python3 server.py --port 18765

协议（每行一个 JSON）:
  客户端 → {"type":"hello","userId":"...","name":"...","room":"ABCD"}
  客户端 → {"type":"state","pet":{...}}
  客户端 → {"type":"avatar","userId":"...","hash":"...","data":"<b64>"}
  客户端 → {"type":"avatar_need","userId":"...","hash":"..."}
  客户端 → {"type":"ping"}
  服务端 → {"type":"welcome","userId":"...","room":"..."}
  服务端 → {"type":"room","members":[{userId,name,pet}, ...]}
  服务端 → {"type":"avatar_data","userId":"...","hash":"...","data":"<b64>"}
  服务端 → {"type":"error","message":"..."}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

LOG = logging.getLogger("friend-server")
# asyncio StreamReader.readline 默认 limit=64KiB，形象 base64 远超会直接 ValueError 断线
MAX_AVATAR_B64 = 900_000
STREAM_LIMIT = MAX_AVATAR_B64 + 64_000


@dataclass
class Member:
    user_id: str
    name: str
    room: str
    writer: asyncio.StreamWriter
    pet: Dict[str, Any] = field(default_factory=dict)
    avatar_hash: str = ""
    avatar_b64: str = ""


class FriendServer:
    def __init__(self) -> None:
        self.members: Dict[str, Member] = {}  # user_id -> Member
        self.rooms: Dict[str, Set[str]] = {}  # room -> user_ids

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        LOG.info("connect %s", peer)
        user_id: Optional[str] = None
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                if len(line) > MAX_AVATAR_B64 + 8_000:
                    await self._send(writer, {"type": "error", "message": "line too large"})
                    continue
                try:
                    msg = json.loads(line.decode("utf-8").strip() or "{}")
                except json.JSONDecodeError:
                    await self._send(writer, {"type": "error", "message": "invalid json"})
                    continue
                mtype = msg.get("type")
                if mtype == "hello":
                    user_id = await self._on_hello(msg, writer, user_id)
                elif mtype == "state":
                    if not user_id or user_id not in self.members:
                        await self._send(writer, {"type": "error", "message": "say hello first"})
                        continue
                    pet = msg.get("pet") or {}
                    if isinstance(pet, dict):
                        member = self.members[user_id]
                        merged = dict(pet)
                        # 心跳若暂时没带 hash，保留服务端已知形象，避免改形后被空 hash 冲掉
                        if not str(merged.get("avatarHash") or "").strip() and member.avatar_hash:
                            merged["avatarHash"] = member.avatar_hash
                        member.pet = merged
                        ah = str(merged.get("avatarHash") or "").strip()
                        if ah:
                            member.avatar_hash = ah
                        LOG.info(
                            "state %s mood=%s hunger=%s anim=%s",
                            user_id,
                            merged.get("mood"),
                            merged.get("hunger"),
                            merged.get("state"),
                        )
                        await self._broadcast_room(member.room)
                elif mtype == "avatar":
                    if not user_id or user_id not in self.members:
                        await self._send(writer, {"type": "error", "message": "say hello first"})
                        continue
                    await self._on_avatar(user_id, msg)
                elif mtype == "avatar_need":
                    if not user_id or user_id not in self.members:
                        continue
                    await self._on_avatar_need(writer, msg)
                elif mtype == "ping":
                    await self._send(writer, {"type": "pong"})
                else:
                    await self._send(writer, {"type": "error", "message": f"unknown type {mtype}"})
        except (ConnectionResetError, asyncio.IncompleteReadError):
            pass
        except ValueError as e:
            # 常见：chunk exceed the limit（未抬高 STREAM_LIMIT 时）
            LOG.warning("protocol error from %s: %s", peer, e)
        finally:
            if user_id:
                await self._leave(user_id)
            writer.close()
            await writer.wait_closed()
            LOG.info("disconnect %s", peer)

    async def _on_hello(
        self, msg: dict, writer: asyncio.StreamWriter, old_id: Optional[str]
    ) -> Optional[str]:
        user_id = str(msg.get("userId") or "").strip()
        name = str(msg.get("name") or "访客").strip()[:24] or "访客"
        room = str(msg.get("room") or "").strip().upper()[:12]
        if not user_id or not room:
            await self._send(writer, {"type": "error", "message": "userId and room required"})
            return old_id
        if old_id and old_id != user_id:
            await self._leave(old_id)
        if user_id in self.members:
            await self._leave(user_id)
        member = Member(user_id=user_id, name=name, room=room, writer=writer)
        self.members[user_id] = member
        self.rooms.setdefault(room, set()).add(user_id)
        await self._send(writer, {"type": "welcome", "userId": user_id, "room": room, "name": name})
        await self._broadcast_room(room)
        # 把房内已有形象推给新人
        for uid in list(self.rooms.get(room, set())):
            if uid == user_id:
                continue
            other = self.members.get(uid)
            if other and other.avatar_hash and other.avatar_b64:
                await self._send(
                    writer,
                    {
                        "type": "avatar_data",
                        "userId": other.user_id,
                        "hash": other.avatar_hash,
                        "mime": "image/png",
                        "data": other.avatar_b64,
                    },
                )
        LOG.info("hello %s room=%s name=%s", user_id, room, name)
        return user_id

    async def _on_avatar(self, user_id: str, msg: dict) -> None:
        member = self.members.get(user_id)
        if not member:
            return
        hash_ = str(msg.get("hash") or "").strip()[:64]
        data = str(msg.get("data") or "")
        if not hash_ or not data or len(data) > MAX_AVATAR_B64:
            return
        member.avatar_hash = hash_
        member.avatar_b64 = data
        if isinstance(member.pet, dict):
            member.pet = {**member.pet, "avatarHash": hash_}
        payload = {
            "type": "avatar_data",
            "userId": user_id,
            "hash": hash_,
            "mime": "image/png",
            "data": data,
        }
        for uid in list(self.rooms.get(member.room, set())):
            if uid == user_id:
                continue
            other = self.members.get(uid)
            if not other:
                continue
            try:
                await self._send(other.writer, payload)
            except Exception:
                await self._leave(uid)
        await self._broadcast_room(member.room)
        LOG.info("avatar %s hash=%s bytes≈%d", user_id, hash_, len(data))

    async def _on_avatar_need(self, writer: asyncio.StreamWriter, msg: dict) -> None:
        target_id = str(msg.get("userId") or "").strip()
        hash_ = str(msg.get("hash") or "").strip()
        target = self.members.get(target_id)
        if not target or not target.avatar_b64:
            return
        if hash_ and target.avatar_hash and target.avatar_hash != hash_:
            return
        await self._send(
            writer,
            {
                "type": "avatar_data",
                "userId": target.user_id,
                "hash": target.avatar_hash,
                "mime": "image/png",
                "data": target.avatar_b64,
            },
        )

    async def _leave(self, user_id: str) -> None:
        member = self.members.pop(user_id, None)
        if not member:
            return
        room_set = self.rooms.get(member.room)
        if room_set:
            room_set.discard(user_id)
            if not room_set:
                self.rooms.pop(member.room, None)
            else:
                await self._broadcast_room(member.room)
        LOG.info("leave %s room=%s", user_id, member.room)

    async def _broadcast_room(self, room: str) -> None:
        ids = list(self.rooms.get(room, set()))
        members = []
        for uid in ids:
            m = self.members.get(uid)
            if m:
                pet = dict(m.pet) if isinstance(m.pet, dict) else {}
                if m.avatar_hash:
                    pet["avatarHash"] = m.avatar_hash
                members.append({"userId": m.user_id, "name": m.name, "pet": pet})
        payload = {"type": "room", "room": room, "members": members}
        dead: list[str] = []
        for uid in ids:
            m = self.members.get(uid)
            if not m:
                continue
            try:
                await self._send(m.writer, payload)
            except Exception:
                dead.append(uid)
        for uid in dead:
            await self._leave(uid)

    @staticmethod
    async def _send(writer: asyncio.StreamWriter, obj: dict) -> None:
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        writer.write(data)
        await writer.drain()


async def main(host: str, port: int) -> None:
    server = FriendServer()
    srv = await asyncio.start_server(server.handle, host, port, limit=STREAM_LIMIT)
    addrs = ", ".join(str(s.getsockname()) for s in srv.sockets or [])
    LOG.info("listening on %s (stream limit=%d)", addrs, STREAM_LIMIT)
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="守伴好友房服务")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        pass
