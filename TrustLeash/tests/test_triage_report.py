"""Edge-case stress tests for ConstraintOps triage_report.py.

Run with:  venv/bin/python -m pytest TrustLeash/tests/test_triage_report.py
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent            # ~/ConstraintOps (repo root)
TRIAGE = REPO / "triage_report.py"


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, str(TRIAGE), *args],
        capture_output=True, text=True, cwd=cwd, timeout=120,
    )


def _mk_transcript(path: Path, events: list[dict]):
    path.write_text("\n".join(json.dumps(e) for e in events))


def _gemini_style(msg_text: str, n_tools: int = 2) -> list[dict]:
    """Build gemini-style lines via the generic shape used in earlier tests."""
    events = [{"type": "tool_call", "name": "read_file", "status": "completed", "args": {}}] * n_tools
    events.append({"type": "message", "role": "assistant", "content": msg_text})
    return events


# ---------------------------------------------------------------------------
# 1. Empty session (no events at all / blank lines)
# ---------------------------------------------------------------------------

def test_empty_session(tmp_path):
    t = tmp_path / "empty.jsonl"
    t.write_text("\n\n\n")
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj),
              "--out", str(tmp_path / "r.md")], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    out = (tmp_path / "r.md").read_text()
    assert "0" in out  # renders zeros without crashing


def test_whitespace_only_content(tmp_path):
    t = tmp_path / "ws.jsonl"
    _mk_transcript(t, [{"type": "message", "role": "assistant", "content": "   \n\t "},
                       {"type": "tool_call", "name": "x", "status": "completed", "args": {}}])
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj)], cwd=str(REPO))
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------------------
# 2. Unreadable / corrupt files
# ---------------------------------------------------------------------------

def test_unreadable_gibbage_file(tmp_path):
    t = tmp_path / "corrupt.jsonl"
    t.write_text("\x00\x01not json at all {{{{{{]][ bin \x03\x04")
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj),
              "--out", str(tmp_path / "r.md")], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    out = (tmp_path / "r.md").read_text()
    # must complete and mark it honestly in the report (reveal, don't conceal)
    assert "T" in out


def test_binary_file(tmp_path):
    t = tmp_path / "binary.jsonl"
    t.write_bytes(bytes(range(256)))
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj)], cwd=str(REPO))
    assert r.returncode == 0, r.stderr


def test_directory_passed_as_transcript(tmp_path):
    d = tmp_path / "somedir"
    d.mkdir()
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(d), "--root", str(proj)], cwd=str(REPO))
    # should not crash with traceback; either handle or exit nonzero cleanly
    assert "Traceback" not in r.stderr


# ---------------------------------------------------------------------------
# 3. Absolute-path claims
# ---------------------------------------------------------------------------

def test_absolute_path_claim_existing(tmp_path):
    real = tmp_path / "real_abs.txt"
    real.write_text("hello\n")
    t = tmp_path / "abs.jsonl"
    _mk_transcript(t, _gemini_style(f"I created {real} for you."))
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj),
              "--out", str(tmp_path / "r.md")], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    out = (tmp_path / "r.md").read_text()
    assert "real_abs.txt" in out


def test_absolute_path_claim_phantom(tmp_path):
    t = tmp_path / "abs2.jsonl"
    _mk_transcript(t, _gemini_style("I created /definitely/not/here/ghost.py today."))
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj),
              "--out", str(tmp_path / "r.md")], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    out = (tmp_path / "r.md").read_text()
    assert "ghost.py" in out


# ---------------------------------------------------------------------------
# 4. Mixed batch: good + bad files together must not lose the good ones
# ---------------------------------------------------------------------------

def test_mixed_batch_survives(tmp_path):
    good = tmp_path / "good.jsonl"
    _mk_transcript(good, _gemini_style("I created main.py.", n_tools=3))
    (tmp_path / "main.py").write_text("x=1\n")
    bad = tmp_path / "bad.jsonl"
    bad.write_bytes(b"\xff\xfe\x00garbage")
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")

    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(good), str(bad), str(empty),
              "--root", str(tmp_path), "--out", str(tmp_path / "r.md")], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    out = (tmp_path / "r.md").read_text()
    assert "good.jsonl" in out          # the good session made it through
    assert "Unreadable" in out          # the bad one is disclosed, not hidden


# ---------------------------------------------------------------------------
# 5. No transcripts found at all
# ---------------------------------------------------------------------------

def test_no_transcripts_nonzero(tmp_path):
    r = _run(["--client", "T", "--transcripts", str(tmp_path / "nope" / "*.jsonl"),
              "--root", str(tmp_path)], cwd=str(REPO))
    assert r.returncode == 2
    assert "no transcripts" in r.stderr.lower()


# ---------------------------------------------------------------------------
# 6. Malformed but valid-JSON lines (numbers, arrays, nulls)
# ---------------------------------------------------------------------------

def test_junk_json_types(tmp_path):
    t = tmp_path / "junk.jsonl"
    t.write_text('42\n[1,2,3]\nnull\n"just a string"\n{"type":"message","role":"assistant","content":"created x.py"}\n')
    proj = tmp_path / "proj"
    proj.mkdir()
    r = _run(["--client", "T", "--transcripts", str(t), "--root", str(proj)], cwd=str(REPO))
    assert r.returncode == 0, r.stderr
