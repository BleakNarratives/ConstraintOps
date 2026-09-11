"""Overlay feeder — reads a transcript, writes audit_status.json for the live overlay.

    python scripts/overlay_feeder.py --watch ~/.gemini/tmp/*/chats/session-latest.jsonl

Polls the transcript every 5 seconds, re-runs the audit, writes status JSON.
The overlay.html page reads this JSON and updates the dashboard.

Run both:
    python scripts/overlay_feeder.py --watch <transcript.jsonl>
    # then open overlay.html in a browser
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "TrustLeash"))

from trustleash.adapters import audit_transcript  # noqa: E402

STATUS_FILE = Path(__file__).resolve().parent.parent / "site" / "audit_status.json"


def read_status(transcript: Path) -> dict:
    """Run audit and build status dict."""
    try:
        result, fmt = audit_transcript(transcript, root=Path.home())
    except Exception as e:
        return {"error": str(e)[:200], "verdict": "ERROR", "source": "error"}

    log = []
    for p in (result.phantom_paths or [])[:10]:
        log.append({"time": datetime.now().strftime("%H:%M:%S"), "text": f"✗ phantom: {p}", "type": "claim"})
    for p in (result.verified_paths or [])[:5]:
        log.append({"time": datetime.now().strftime("%H:%M:%S"), "text": f"✓ verified: {p}", "type": "verified"})

    if not log:
        log.append({"time": datetime.now().strftime("%H:%M:%S"), "text": "No claims detected yet..."})

    return {
        "messages": result.messages,
        "tools": result.tool_calls,
        "ratio": result.ratio if result.ratio != float("inf") else 99.9,
        "claims": len(result.claimed_paths),
        "phantoms": len(result.phantom_paths),
        "verified": result.verified_real,
        "verdict": result.verdict,
        "source": fmt,
        "file": transcript.name,
        "hedges": result.register.hedge_count,
        "score": round(result.register.corruption_score, 4),
        "log": log,
        "timestamp": datetime.now().isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Overlay feeder — writes audit_status.json")
    ap.add_argument("--watch", required=True, help="transcript to monitor")
    ap.add_argument("--interval", type=int, default=5, help="poll interval in seconds")
    args = ap.parse_args()

    transcript = Path(args.watch).expanduser()
    if not transcript.exists():
        print(f"error: file not found: {transcript}", file=sys.stderr)
        return 2

    print(f"Monitoring {transcript} every {args.interval}s -> {STATUS_FILE}")
    print("Open overlay.html in a browser to see the dashboard.")

    try:
        while True:
            status = read_status(transcript)
            STATUS_FILE.write_text(json.dumps(status, indent=2))
            v = status.get("verdict", "?")
            c = status.get("phantoms", 0)
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] {v} | "
                  f"{status.get('messages',0)} msgs, {status.get('tools',0)} tools, "
                  f"{c} phantoms", end="\r")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
