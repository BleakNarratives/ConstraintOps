"""Adapters for Claude Code, OpenCode, and Codex CLI transcripts.

Each adapter flattens its native format into generic events:
  {"type": "message",   "role": "assistant"|"user", "content": "..."}
  {"type": "tool_call", "name": "...", "status": "completed"|"cancelled", "args": {...}}
  {"type": "thought",   "role": "assistant", "content": "..."}

Claude Code (~/.claude/projects/<proj>/*.jsonl):
  {"type": "assistant", "message": {"role": "assistant", "content": [
      {"type": "text", "text": "..."} | {"type": "tool_use", "name": "...", "input": {...}}]}}

OpenCode (~/.local/share/opencode/storage/message/<sessionID>/*.json):
  one JSON file per message: {"role": "...", "parts": [
      {"type": "text", "text": "..."} | {"type": "tool", "tool": "...", "state": {...}}]}

Codex CLI (~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl):
  {"type": "response_item", "payload": {"type": "message", "role": "assistant",
      "content": [{"type": "output_text", "text": "..."}]}}
  {"type": "response_item", "payload": {"type": "function_call", "name": "...",
      "arguments": "{...}"}}
  {"type": "response_item", "payload": {"type": "reasoning", "summary": [...]}}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def _flatten_content(content) -> str:
    """Flatten Anthropic/OpenAI-style content blocks into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") in ("text", "output_text", "input_text"):
                    parts.append(block.get("text", "") or "")
        return "\n".join(p for p in parts if p)
    return ""


def _events_from_claude_line(obj: dict) -> list[dict]:
    events: list[dict] = []
    mtype = obj.get("type")
    if mtype not in ("assistant", "user"):
        return events
    msg = obj.get("message") or {}
    role = msg.get("role", mtype)
    content = msg.get("content", "")
    if role == "assistant":
        events.append({"type": "message", "role": "assistant",
                       "content": _flatten_content(content)})
        for block in (content if isinstance(content, list) else []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                events.append({"type": "tool_call", "name": block.get("name", "unknown"),
                               "status": "completed", "args": block.get("input") or {}})
    elif role == "user":
        text = _flatten_content(content)
        if text:
            events.append({"type": "message", "role": "user", "content": text})
    return events


def load_claude_session(path: str | Path) -> list[dict]:
    """Flatten a Claude Code transcript (~/.claude/projects/<proj>/*.jsonl)."""
    events: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.extend(_events_from_claude_line(obj))
    return events


def load_opencode_session(path: str | Path) -> list[dict]:
    """Flatten an OpenCode session directory (storage/message/<sessionID>/*.json).

    ``path`` may be a directory of message files or a combined JSONL file.
    """
    p = Path(path)
    records: list[dict] = []
    if p.is_dir():
        for f in sorted(p.glob("*.json")):
            try:
                obj = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue
            records.append(obj)
    else:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    events: list[dict] = []
    for msg in records:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role") or msg.get("data", {}).get("role")
        parts = msg.get("parts") or msg.get("data", {}).get("parts") or []
        if role == "assistant":
            text = "\n".join(part.get("text", "") or "" for part in parts
                             if isinstance(part, dict) and part.get("type") == "text")
            events.append({"type": "message", "role": "assistant", "content": text})
            for part in parts:
                if isinstance(part, dict) and part.get("type") == "tool":
                    state = part.get("state") or {}
                    status = state.get("status", "completed")
                    events.append({"type": "tool_call", "name": part.get("tool", "unknown"),
                                   "status": status, "args": state.get("input") or {}})
        elif role == "user":
            text = "\n".join(part.get("text", "") or "" for part in parts
                             if isinstance(part, dict) and part.get("type") == "text")
            if text:
                events.append({"type": "message", "role": "user", "content": text})
    return events


def _events_from_codex_line(obj: dict) -> list[dict]:
    events: list[dict] = []
    if obj.get("type") != "response_item":
        return events
    payload = obj.get("payload") or {}
    ptype = payload.get("type")
    if ptype == "message":
        role = payload.get("role")
        text = _flatten_content(payload.get("content"))
        if role == "assistant":
            events.append({"type": "message", "role": "assistant", "content": text})
        elif role == "user" and text:
            events.append({"type": "message", "role": "user", "content": text})
    elif ptype == "function_call":
        name = payload.get("name", "unknown")
        raw_args = payload.get("arguments") or "{}"
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            args = {}
        events.append({"type": "tool_call", "name": name, "status": "completed", "args": args})
    elif ptype == "reasoning":
        summary = payload.get("summary") or []
        text = " ".join(
            s.get("text", "") for s in summary if isinstance(s, dict) and s.get("text")
        )
        if text.strip():
            events.append({"type": "thought", "role": "assistant", "content": text})
    return events


def load_codex_session(path: str | Path) -> list[dict]:
    """Flatten a Codex CLI rollout transcript (~/.codex/sessions/.../rollout-*.jsonl)."""
    events: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.extend(_events_from_codex_line(obj))
    return events


# ---------------------------------------------------------------------------
# Format detection + unified entry
# ---------------------------------------------------------------------------

def detect_format(path: str | Path) -> str:
    p = Path(path)
    sp = str(p)
    if p.is_dir() or "opencode" in sp:
        return "opencode"
    if "rollout-" in p.name or ".codex" in sp:
        return "codex"
    if ".claude" in sp:
        return "claude"
    if ".gemini" in sp:
        return "gemini"
    # sniff the first JSON line
    try:
        with p.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    break
                if obj.get("type") == "response_item" or "rollout" in sp:
                    return "codex"
                if obj.get("type") in ("assistant", "user") and "message" in obj:
                    return "claude"
                if obj.get("type") == "gemini" or "$set" in obj:
                    return "gemini"
                break
    except (OSError, json.JSONDecodeError):
        pass
    return "generic"


def audit_transcript(path: str | Path, root: str | Path = "."):
    """Audit any supported transcript with automatic format detection."""
    from .analyzer import audit_session

    fmt = detect_format(path)
    if fmt == "gemini":
        from .gemini_adapter import audit_gemini
        return audit_gemini(path, root=root), fmt
    loaders = {"claude": load_claude_session, "opencode": load_opencode_session,
               "codex": load_codex_session}
    loader = loaders.get(fmt)
    if loader is None:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        return audit_session(lines, root=root), fmt
    return audit_session(loader(path), root=root), fmt
