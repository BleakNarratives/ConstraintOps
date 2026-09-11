"""Cannibal Boardroom — run the same task across multiple agents.

    python boardroom/run.py --task tasks/todo_api.json --agents gemini,codex

Each agent gets the identical prompt. Output saved to boardroom/sessions/<agent>/.
TrustLeash audits each session after completion.

Agents:
  gemini  — Gemini CLI (google-gemini/gemini-cli)
  codex   — OpenAI Codex CLI (openai/codex)
  freebuff — Freebuff agent (manual: paste prompt, save transcript)
  claude  — Claude Code CLI (anthropic/claude-code)
  copilot — GitHub Copilot (manual: VS Code, save output)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SESSIONS = HERE / "boardroom" / "sessions"


def load_task(task_path: Path) -> dict:
    return json.loads(task_path.read_text())


def run_gemini(task: dict, out_dir: Path) -> Path:
    """Run task via Gemini CLI."""
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript = out_dir / "session.jsonl"
    prompt = task["prompt"]

    # Write prompt to a temp file for gemini -i
    prompt_file = out_dir / "prompt.txt"
    prompt_file.write_text(prompt)

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt, "--output_format", "json"],
            capture_output=True, text=True,
            timeout=task.get("timeout_seconds", 120),
            cwd=str(out_dir),
        )
        # Save output
        (out_dir / "response.txt").write_text(result.stdout)
        (out_dir / "stderr.txt").write_text(result.stderr)

        # If gemini produced a session transcript, copy it
        # Gemini CLI stores transcripts in ~/.gemini/tmp/
        gemini_home = Path.home() / ".gemini" / "tmp"
        if gemini_home.exists():
            sessions = sorted(gemini_home.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)
            if sessions:
                latest = sessions[-1]
                if latest.stat().st_mtime > time.time() - 300:  # within last 5 min
                    transcript.write_bytes(latest.read_bytes())
                    return transcript

        # Fallback: save the response as a pseudo-transcript
        events = []
        events.append(json.dumps({"type": "message", "role": "user", "content": prompt}))
        events.append(json.dumps({"type": "message", "role": "assistant", "content": result.stdout}))
        transcript.write_text("\n".join(events))
        return transcript

    except FileNotFoundError:
        (out_dir / "error.txt").write_text("gemini CLI not found on PATH")
        return transcript
    except subprocess.TimeoutExpired:
        (out_dir / "error.txt").write_text(f"timed out after {task.get('timeout_seconds', 120)}s")
        return transcript


def run_codex(task: dict, out_dir: Path) -> Path:
    """Run task via Codex CLI."""
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript = out_dir / "session.jsonl"
    prompt = task["prompt"]

    try:
        result = subprocess.run(
            ["codex", "--quiet", prompt],
            capture_output=True, text=True,
            timeout=task.get("timeout_seconds", 120),
            cwd=str(out_dir),
        )
        (out_dir / "response.txt").write_text(result.stdout)
        (out_dir / "stderr.txt").write_text(result.stderr)

        # Codex stores sessions in ~/.codex/sessions/
        codex_home = Path.home() / ".codex" / "sessions"
        if codex_home.exists():
            rollouts = sorted(codex_home.rglob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime)
            if rollouts:
                latest = rollouts[-1]
                if latest.stat().st_mtime > time.time() - 300:
                    transcript.write_bytes(latest.read_bytes())
                    return transcript

        # Fallback
        events = []
        events.append(json.dumps({"type": "message", "role": "user", "content": prompt}))
        events.append(json.dumps({"type": "message", "role": "assistant", "content": result.stdout}))
        transcript.write_text("\n".join(events))
        return transcript

    except FileNotFoundError:
        (out_dir / "error.txt").write_text("codex CLI not found on PATH")
        return transcript
    except subprocess.TimeoutExpired:
        (out_dir / "error.txt").write_text(f"timed out after {task.get('timeout_seconds', 120)}s")
        return transcript


def run_freebuff(task: dict, out_dir: Path) -> Path:
    """Placeholder for Freebuff — requires manual transcript paste."""
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript = out_dir / "session.jsonl"
    prompt = task["prompt"]

    # Write the prompt so it's ready
    (out_dir / "prompt.txt").write_text(prompt)
    (out_dir / "instructions.txt").write_text(
        "1. Paste this prompt into Freebuff: the chat interface\n"
        "2. Let it complete the task\n"
        "3. Export/copy the transcript\n"
        "4. Save it as boardroom/sessions/freebuff/session.jsonl\n"
        f"\nPrompt:\n{prompt}"
    )
    return transcript


def run_claude(task: dict, out_dir: Path) -> Path:
    """Run task via Claude Code CLI."""
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript = out_dir / "session.jsonl"
    prompt = task["prompt"]

    try:
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True, text=True,
            timeout=task.get("timeout_seconds", 120),
            cwd=str(out_dir),
        )
        (out_dir / "response.txt").write_text(result.stdout)
        (out_dir / "stderr.txt").write_text(result.stderr)

        # Claude Code stores sessions in ~/.claude/projects/
        claude_home = Path.home() / ".claude" / "projects"
        if claude_home.exists():
            sessions = sorted(claude_home.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)
            if sessions:
                latest = sessions[-1]
                if latest.stat().st_mtime > time.time() - 300:
                    transcript.write_bytes(latest.read_bytes())
                    return transcript

        events = []
        events.append(json.dumps({"type": "message", "role": "user", "content": prompt}))
        events.append(json.dumps({"type": "message", "role": "assistant", "content": result.stdout}))
        transcript.write_text("\n".join(events))
        return transcript

    except FileNotFoundError:
        (out_dir / "error.txt").write_text("claude CLI not found on PATH")
        return transcript
    except subprocess.TimeoutExpired:
        (out_dir / "error.txt").write_text(f"timed out after {task.get('timeout_seconds', 120)}s")
        return transcript


RUNNERS = {
    "gemini": run_gemini,
    "codex": run_codex,
    "freebuff": run_freebuff,
    "claude": run_claude,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Cannibal Boardroom — run task across agents")
    ap.add_argument("--task", required=True, help="path to task JSON")
    ap.add_argument("--agents", default="gemini,codex", help="comma-separated agent names")
    ap.add_argument("--out", default=None, help="override output directory")
    args = ap.parse_args()

    task = load_task(Path(args.task))
    agents = [a.strip() for a in args.agents.split(",")]

    print(f"Task: {task['name']}")
    print(f"Agents: {', '.join(agents)}")
    print()

    results = {}
    for agent in agents:
        if agent not in RUNNERS:
            print(f"  [skip] {agent}: no runner (manual — see instructions.txt)")
            continue

        out_dir = Path(args.out) / agent if args.out else SESSIONS / agent
        print(f"  [{agent}] running...", end=" ", flush=True)

        start = time.time()
        transcript = RUNNERS[agent](task, out_dir)
        elapsed = round(time.time() - start, 1)

        # Check for errors
        error_file = out_dir / "error.txt"
        if error_file.exists():
            print(f"FAILED ({elapsed}s): {error_file.read_text()[:60]}")
            results[agent] = {"status": "failed", "error": error_file.read_text()[:200]}
        else:
            print(f"done ({elapsed}s) -> {transcript}")
            results[agent] = {"status": "ok", "transcript": str(transcript), "elapsed": elapsed}

    # Save summary
    summary = {
        "task": task["name"],
        "timestamp": datetime.now().isoformat(),
        "agents": results,
    }
    summary_path = SESSIONS / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
