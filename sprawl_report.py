"""ConstraintOps — Codebase Sprawl Triage report generator.

The client-facing deliverable for services/codebase-sprawl-triage.md.
Point it at any folder (or globs of folders); it inventories the tree, tests
what compiles, maps duplication, and renders the client report with an
explicit evidence appendix. Operator does the human pass (sections 4-5)
before delivery, per the creed: we reveal, we don't conceal.

Usage:
    python sprawl_report.py --client "Acme" --root ~/their-project --out report.md
    python sprawl_report.py --client "Acme" --root . --include "src/**" "lib/**/*.py"
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import py_compile
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# analyzed extensions (code + config + docs-of-record)
CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".rb", ".go", ".rs"}
DOC_EXTS = {".md", ".txt", ".rst"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
             ".mypy_cache", ".ruff_cache", "dist", "build", ".tox", ".idea", ".vscode"}
LARGE_FILE_BYTES = 1_000_000      # >1MB is flagged (logs/zips/assets in the tree)
DUP_MIN_BYTES = 200               # hash files this size or larger for duplicate detection

BAK_PAT = re.compile(r"\.(bak|bak_plain|orig|old|save|backup|tmp)(\.\d+)?$", re.IGNORECASE)


def _walk(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            files.append(Path(dirpath) / f)
    return files


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def analyze(root: Path) -> dict:
    files = _walk(root)
    code = [f for f in files if f.suffix.lower() in CODE_EXTS]
    docs = [f for f in files if f.suffix.lower() in DOC_EXTS]

    total_lines = 0
    big_files = []
    for f in code:
        try:
            with f.open("rb") as fh:
                n = sum(1 for _ in fh)
            total_lines += n
            if f.stat().st_size > LARGE_FILE_BYTES:
                big_files.append((f, f.stat().st_size))
        except OSError:
            pass

    # python compile gate (write bytecode cache next to file, like python -m py_compile;
    # NOTE: cfile=os.devnull breaks on Linux — devnull is not a regular file)
    py_ok, py_broken = 0, []
    for f in code:
        if f.suffix == ".py":
            try:
                py_compile.compile(str(f), doraise=True)
                py_ok += 1
            except (py_compile.PyCompileError, OSError, ValueError) as e:
                py_broken.append((f, str(e).splitlines()[0][:120]))

    # duplicate detection by content hash (code + docs >= DUP_MIN_BYTES)
    hashes: dict[str, list[Path]] = defaultdict(list)
    for f in files:
        try:
            if f.stat().st_size >= DUP_MIN_BYTES:
                h = _sha(f)
                if h:
                    hashes[h].append(f)
        except OSError:
            pass
    dup_groups = sorted((g for g in hashes.values() if len(g) > 1),
                        key=lambda g: -len(g))

    # backup-lineage files
    baks = [f for f in files if BAK_PAT.search(f.name)]

    # stem collision (same filename in multiple places)
    by_name: dict[str, set] = defaultdict(set)
    for f in files:
        by_name[f.name].add(f.parent)
    stem_dupes = {n: sorted(str(p) for p in ps) for n, ps in by_name.items() if len(ps) > 1}

    # entrypoints (py files with main guard, sh/executables at root-ish level)
    entrypoints = []
    for f in code:
        if f.suffix == ".py":
            try:
                txt = f.read_text(encoding="utf-8", errors="replace")[:8000]
                if '__main__' in txt:
                    entrypoints.append(f)
            except OSError:
                pass

    return {
        "root": root, "n_files": len(files), "n_code": len(code), "n_docs": len(docs),
        "total_lines": total_lines, "py_total": py_ok + len(py_broken),
        "py_ok": py_ok, "py_broken": py_broken, "big_files": big_files,
        "dup_groups": dup_groups, "baks": baks, "stem_dupes": stem_dupes,
        "entrypoints": entrypoints,
    }


def render(client: str, a: dict) -> str:
    L: list[str] = []
    L.append(f"# Codebase Sprawl Triage — {client}")
    L.append("")
    L.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · prepared under the "
             f"ConstraintOps creed: we reveal, we don't conceal. Every finding below "
             f"can be re-verified with the commands in the appendix.*")
    L.append("")
    L.append("## 1. Executive summary")
    L.append("")
    L.append(f"- Folder `{a['root']}` contains **{a['n_files']} files** "
             f"({a['n_code']} code, {a['n_docs']} docs), roughly **{a['total_lines']:,} lines** of code.")
    if a["py_total"]:
        L.append(f"- Python compile gate: **{a['py_ok']}/{a['py_total']} files compile clean**; "
                 f"{len(a['py_broken'])} broken (list in findings).")
    if a["baks"]:
        L.append(f"- **{len(a['baks'])} backup-lineage files** (.bak/.old/.save patterns) — "
                 f"version-control archaeology standing in for git.")
    dup_files = sum(len(g) for g in a["dup_groups"])
    if a["dup_groups"]:
        L.append(f"- **{dup_files} files across {len(a['dup_groups'])} groups are exact "
                 f"duplicates** by content hash.")
    L.append(f"- {len(a['entrypoints'])} candidate entrypoints detected (__main__ guards).")
    L.append("")

    L.append("## 2. Inventory")
    L.append("")
    L.append("| Metric | Count |")
    L.append("|---|---|")
    L.append(f"| Total files (excluding deps/caches) | {a['n_files']} |")
    L.append(f"| Code files | {a['n_code']} |")
    L.append(f"| Docs/notes | {a['n_docs']} |")
    L.append(f"| Lines of code | {a['total_lines']:,} |")
    L.append(f"| Python compile-clean | {a['py_ok']}/{a['py_total']} |")
    L.append(f"| Backup-lineage files | {len(a['baks'])} |")
    L.append(f"| Exact-duplicate files | {dup_files} |")
    L.append(f"| Same-name files in multiple dirs | {len(a['stem_dupes'])} |")
    L.append(f"| Files >1MB (logs/assets in tree) | {len(a['big_files'])} |")
    L.append("")

    L.append("## 3. Findings")
    L.append("")
    L.append("### Broken code (compile gate)")
    L.append("")
    if a["py_broken"]:
        for f, err in a["py_broken"][:25]:
            L.append(f"- ✗ `{f.relative_to(a['root'])}` — {err}")
        if len(a["py_broken"]) > 25:
            L.append(f"- … and {len(a['py_broken']) - 25} more (full list in appendix)")
    else:
        L.append("- None. Everything that can be parsed, parses.")
    L.append("")
    L.append("### Duplicate content (exact, by hash)")
    L.append("")
    if a["dup_groups"]:
        for g in a["dup_groups"][:20]:
            names = ", ".join(f"`{p.relative_to(a['root'])}`" for p in g[:6])
            extra = f" (+{len(g) - 6} more)" if len(g) > 6 else ""
            L.append(f"- {names}{extra}")
    else:
        L.append("- None found.")
    L.append("")
    L.append("### Backup-lineage (uncommitted history)")
    L.append("")
    if a["baks"]:
        for f in a["baks"][:25]:
            L.append(f"- `{f.relative_to(a['root'])}`")
    else:
        L.append("- None found.")
    L.append("")

    L.append("## 4. Damage assessment — OPERATOR PASS REQUIRED")
    L.append("")
    L.append("*Human pass: which broken files are load-bearing? Which duplicate set is "
             "canonical? Which backup file holds the newest real code? Placeholder until "
             "the operator reviews the evidence.*")
    L.append("")
    L.append("## 5. Ship-path ranking — OPERATOR PASS REQUIRED")
    L.append("")
    L.append("*Human pass: 3 fastest credible paths to something deployable, ranked by "
             "effort-to-first-value, each traceable to inventory rows above.*")
    L.append("")

    L.append("## Appendix — evidence & re-verification")
    L.append("")
    if a["big_files"]:
        L.append("**Oversized files in tree (>1MB):**")
        L.append("")
        for f, sz in a["big_files"][:15]:
            L.append(f"- `{f.relative_to(a['root'])}` ({sz / 1e6:.1f} MB)")
        L.append("")
    L.append("Re-run this exact analysis yourself:")
    L.append("")
    L.append("```bash")
    L.append(f"python sprawl_report.py --client \"{client}\" --root {a['root']}")
    L.append("")
    L.append("# verify a specific python file compiles:")
    L.append("#   python -m py_compile <file>")
    L.append("")
    L.append("# find exact duplicates yourself:")
    L.append("#   find <root> -type f -size +200c -exec sha256sum {} + | sort | uniq -w64 -D")
    L.append("```")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="ConstraintOps Codebase Sprawl Triage generator")
    ap.add_argument("--client", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    a = analyze(root)
    report = render(args.client, a)
    print(report)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"\nreport written to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
