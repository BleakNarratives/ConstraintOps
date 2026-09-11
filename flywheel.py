"""ConstraintOps flywheel — one command, self-healing, each stage feeds the next.

    python flywheel.py            # run all stages
    python flywheel.py --stage N  # run from stage N onward
    python flywheel.py --quiet    # only print failures + summary

Design contract (the doctrine, in code):
  - We reveal, we don't conceal: every stage result is recorded, failures loudest.
  - We respond, we don't react: a failing stage is quarantined and logged to
    state/failures.json; the chain continues with degraded inputs rather than dying.
  - Each move accelerates the next: stage outputs feed stage inputs (tests verify
    the instrument -> the sweep uses it -> the triage report is built from the
    sweep -> the state journal snapshots everything for the next run's baseline).
  - Regain control on failure: every failure produces a concrete artifact (log
    entry + retry hint), never a silent skip, never a half-truth "success".
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
VENV_PY = HOME / "venv" / "bin" / "python"
TL = HERE / "TrustLeash"
STATE_DIR = HERE / "state"


class Stage:
    def __init__(self, num: int, name: str, fn):
        self.num, self.name, self.fn = num, name, fn


def run_tests() -> str:
    """Stage 1: verify the instrument. Everything downstream trusts this."""
    r = subprocess.run([str(VENV_PY), "-m", "pytest", "tests/", "-q"],
                       cwd=str(TL), capture_output=True, text=True, timeout=300)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "(no output)"
    if r.returncode != 0:
        raise RuntimeError(f"pytest failed: {tail}")
    return tail


def run_sweep() -> str:
    """Stage 2: sweep all local transcripts into the corruption leaderboard."""
    out = TL / "leaderboard.md"
    r = subprocess.run([str(VENV_PY), str(TL / "scripts" / "sweep.py"), "--out", str(out)],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"sweep failed: {r.stderr.strip()[:200]}")
    n = sum(1 for line in r.stdout.splitlines() if line.startswith("| gemini") or line.startswith("| codex")
            or line.startswith("| claude") or line.startswith("| opencode"))
    return f"{n} sessions audited -> {out.name}"


def run_triage() -> str:
    """Stage 3: regenerate the self-portfolio triage report from the live sweep."""
    transcripts = sorted((HOME / ".gemini/tmp/bleaknarratives/chats").glob("*.jsonl"))
    codex = sorted(HOME.glob(".codex/sessions/*/*/*/rollout-*.jsonl"))
    if not transcripts:
        raise RuntimeError("no gemini transcripts found — evidence base missing")
    out = HERE / "portfolio" / "live_triage_self.md"
    r = subprocess.run(
        [str(VENV_PY), str(HERE / "triage_report.py"),
         "--client", "Self / BleakNarratives",
         "--transcripts", *[str(p) for p in transcripts[:5]], *[str(p) for p in codex[:3]],
         "--root", str(HOME / "bleaknarratives"), "--out", str(out)],
        capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"triage failed: {r.stderr.strip()[:200]}")
    return f"self-triage refreshed -> {out.name}"


def run_state() -> str:
    """Stage 4: snapshot the flywheel state for the next run's baseline."""
    STATE_DIR.mkdir(exist_ok=True)
    snap = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "leaderboard_exists": (TL / "leaderboard.md").exists(),
        "portfolio_live": (HERE / "portfolio" / "live_triage_self.md").exists(),
        "site_exists": (HERE / "site" / "index.html").exists(),
    }
    (STATE_DIR / "last_state.json").write_text(json.dumps(snap, indent=2))
    return f"state snapshotted -> state/last_state.json"


STAGES = [
    Stage(1, "verify instrument (pytest)", run_tests),
    Stage(2, "sweep transcripts (leaderboard)", run_sweep),
    Stage(3, "refresh self-triage report", run_triage),
    Stage(4, "snapshot state", run_state),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=1, help="start from this stage")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    STATE_DIR.mkdir(exist_ok=True)
    failures_file = STATE_DIR / "failures.json"
    failures = json.loads(failures_file.read_text()) if failures_file.exists() else []

    results, had_failure = [], False
    for stage in STAGES:
        if stage.num < args.stage:
            continue
        t0 = time.time()
        try:
            detail = stage.fn()
            results.append((stage.num, stage.name, "OK", detail, time.time() - t0))
            if not args.quiet:
                print(f"[{stage.num}/4] ✓ {stage.name} — {detail}")
        except Exception as e:
            had_failure = True
            detail = str(e)[:300]
            results.append((stage.num, stage.name, "FAIL", detail, time.time() - t0))
            print(f"[{stage.num}/4] ✗ {stage.name} — {detail}", file=sys.stderr)
            failures.append({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "stage": stage.num, "name": stage.name, "error": detail,
                "retry": f"python flywheel.py --stage {stage.num}",
            })
            # quarantine + continue: one broken stage must not stall the chain

    failures_file.write_text(json.dumps(failures[-50:], indent=2))

    print("\n== flywheel summary ==")
    for num, name, status, detail, dt in results:
        mark = "✓" if status == "OK" else "✗"
        print(f"  {mark} [{num}] {name} ({dt:.1f}s){' — ' + detail if status == 'FAIL' else ''}")
    if failures:
        print(f"\n{len(failures)} quarantined failure(s) on file: {failures_file}")
        print("regain control:  python flywheel.py --stage <N>")
    return 1 if had_failure else 0


if __name__ == "__main__":
    sys.exit(main())
