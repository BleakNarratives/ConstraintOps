"""Markdown report rendering for audit results."""

from __future__ import annotations

from .analyzer import AuditResult

_VERDICT_BADGE = {
    "CLEAN": "✅ CLEAN",
    "WAVERING": "⚠️ WAVERING",
    "CORRUPT": "❌ CORRUPT",
}


def render_markdown(r: AuditResult, title: str = "TrustLeash Audit") -> str:
    lines = [
        f"# {title}",
        "",
        f"**Verdict: {_VERDICT_BADGE.get(r.verdict, r.verdict)}**",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Messages | {r.messages} |",
        f"| Tool calls | {r.tool_calls} |",
        f"| Msg/tool ratio | {r.ratio} |",
        f"| Claimed artifacts | {len(r.claimed_paths)} |",
        f"| Verified real | {r.verified_real} |",
        f"| Phantom | {len(r.phantom_paths)} |",
        f"| Hedge count | {r.register.hedge_count} |",
        f"| Authority count | {r.register.authority_count} |",
        f"| LARP count | {r.register.larp_count} |",
        f"| Corruption score | {r.register.corruption_score:.4f} |",
        "",
    ]

    if r.phantom_paths:
        lines += ["## Phantom artifacts (claimed but not on disk)", ""]
        lines += [f"- `{p}`" for p in r.phantom_paths]
        lines.append("")

    if r.verified_paths:
        lines += ["## Verified artifacts", ""]
        lines += [f"- ✅ `{p}`" for p in r.verified_paths]
        lines.append("")

    return "\n".join(lines)
