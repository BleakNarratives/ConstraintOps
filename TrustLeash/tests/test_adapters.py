"""Tests for multi-agent adapters: claude, opencode, codex, plus detection."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trustleash.adapters import (
    audit_transcript,
    detect_format,
    load_claude_session,
    load_codex_session,
    load_opencode_session,
)


def _j(tmp_path, name, events):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(e) for e in events))
    return p


# ---------------------------------------------------------------------------
# Claude Code
# ---------------------------------------------------------------------------

def test_claude_adapter_extracts_text_and_tools(tmp_path):
    events = [
        {"type": "user", "message": {"role": "user",
         "content": [{"type": "text", "text": "fix the bug"}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "I created src/fix.py to resolve it."},
            {"type": "tool_use", "name": "Write", "input": {"path": "src/fix.py"}},
        ]}},
    ]
    p = _j(tmp_path, "claude-session.jsonl", events)
    evs = load_claude_session(p)
    msgs = [e for e in evs if e["type"] == "message"]
    tools = [e for e in evs if e["type"] == "tool_call"]
    assert len(msgs) == 2
    assert "src/fix.py" in msgs[1]["content"]
    assert len(tools) == 1 and tools[0]["name"] == "Write"


def test_claude_session_audit(tmp_path):
    events = [
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Created ghost.py"}]}},
    ] * 30
    p = _j(tmp_path, "s.jsonl", events)
    result, fmt = audit_transcript(p, root=tmp_path)
    assert fmt == "generic" or fmt == "claude"
    assert "ghost.py" in result.phantom_paths


# ---------------------------------------------------------------------------
# OpenCode
# ---------------------------------------------------------------------------

def test_opencode_adapter_directory(tmp_path):
    session_dir = tmp_path / "opencode" / "msg" / "sess1"
    session_dir.mkdir(parents=True)
    (session_dir / "msg01.json").write_text(json.dumps({
        "role": "user", "parts": [{"type": "text", "text": "build it"}]}))
    (session_dir / "msg02.json").write_text(json.dumps({
        "role": "assistant", "parts": [
            {"type": "text", "text": "I created main.py"},
            {"type": "tool", "tool": "write", "state": {"status": "completed",
             "input": {"path": "main.py"}}}]}))
    evs = load_opencode_session(session_dir)
    tools = [e for e in evs if e["type"] == "tool_call"]
    msgs = [e for e in evs if e["type"] == "message"]
    assert len(tools) == 1 and tools[0]["name"] == "write"
    assert len(msgs) == 2


# ---------------------------------------------------------------------------
# Codex
# ---------------------------------------------------------------------------

def test_codex_adapter_full(tmp_path):
    events = [
        {"type": "session_meta", "payload": {"session_id": "x"}},
        {"type": "response_item", "payload": {"type": "message", "role": "user",
         "content": [{"type": "input_text", "text": "do the thing"}]}},
        {"type": "response_item", "payload": {"type": "function_call",
         "name": "exec_command", "arguments": "{\"cmd\": [\"ls\"]}"}},
        {"type": "response_item", "payload": {"type": "message", "role": "assistant",
         "content": [{"type": "output_text", "text": "I created out.txt for you."}]}},
        {"type": "response_item", "payload": {"type": "reasoning",
         "summary": [{"type": "summary_text", "text": "planning the write"}]}},
    ]
    p = _j(tmp_path, "rollout-2026-09-11T00-00-00-abc.jsonl", events)
    evs = load_codex_session(p)
    msgs = [e for e in evs if e["type"] == "message"]
    tools = [e for e in evs if e["type"] == "tool_call"]
    thoughts = [e for e in evs if e["type"] == "thought"]
    assert len(msgs) == 2 and len(tools) == 1 and len(thoughts) == 1
    assert "out.txt" in msgs[1]["content"]

    # detection by filename
    assert detect_format(p) == "codex"

    # full audit: phantom claim (out.txt never written to tmp_path root)
    result, fmt = audit_transcript(p, root=tmp_path)
    assert fmt == "codex"
    assert "out.txt" in result.phantom_paths


def test_codex_real_session_shape():
    """Smoke: adapter must handle the real Codex transcript on this machine."""
    import glob
    rolls = sorted(glob.glob("/home/bleaknarratives/.codex/sessions/*/*/*/rollout-*.jsonl"))
    if not rolls:
        return  # no codex data; skip silently
    evs = load_codex_session(rolls[-1])
    assert any(e["type"] == "tool_call" for e in evs)
    assert any(e["type"] == "message" and e["role"] == "assistant" for e in evs)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def test_detect_gemini_by_path():
    p = Path("/home/bleaknarratives/.gemini/tmp/x/chats/session-2026-09-09.jsonl")
    assert detect_format(p) == "gemini"


def test_detect_claude_by_content(tmp_path):
    events = [{"type": "assistant", "message": {"role": "assistant",
               "content": [{"type": "text", "text": "hi"}]}}]
    p = _j(tmp_path, "unknown-name.jsonl", events)
    assert detect_format(p) == "claude"
