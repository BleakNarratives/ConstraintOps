"""Build the overlay with embedded data — no fetch, no CORS, no path issues.

    python scripts/build_overlay.py --transcript ~/.gemini/tmp/.../session.jsonl
    python scripts/build_overlay.py --transcript ~/.gemini/tmp/.../session.jsonl --watch

Generates site/overlay.html with the audit data baked into a <script> tag.
The page works standalone — open it in any browser, no server needed.

--watch: rebuild every 5 seconds (for live streaming).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TEMPLATE = HERE / "site" / "overlay.html"
OUTPUT = HERE / "site" / "live_audit.html"

sys.path.insert(0, str(HERE / "TrustLeash"))
from trustleash.adapters import audit_transcript  # noqa: E402


def build_data(transcript: Path) -> dict:
    """Run audit, return JSON-serializable status dict."""
    try:
        result, fmt = audit_transcript(transcript, root=Path.home())
    except Exception as e:
        return {"error": str(e)[:200], "verdict": "ERROR", "messages": 0, "tools": 0,
                "ratio": 0, "claims": 0, "phantoms": 0, "verified": 0,
                "source": "error", "file": transcript.name, "hedges": 0,
                "score": 0, "log": [], "timestamp": datetime.now().isoformat()}

    log = []
    for p in (result.phantom_paths or [])[:10]:
        log.append({"time": datetime.now().strftime("%H:%M:%S"), "text": f"phantom: {p}", "type": "claim"})
    for p in (result.verified_paths or [])[:5]:
        log.append({"time": datetime.now().strftime("%H:%M:%S"), "text": f"verified: {p}", "type": "verified"})

    return {
        "messages": result.messages, "tools": result.tool_calls,
        "ratio": round(result.ratio, 1) if result.ratio != float("inf") else 99.9,
        "claims": len(result.claimed_paths), "phantoms": len(result.phantom_paths),
        "verified": result.verified_real, "verdict": result.verdict,
        "source": fmt, "file": transcript.name,
        "hedges": result.register.hedge_count,
        "score": round(result.register.corruption_score, 4),
        "log": log, "timestamp": datetime.now().isoformat(),
    }


def bake(data: dict) -> str:
    """Read overlay.html template, replace AUDIT_DATA_PLACEHOLDER with data."""
    template = TEMPLATE.read_text(encoding="utf-8")
    return template.replace("AUDIT_DATA_PLACEHOLDER", json.dumps(data))


def main() -> int:
    ap = argparse.ArgumentParser(description="Build overlay with baked-in audit data")
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--interval", type=int, default=5)
    args = ap.parse_args()

    transcript = Path(args.transcript).expanduser()
    if not transcript.exists():
        print(f"error: {transcript}", file=sys.stderr)
        return 2

    if not args.watch:
        data = build_data(transcript)
        OUTPUT.write_text(bake(data), encoding="utf-8")
        print(f"built {OUTPUT}")
        print(f"verdict: {data['verdict']} | {data['phantoms']} phantoms | {data['claims']} claims")
        return 0

    # watch mode
    print(f"watching {transcript} every {args.interval}s -> {OUTPUT}")
    try:
        while True:
            data = build_data(transcript)
            OUTPUT.write_text(bake(data), encoding="utf-8")
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] {data['verdict']} | "
                  f"{data['phantoms']} phantoms", end="\r")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
