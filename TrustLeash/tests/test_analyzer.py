"""Tests for TrustLeash analyzer, verifier, report, CLI."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trustleash.analyzer import audit_session, sniff_register, extract_claimed_paths
from trustleash.report import render_markdown

ROOT = Path(__file__).resolve().parents[1]


def _ev_assistant(text):
    return {"type": "message", "role": "assistant", "content": text}


def _ev_tool(name="write_file", path="src/foo.py"):
    return {"type": "tool_call", "name": name, "args": {"path": path}}


def _lines(events):
    return [json.dumps(e) for e in events]


# ---------------------------------------------------------------------------
# Register sniff
# ---------------------------------------------------------------------------

def test_sniff_counts_hedges():
    sniff = sniff_register("It seems fine. Perhaps we should. I just need to clarify.")
    assert sniff.hedge_count >= 3
    assert sniff.total_tokens > 0


def test_sniff_clean_text():
    sniff = sniff_register("Created parser.py. Added tests. All checks pass.")
    assert sniff.hedge_count == 0
    assert sniff.larp_count == 0


def test_corruption_score_zero_on_empty():
    assert sniff_register("").corruption_score == 0.0


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------

def test_extract_created_paths():
    text = "I created src/engine.py and wrote tests/test_engine.py for you."
    paths = extract_claimed_paths(text)
    assert "src/engine.py" in paths
    assert "tests/test_engine.py" in paths


def test_extract_dedupes():
    text = "Created a.py. Then updated a.py again."
    paths = extract_claimed_paths(text)
    assert paths.count("a.py") == 1


# ---------------------------------------------------------------------------
# Full session audit
# ---------------------------------------------------------------------------

def test_clean_session(tmp_path):
    (tmp_path / "engine.py").write_text("print('hi')\n")
    events = [
        _ev_tool(path="engine.py"),
        _ev_assistant("Created engine.py with the parsing loop."),
        _ev_tool(),
    ]
    result = audit_session(_lines(events), root=tmp_path)
    assert result.verdict == "CLEAN"
    assert result.verified_real == 1
    assert result.phantom_paths == []


def test_corrupt_session_like_gemini(tmp_path):
    # 90 messages, 10 tool calls, phantom claims, hedge-heavy prose
    events = []
    for _ in range(10):
        events.append(_ev_tool(name="read_file"))
    for i in range(90):
        events.append(_ev_assistant(
            "It seems I created src/module.py. Perhaps feel free to reach out. "
            "I just need to clarify. Apologies for any confusion. It seems about right."
        ))
    result = audit_session(_lines(events), root=tmp_path)
    assert result.messages == 90
    assert result.tool_calls == 10
    assert result.ratio == 9.0
    assert result.verdict == "CORRUPT"
    assert len(result.phantom_paths) > 0
    assert result.register.hedge_count > 5


def test_all_talk_no_tools_is_corrupt(tmp_path):
    events = [_ev_assistant("I created main.py and it works!")] * 20
    result = audit_session(_lines(events), root=tmp_path)
    assert result.verdict == "CORRUPT"
    assert "main.py" in result.phantom_paths


def test_inf_ratio_repr():
    events = [_ev_assistant("hello")]
    result = audit_session(_lines(events), root=".")
    assert result.ratio == float("inf")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def test_report_renders_verdict_and_phantoms(tmp_path):
    events = [_ev_assistant("I created ghost.py")] * 15
    result = audit_session(_lines(events), root=tmp_path)
    md = render_markdown(result)
    assert "CORRUPT" in md
    assert "ghost.py" in md


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

def test_cli_strict_exit_code(tmp_path):
    from trustleash.__main__ import main
    transcript = tmp_path / "session.jsonl"
    events = [_ev_assistant("It seems I created ghost.py. Apologies.")] * 40
    transcript.write_text("\n".join(_lines(events)))
    rc = main(["audit", str(transcript), "--root", str(tmp_path), "--strict"])
    assert rc == 1


def test_cli_clean_exit_zero(tmp_path):
    from trustleash.__main__ import main
    transcript = tmp_path / "session.jsonl"
    (tmp_path / "real.py").write_text("x = 1\n")
    events = [_ev_tool(path="real.py"), _ev_assistant("Created real.py.")]
    transcript.write_text("\n".join(_lines(events)))
    rc = main(["audit", str(transcript), "--root", str(tmp_path)])
    assert rc == 0
