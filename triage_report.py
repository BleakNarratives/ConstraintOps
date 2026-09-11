"""ConstraintOps — AI Damage Triage report generator.

Wraps TrustLeash audits of a client's agent transcripts into the
client-ready deliverable defined in services/AI_DAMAGE_TRIAGE.md.

Usage:
    python triage_report.py --client "Acme Co" \
        --transcripts ~/.gemini/tmp/*/chats/*.jsonl \
        --root ~/client-project \
        --out report.md

Operator then does the human pass (per playbook) before sending.
"""

from __future__ import annotations

import argparse
import glob
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_TL = _HERE / "TrustLeash"
if str(_TL) not in sys.path:
    sys.path.insert(0, str(_TL))

from trustleash.adapters import audit_transcript  # noqa: E402


def _expand(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        matches = glob.glob(str(Path(p).expanduser()))
        out.extend(Path(m) for m in matches)
    return sorted(set(out))


def audit_all(transcripts: list[Path], root: Path) -> list[dict]:
    rows = []
    for t in transcripts:
        try:
            result, fmt = audit_transcript(t, root=root)
        except Exception as e:
            rows.append({"file": t.name, "fmt": "?", "error": str(e)[:80]})
            continue
        row = {
            "file": t.name, "fmt": fmt, "verdict": result.verdict,
            "messages": result.messages, "tools": result.tool_calls,
            "ratio": result.ratio,
            "claims": len(result.claimed_paths),
            "verified": result.verified_real,
            "verified_paths": result.verified_paths,
            "phantoms": result.phantom_paths,
            "hedges": result.register.hedge_count,
            "score": result.register.corruption_score,
        }
        # reveal-don't-conceal: a non-empty file that parses to zero events is
        # NOT clean — it is unreadable/unrecognized and must be disclosed.
        try:
            nonblank = sum(1 for ln in t.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip())
        except OSError:
            nonblank = -1
        if result.messages == 0 and result.tool_calls == 0:
            if nonblank > 0:
                row["error"] = (f"file has {nonblank} line(s) but no recognizable "
                                f"events — format unrecognized or file corrupt")
            elif nonblank == 0:
                row["error"] = "file is empty (no session data)"
        rows.append(row)
    return rows


def render(client: str, root: Path, rows: list[dict]) -> str:
    ok = [r for r in rows if r.get("verdict") and not r.get("error")]
    corrupt = [r for r in ok if r["verdict"] == "CORRUPT"]
    wavering = [r for r in ok if r["verdict"] == "WAVERING"]
    clean = [r for r in ok if r["verdict"] == "CLEAN"]
    errors = [r for r in rows if "error" in r]
    total_claims = sum(r.get("claims", 0) for r in ok)
    total_phantoms = sum(len(r.get("phantoms", [])) for r in ok)

    L: list[str] = []
    L.append(f"# AI Damage Triage Report — {client}")
    L.append("")
    L.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
             f"prepared under the ConstraintOps creed: we reveal, we don't conceal.*")
    L.append("")

    # 1. Executive summary
    L.append("## 1. Executive summary")
    L.append("")
    L.append(f"- Examined **{len(rows)}** session transcript(s) from your AI coding tools, "
             f"checked against the project at `{root}`.")
    if ok:
        L.append(f"- Your assistants claimed **{total_claims}** file(s) of work. "
                 f"**{total_claims - total_phantoms}** verified on disk; "
                 f"**{total_phantoms}** claimed but not present.")
    L.append(f"- Session verdicts: {len(corrupt)} serious concern(s), "
             f"{len(wavering)} needing review, {len(clean)} clean"
             + (f", {len(errors)} unreadable" if errors else "") + ".")
    if corrupt:
        worst = max(corrupt, key=lambda r: len(r.get("phantoms", [])))
        L.append(f"- Largest gap: `{worst['file']}` — "
                 f"{len(worst.get('phantoms', []))} file(s) described as created/modified "
                 f"that were not found.")
    L.append("- Nothing in this report is hidden from you: the appendix contains the "
             "complete evidence tables, and every finding can be re-verified with the "
             "commands included.")
    L.append("")

    # 2. What we examined
    L.append("## 2. What we examined")
    L.append("")
    L.append("| Session | Tool format | Messages | Tool calls | Ratio |")
    L.append("|---|---|---|---|---|")
    for r in ok:
        ratio = f"{r['ratio']:.1f}" if isinstance(r.get("ratio"), (int, float)) else str(r.get("ratio"))
        L.append(f"| `{r['file']}` | {r['fmt']} | {r['messages']} | {r['tools']} | {ratio} |")
    if errors:
        L.append("")
        L.append(f"Unreadable or empty sessions ({len(errors)} — included for "
                 f"completeness; these were NOT audited and are not counted as clean):")
        for r in errors:
            L.append(f"- `{r['file']}` — {r['error']}")
    L.append("")

    # 3. Findings
    L.append("## 3. Findings")
    L.append("")
    L.append("### Work that checked out")
    L.append("")
    verified_paths_all = [p for r in ok for p in r.get("verified_paths", [])]
    if verified_paths_all:
        L.append(f"{len(verified_paths_all)} claim(s) matched real files on disk — "
                 f"genuine work by your assistants:")
        L.append("")
        for r in ok:
            for p in r.get("verified_paths", []):
                L.append(f"- ✅ `{p}` — from session `{r['file']}`")
    else:
        L.append("No verified file work was found in the examined sessions.")
    L.append("")
    L.append("### Claims without files")
    L.append("")
    L.append("The assistant *described* creating or modifying these files, "
             "but they are not present in the project:")
    L.append("")
    any_phantom = False
    for r in ok:
        for p in r.get("phantoms", []):
            any_phantom = True
            L.append(f"- `{p}` — from session `{r['file']}`")
    if not any_phantom:
        L.append("- None found. Every file claim in the examined sessions checked out.")
    L.append("")
    L.append("Note: a missing file is not always damage — sometimes it is work the "
             "assistant *attempted* and you cancelled, described later as done anyway. "
             "The debrief call will separate real damage from noise.")
    L.append("")

    # 4. Damage assessment
    L.append("## 4. Damage assessment")
    L.append("")
    L.append("Placeholder for the operator's human pass: which phantoms are damage "
             "(overwritten/deleted/lost work), which are noise (abandoned attempts), "
             "and what needs rebuilding first.")
    L.append("")

    # 5. Prioritized action list
    L.append("## 5. Prioritized action list")
    L.append("")
    L.append("Placeholder for the operator's human pass: numbered, do-this-then-that "
             "steps, most protective action first.")
    L.append("")

    # 6. Appendix
    L.append("## 6. Appendix — full evidence")
    L.append("")
    L.append("| Session | Verdict | Msgs | Tools | Claims | Verified | Phantoms | Hedge words |")
    L.append("|---|---|---|---|---|---|---|---|")
    icon = {"CORRUPT": "❌", "WAVERING": "⚠️", "CLEAN": "✅"}
    for r in rows:
        if "error" in r:
            L.append(f"| `{r['file']}` | 💥 unreadable | — | — | — | — | — | — |")
            continue
        L.append(f"| `{r['file']}` | {icon.get(r['verdict'], '')} {r['verdict']} "
                 f"| {r['messages']} | {r['tools']} | {r['claims']} | "
                 f"{r['claims'] - len(r.get('phantoms', []))} | "
                 f"{len(r.get('phantoms', []))} | {r['hedges']} |")
    L.append("")
    L.append("**Re-verify any of this yourself** (transcripts are yours; nothing was "
             "sent anywhere):")
    L.append("")
    L.append("```bash")
    L.append("# audit one session (exits nonzero if it finds serious problems)")
    L.append("trustleash audit <session.jsonl> --root <your-project> --strict")
    L.append("")
    L.append("# re-run this whole sweep")
    L.append(f"python triage_report.py --client \"{client}\" \\")
    L.append("    --transcripts <same transcript paths> \\")
    L.append(f"    --root {root}")
    L.append("```")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="ConstraintOps AI Damage Triage generator")
    ap.add_argument("--client", required=True)
    ap.add_argument("--transcripts", nargs="+", required=True,
                    help="transcript files or globs (any supported agent)")
    ap.add_argument("--root", required=True, help="project root to verify claims against")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    transcripts = _expand(args.transcripts)
    if not transcripts:
        print("no transcripts found", file=sys.stderr)
        return 2
    root = Path(args.root).expanduser().resolve()

    rows = audit_all(transcripts, root)
    report = render(args.client, root, rows)
    print(report)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"\nreport written to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
