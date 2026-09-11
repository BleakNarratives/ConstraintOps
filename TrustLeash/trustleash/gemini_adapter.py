"""Adapter for Gemini CLI session transcripts (~/.gemini/tmp/*/chats/*.jsonl).

Gemini transcripts are JSONL with:
  - a "sessionId" header line
  - {"id": ..., "type": "user"|"gemini"|"info"|"error", "content": ...} message lines
  - "$set" state-chunk lines (ignored)

Gemini message lines: {"id","type":"gemini","content":"...","toolCalls":[...]}
toolCalls entries: {"name": ..., "args": {...}, "status": ...} — status may be
"cancelled" (user denied) or "completed".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def load_gemini_session(path: str | Path) -> list[dict]:
    """Flatten a Gemini transcript into generic events compatible with audit_session()."""
    events: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue

        if "id" in obj and "type" in obj and "$set" not in obj:
            mtype = obj.get("type")
            content = obj.get("content", "")
            if mtype == "gemini":
                # every gemini turn counts as a message, even if content is empty
                # (matches the manual-audit methodology: msg/tool ratio uses all turns)
                events.append({"type": "message", "role": "assistant", "content": content or ""})
                # thinking-block prose is scanned for claims but flagged as thought-sourced
                thought_text = " ".join(
                    (t.get("description", "") or "") + " " + (t.get("subject", "") or "")
                    for t in (obj.get("thoughts") or []) if isinstance(t, dict)
                )
                if thought_text.strip():
                    events.append({"type": "thought", "role": "assistant", "content": thought_text})
                for tc in obj.get("toolCalls") or []:
                    status = tc.get("status", "completed")
                    events.append({
                        "type": "tool_call",
                        "name": tc.get("name", "unknown"),
                        "status": status,
                        "args": tc.get("args") or {},
                    })
            elif mtype == "user":
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("text")
                    )
                if content:
                    events.append({"type": "message", "role": "user", "content": content})
        # "$set" chunks and sessionId headers are intentionally skipped
    return events


def audit_gemini(path: str | Path, root: str | Path = "."):
    """Audit a Gemini CLI transcript. Returns AuditResult."""
    from .analyzer import audit_session
    return audit_session(load_gemini_session(path), root=root)
