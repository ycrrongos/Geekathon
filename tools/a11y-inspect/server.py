#!/usr/bin/env python3
"""本机网页工具：通过 adb 抓前台 ACTIVE + uiautomator 界面树，点选记录元素。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
RECORDS_PATH = ROOT / "records.json"
DEFAULT_PORT = 8764
BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")


def adb(*args: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["adb", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else ""
        err = e.stderr if isinstance(e.stderr, str) else f"timeout after {timeout}s"
        return subprocess.CompletedProcess(list(e.cmd), 124, out or "", err or "")


def adb_ok() -> tuple[bool, str]:
    r = adb("devices", timeout=5)
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    devices = [ln for ln in lines[1:] if "\tdevice" in ln]
    if not devices:
        return False, r.stderr.strip() or "没有已连接的 adb device（请 USB 调试并授权）"
    return True, devices[0].split("\t", 1)[0]


def parse_focus(blob: str) -> dict:
    pkg = activity = None
    # mCurrentFocus=Window{... com.pkg/com.pkg.Activity}
    m = re.search(
        r"mCurrentFocus=Window\{[^ ]+ [^ ]+ ([^\s}/]+)/([^\s}]+)",
        blob,
    )
    if m:
        pkg, activity = m.group(1), m.group(2)
    if not pkg:
        m = re.search(r"mFocusedApp=.*? ([^\s}/]+)/([^\s}\s]+)", blob)
        if m:
            pkg, activity = m.group(1), m.group(2)
    if not pkg:
        m = re.search(
            r"mResumedActivity:.*? ([^\s}/]+)/([^\s}\s]+)",
            blob,
        )
        if m:
            pkg, activity = m.group(1), m.group(2)
    return {"packageName": pkg, "activity": activity}


def get_active() -> dict:
    ok, device = adb_ok()
    if not ok:
        return {"ok": False, "error": device}
    focus = {"packageName": None, "activity": None}
    for cmd in (
        ["shell", "dumpsys", "activity", "activities"],
        ["shell", "dumpsys", "window", "displays"],
        ["shell", "dumpsys", "window", "windows"],
    ):
        r = adb(*cmd, timeout=12)
        parsed = parse_focus(r.stdout or "")
        if parsed.get("packageName"):
            focus = parsed
            break
    return {
        "ok": True,
        "device": device,
        "packageName": focus.get("packageName"),
        "activity": focus.get("activity"),
        "label": None,
        "ts": int(time.time() * 1000),
    }


def dump_ui_hierarchy() -> dict:
    ok, device = adb_ok()
    if not ok:
        return {"ok": False, "error": device}

    # Prefer dump to stdout when supported; fallback to file pull.
    r = adb("exec-out", "uiautomator", "dump", "/dev/tty", timeout=40)
    xml_text = r.stdout
    if not xml_text.strip().startswith("<?xml") and "<hierarchy" not in xml_text:
        remote = "/data/local/tmp/a11y_inspect_dump.xml"
        r2 = adb("shell", "uiautomator", "dump", remote, timeout=40)
        if r2.returncode != 0 and "UI hierchary dumped" not in (r2.stdout + r2.stderr):
            # typo in older uiautomator message: hierchary
            if "dumped to" not in (r2.stdout + r2.stderr).lower():
                return {
                    "ok": False,
                    "error": (r2.stderr or r2.stdout or "uiautomator dump 失败").strip(),
                    "device": device,
                }
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            local = tmp.name
        pull = adb("pull", remote, local, timeout=20)
        if pull.returncode != 0:
            return {
                "ok": False,
                "error": (pull.stderr or "adb pull 失败").strip(),
                "device": device,
            }
        xml_text = Path(local).read_text(encoding="utf-8", errors="replace")
        try:
            os.unlink(local)
        except OSError:
            pass

    # Strip non-xml prefix/suffix noise from exec-out
    start = xml_text.find("<?xml")
    if start < 0:
        start = xml_text.find("<hierarchy")
    if start >= 0:
        xml_text = xml_text[start:]
    end = xml_text.rfind("</hierarchy>")
    if end >= 0:
        xml_text = xml_text[: end + len("</hierarchy>")]

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        return {"ok": False, "error": f"XML 解析失败: {e}", "device": device}

    nodes: list[dict] = []
    counter = {"n": 0}

    def walk(el: ET.Element, depth: int) -> None:
        if el.tag != "node" and depth > 0 and el.tag != "hierarchy":
            pass
        if el.tag == "node":
            bounds_raw = el.attrib.get("bounds", "")
            left = top = right = bottom = 0
            bm = BOUNDS_RE.match(bounds_raw or "")
            if bm:
                left, top, right, bottom = map(int, bm.groups())
            nid = counter["n"]
            counter["n"] += 1
            nodes.append(
                {
                    "id": nid,
                    "depth": depth,
                    "index": el.attrib.get("index"),
                    "text": el.attrib.get("text") or None,
                    "contentDescription": el.attrib.get("content-desc") or None,
                    "className": el.attrib.get("class") or None,
                    "packageName": el.attrib.get("package") or None,
                    "viewId": el.attrib.get("resource-id") or None,
                    "clickable": el.attrib.get("clickable") == "true",
                    "longClickable": el.attrib.get("long-clickable") == "true",
                    "checkable": el.attrib.get("checkable") == "true",
                    "checked": el.attrib.get("checked") == "true",
                    "enabled": el.attrib.get("enabled") == "true",
                    "focusable": el.attrib.get("focusable") == "true",
                    "scrollable": el.attrib.get("scrollable") == "true",
                    "selected": el.attrib.get("selected") == "true",
                    "bounds": bounds_raw,
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "width": max(0, right - left),
                    "height": max(0, bottom - top),
                }
            )
            child_depth = depth + 1
        else:
            child_depth = depth
        for child in el:
            walk(child, child_depth)

    walk(root, 0)
    active = get_active()
    return {
        "ok": True,
        "device": device,
        "count": len(nodes),
        "nodes": nodes,
        "active": {
            "packageName": active.get("packageName"),
            "activity": active.get("activity"),
            "label": active.get("label"),
        },
        "ts": int(time.time() * 1000),
    }


def load_records() -> list[dict]:
    if not RECORDS_PATH.exists():
        return []
    try:
        data = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_records(records: list[dict]) -> None:
    RECORDS_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>守伴 ADB 界面检查</title>
<style>
  :root {
    --bg: #0f1419;
    --panel: #1a222c;
    --line: #2c3845;
    --text: #e7eef6;
    --muted: #8b9bb0;
    --accent: #3d9cf0;
    --ok: #3ecf8e;
    --warn: #f0b429;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: "IBM Plex Sans", "Noto Sans SC", system-ui, sans-serif;
    background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column;
  }
  header {
    padding: 14px 18px; border-bottom: 1px solid var(--line);
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
  }
  header h1 { font-size: 16px; margin: 0; font-weight: 600; letter-spacing: 0.02em; }
  .ops { display: flex; gap: 8px; flex-wrap: wrap; margin-left: auto; }
  button, .file-btn {
    background: var(--panel); color: var(--text); border: 1px solid var(--line);
    border-radius: 8px; padding: 8px 12px; cursor: pointer; font-size: 13px;
  }
  button.primary { background: var(--accent); border-color: var(--accent); color: #041018; font-weight: 600; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  main { flex: 1; display: grid; grid-template-columns: 1.2fr 0.9fr 0.8fr; min-height: 0; }
  @media (max-width: 1100px) { main { grid-template-columns: 1fr; } }
  section { border-right: 1px solid var(--line); min-height: 0; display: flex; flex-direction: column; }
  section:last-child { border-right: none; }
  .sec-h { padding: 10px 14px; border-bottom: 1px solid var(--line); color: var(--muted); font-size: 12px; }
  .scroll { overflow: auto; flex: 1; padding: 8px; }
  .active-box {
    margin: 10px 14px; padding: 12px; background: var(--panel); border-radius: 10px;
    border: 1px solid var(--line); font-size: 13px; line-height: 1.5;
  }
  .active-box code { color: var(--ok); }
  .node {
    display: block; width: 100%; text-align: left; margin: 0 0 4px;
    padding: 8px 10px; border-radius: 8px; border: 1px solid transparent;
    background: transparent; color: var(--text); font-size: 12px; font-family: ui-monospace, monospace;
  }
  .node:hover { background: #243040; }
  .node.selected { border-color: var(--accent); background: #1c3044; }
  .node .meta { color: var(--muted); }
  .detail, .records { padding: 12px 14px; font-size: 13px; }
  .detail pre {
    white-space: pre-wrap; word-break: break-word; background: var(--panel);
    border: 1px solid var(--line); border-radius: 10px; padding: 12px; font-size: 12px;
  }
  .status { color: var(--muted); font-size: 12px; }
  .status.err { color: #ff7b72; }
  .rec-item {
    border: 1px solid var(--line); border-radius: 10px; padding: 10px; margin-bottom: 8px;
    background: var(--panel); font-size: 12px;
  }
  .rec-item .row { display: flex; gap: 8px; justify-content: space-between; align-items: start; }
  input[type=text] {
    width: 100%; margin: 8px 0; padding: 8px; border-radius: 8px; border: 1px solid var(--line);
    background: #0c1117; color: var(--text);
  }
  .filter { padding: 8px 14px; border-bottom: 1px solid var(--line); }
</style>
</head>
<body>
<header>
  <h1>守伴 · ADB 界面检查</h1>
  <span id="status" class="status">未连接</span>
  <div class="ops">
    <button id="btnActive" class="primary">抓 ACTIVE</button>
    <button id="btnDump" class="primary">抓界面树</button>
    <button id="btnRefreshRec">刷新记录</button>
    <button id="btnClearRec">清空记录</button>
  </div>
</header>
<main>
  <section>
    <div class="sec-h">元素列表（点击查看详情）</div>
    <div class="filter">
      <input id="filter" type="text" placeholder="过滤 text / desc / class / viewId / package"/>
    </div>
    <div id="active" class="active-box">尚未抓取前台</div>
    <div id="list" class="scroll"></div>
  </section>
  <section>
    <div class="sec-h">元素详情</div>
    <div class="detail scroll">
      <div id="detailEmpty" class="status">点左侧元素</div>
      <div id="detailPane" hidden>
        <pre id="detailJson"></pre>
        <input id="note" type="text" placeholder="备注（可选），如：朋友圈入口"/>
        <button id="btnRecord" class="primary">记录此元素</button>
      </div>
    </div>
  </section>
  <section>
    <div class="sec-h">已记录</div>
    <div id="records" class="scroll records"></div>
  </section>
</main>
<script>
const $ = (id) => document.getElementById(id);
let nodes = [];
let selected = null;
let activeInfo = null;

function setStatus(msg, err=false) {
  const el = $('status');
  el.textContent = msg;
  el.className = 'status' + (err ? ' err' : '');
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok || data.ok === false) throw new Error(data.error || res.statusText);
  return data;
}

function labelOf(n) {
  const t = n.text || n.contentDescription || '(无文字)';
  const short = t.length > 48 ? t.slice(0, 48) + '…' : t;
  return short;
}

function renderList() {
  const q = ($('filter').value || '').trim().toLowerCase();
  const box = $('list');
  box.innerHTML = '';
  const filtered = nodes.filter(n => {
    if (!q) return true;
    const blob = [n.text, n.contentDescription, n.className, n.viewId, n.packageName]
      .map(x => (x || '').toLowerCase()).join(' ');
    return blob.includes(q);
  });
  for (const n of filtered) {
    const b = document.createElement('button');
    b.className = 'node' + (selected && selected.id === n.id ? ' selected' : '');
    b.type = 'button';
    const pad = '·'.repeat(Math.min(n.depth, 8));
    b.innerHTML = `<span class="meta">${pad} #${n.id}</span> ${escapeHtml(labelOf(n))}<br/>
      <span class="meta">${escapeHtml((n.className||'').split('.').pop())} ${escapeHtml(n.viewId||'')} [${n.width}×${n.height}]</span>`;
    b.onclick = () => selectNode(n);
    box.appendChild(b);
  }
  if (!filtered.length) {
    box.innerHTML = '<div class="status" style="padding:12px">无匹配节点</div>';
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function selectNode(n) {
  selected = n;
  $('detailEmpty').hidden = true;
  $('detailPane').hidden = false;
  $('detailJson').textContent = JSON.stringify(n, null, 2);
  renderList();
}

function renderActive(a) {
  activeInfo = a;
  if (!a || (!a.packageName && !a.activity)) {
    $('active').innerHTML = '尚未抓取前台';
    return;
  }
  $('active').innerHTML = `ACTIVE<br/><code>${escapeHtml(a.packageName||'?')}</code><br/>
    activity: <code>${escapeHtml(a.activity||'?')}</code><br/>
    label: ${escapeHtml(a.label||'—')}`;
}

async function grabActive() {
  setStatus('抓取 ACTIVE…');
  try {
    const data = await api('/api/active');
    renderActive(data);
    setStatus(`device ${data.device || ''} · ACTIVE 已更新`);
  } catch (e) {
    setStatus(String(e.message || e), true);
  }
}

async function grabDump() {
  setStatus('uiautomator dump 中…');
  $('btnDump').disabled = true;
  try {
    const data = await api('/api/dump');
    nodes = data.nodes || [];
    renderActive(data.active || null);
    selected = null;
    $('detailEmpty').hidden = false;
    $('detailPane').hidden = true;
    renderList();
    setStatus(`device ${data.device || ''} · ${data.count} 个节点`);
  } catch (e) {
    setStatus(String(e.message || e), true);
  } finally {
    $('btnDump').disabled = false;
  }
}

async function loadRecords() {
  try {
    const data = await api('/api/records');
    const box = $('records');
    box.innerHTML = '';
    const list = data.records || [];
    if (!list.length) {
      box.innerHTML = '<div class="status">暂无记录</div>';
      return;
    }
    for (const r of list) {
      const div = document.createElement('div');
      div.className = 'rec-item';
      div.innerHTML = `<div class="row"><strong>${escapeHtml(r.note || r.text || r.contentDescription || r.id)}</strong>
        <button data-id="${escapeHtml(r.id)}" class="del">删</button></div>
        <div class="meta">${escapeHtml(r.packageName||'')} · ${escapeHtml(r.className||'')}</div>
        <div>text: ${escapeHtml(r.text||'—')}</div>
        <div>desc: ${escapeHtml(r.contentDescription||'—')}</div>
        <div>viewId: ${escapeHtml(r.viewId||'—')}</div>
        <div>bounds: ${escapeHtml(r.bounds||'—')}</div>`;
      div.querySelector('.del').onclick = async () => {
        await api('/api/records/' + encodeURIComponent(r.id), { method: 'DELETE' });
        loadRecords();
      };
      box.appendChild(div);
    }
  } catch (e) {
    setStatus(String(e.message || e), true);
  }
}

async function recordSelected() {
  if (!selected) return;
  const note = $('note').value.trim();
  try {
    await api('/api/record', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        note,
        node: selected,
        active: activeInfo,
      }),
    });
    $('note').value = '';
    setStatus('已记录');
    loadRecords();
  } catch (e) {
    setStatus(String(e.message || e), true);
  }
}

$('btnActive').onclick = grabActive;
$('btnDump').onclick = grabDump;
$('btnRecord').onclick = recordSelected;
$('btnRefreshRec').onclick = loadRecords;
$('btnClearRec').onclick = async () => {
  if (!confirm('清空全部记录？')) return;
  await api('/api/records', { method: 'DELETE' });
  loadRecords();
};
$('filter').oninput = renderList;

api('/api/health').then(d => {
  setStatus(d.adbOk ? `adb ok · ${d.device}` : d.error, !d.adbOk);
}).catch(e => setStatus(String(e.message||e), true));
loadRecords();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[a11y-inspect] {self.address_string()} {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict | list) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, HTML_PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/health":
            ok, info = adb_ok()
            self._json(
                200,
                {"ok": True, "adbOk": ok, "device": info if ok else None, "error": None if ok else info},
            )
            return
        if path == "/api/active":
            self._json(200, get_active())
            return
        if path == "/api/dump":
            self._json(200, dump_ui_hierarchy())
            return
        if path == "/api/records":
            self._json(200, {"ok": True, "records": load_records()})
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/record":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._json(400, {"ok": False, "error": "invalid json"})
                return
            node = payload.get("node") or {}
            active = payload.get("active") or {}
            rec = {
                "id": uuid.uuid4().hex[:10],
                "note": (payload.get("note") or "").strip(),
                "packageName": node.get("packageName") or active.get("packageName"),
                "activity": active.get("activity"),
                "text": node.get("text"),
                "contentDescription": node.get("contentDescription"),
                "className": node.get("className"),
                "viewId": node.get("viewId"),
                "bounds": node.get("bounds"),
                "clickable": node.get("clickable"),
                "node": node,
                "createdAt": int(time.time() * 1000),
            }
            records = load_records()
            records.insert(0, rec)
            save_records(records[:500])
            self._json(200, {"ok": True, "record": rec})
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/records":
            save_records([])
            self._json(200, {"ok": True})
            return
        if path.startswith("/api/records/"):
            rid = path[len("/api/records/") :]
            save_records([r for r in load_records() if r.get("id") != rid])
            self._json(200, {"ok": True})
            return
        self._json(404, {"ok": False, "error": "not found"})


def main() -> None:
    port = int(os.environ.get("A11Y_INSPECT_PORT", DEFAULT_PORT))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"守伴 ADB 界面检查: http://127.0.0.1:{port}")
    print("需要本机 adb，手机已授权 USB 调试。Ctrl+C 退出。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
