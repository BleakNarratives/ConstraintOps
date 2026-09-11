"""CLI: python -m trustleash audit <session.jsonl> [--strict] [--report out.md]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import audit_session
from .report import render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trustleash", description="Forensic audits for AI coding agents")
    sub = parser.add_subparsers(dest="command", required=True)

    install_p = sub.add_parser("install-hook", help="Install the pre-commit hook into the current git repo")

    audit_p = sub.add_parser("audit", help="Audit a JSONL session transcript")
    audit_p.add_argument("transcript", help="Path to JSONL transcript")
    audit_p.add_argument("--root", default=".", help="Root dir to verify claimed paths against")
    audit_p.add_argument("--report", help="Write markdown report to this path")
    audit_p.add_argument("--strict", action="store_true", help="Exit 1 if verdict is CORRUPT")
    audit_p.add_argument("--format", choices=["auto", "gemini", "claude", "opencode", "codex", "generic"],
                         default="auto", help="Transcript format (default: auto-detect)")

    args = parser.parse_args(argv)

    if args.command == "install-hook":
        import shutil
        import stat
        hook_src = Path(__file__).resolve().parents[1] / "hooks" / "trustleash-pre-commit"
        if not hook_src.exists():
            print(f"error: hook template missing: {hook_src}", file=sys.stderr)
            return 2
        git_dir = Path(".git")
        if not git_dir.exists():
            print("error: not inside a git repository (no .git dir)", file=sys.stderr)
            return 2
        hooks = git_dir / "hooks"
        hooks.mkdir(exist_ok=True)
        dst = hooks / "pre-commit"
        shutil.copy(hook_src, dst)
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"installed pre-commit hook: {dst}")
        return 0

    transcript = Path(args.transcript)
    if not transcript.exists():
        print(f"error: transcript not found: {transcript}", file=sys.stderr)
        return 2

    lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    from .adapters import audit_transcript

    if args.format == "auto":
        result, fmt = audit_transcript(transcript, root=args.root)
    else:
        result, fmt = audit_transcript(transcript, root=args.root)
        fmt = args.format
    print(f"detected format: {fmt}", file=sys.stderr)

    print(render_markdown(result, title=f"TrustLeash Audit — {transcript.name}"))

    if args.report:
        Path(args.report).write_text(render_markdown(result), encoding="utf-8")
        print(f"report written to {args.report}")

    if args.strict and result.verdict == "CORRUPT":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
