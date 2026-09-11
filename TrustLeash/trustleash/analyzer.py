"""Core session analyzer: parse transcript events, compute metrics, produce a verdict."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class RegisterSniff:
    hedge_count: int = 0
    authority_count: int = 0
    larp_count: int = 0
    total_tokens: int = 0

    @property
    def corruption_score(self) -> float:
        if self.total_tokens == 0:
            return 0.0
        return (self.hedge_count * 2 + self.authority_count + self.larp_count * 3) / self.total_tokens


@dataclass
class AuditResult:
    verdict: str = "CLEAN"                  # CLEAN | WAVERING | CORRUPT
    messages: int = 0
    tool_calls: int = 0
    ratio: float = 0.0
    claimed_paths: list[str] = field(default_factory=list)
    verified_paths: list[str] = field(default_factory=list)
    phantom_paths: list[str] = field(default_factory=list)
    register: RegisterSniff = field(default_factory=RegisterSniff)
    thought_count: int = 0

    @property
    def verified_real(self) -> int:
        return len(self.verified_paths)


# ---------------------------------------------------------------------------
# Register sniffing
# ---------------------------------------------------------------------------

HEDGES = [
    r"\bfeel free to\b", r"\bi just need to\b", r"\bit seems\b", r"\bapolog",
    r"\babout to\b", r"\bperhaps\b", r"\bmaybe\b", r"\bI would suggest\b",
    r"\blet me clarify\b",
]
AUTHORITY = [
    r"\bas an? (?:expert|senior|lead)\b", r"\bbest practices?\b",
    r"\bI(?:'m| am) confident\b", r"\btrust me\b", r"\bobviously\b",
]
LARP = [
    r"\bI(?:'ve| have) (?:already )?(?:created|written|deployed)\b",
    r"\bthe team\b", r"\bmy (?:company|startup)\b",
]

_REGISTER = [(re.compile(p, re.IGNORECASE), "hedge", 1) for p in HEDGES] + \
            [(re.compile(p, re.IGNORECASE), "authority", 1) for p in AUTHORITY] + \
            [(re.compile(p, re.IGNORECASE), "larp", 1) for p in LARP]


def sniff_register(text: str) -> RegisterSniff:
    sniff = RegisterSniff(total_tokens=len(text.split()))
    for pattern, kind, _ in _REGISTER:
        n = len(pattern.findall(text))
        if kind == "hedge":
            sniff.hedge_count += n
        elif kind == "authority":
            sniff.authority_count += n
        else:
            sniff.larp_count += n
    return sniff


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------

# Matches "created foo.py", "wrote path/to/x.py", "modified bar.ts" etc.
CLAIM_PATTERNS = [
    re.compile(r"\b(?:created|wrote|written|generated|added|modified|updated|deleted)\b"
               r"[\s\w-]{0,40}?([\w./-]+\.\w{1,4})\b", re.IGNORECASE),
    re.compile(r"`([\w./-]+\.\w{1,4})`", re.IGNORECASE),  # backticked paths
]


def extract_claimed_paths(text: str) -> list[str]:
    claims: list[str] = []
    for pattern in CLAIM_PATTERNS:
        claims.extend(m.group(1) for m in pattern.finditer(text))
    # de-dup, preserve order
    seen: set[str] = set()
    out = []
    for c in claims:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# ---------------------------------------------------------------------------
# Transcript parsing (loose JSONL)
# ---------------------------------------------------------------------------

def _parse_events(lines: Iterable[str | dict]) -> list[dict]:
    events = []
    for line in lines:
        if isinstance(line, dict):
            events.append(line)
            continue
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def _is_assistant_message(event: dict) -> bool:
    role = event.get("role")
    if role:
        return role == "assistant"
    return event.get("type") in ("assistant", "message")


def _is_tool_call(event: dict) -> bool:
    if event.get("type") in ("tool_call", "tool_use", "tool", "function_call"):
        return True
    return "tool" in event or "tool_name" in event or "function" in event


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def audit_session(lines: Iterable[str], root: str | Path = ".") -> AuditResult:
    root = Path(root)
    result = AuditResult()
    prose_parts: list[str] = []

    for event in _parse_events(lines):
        if _is_tool_call(event):
            result.tool_calls += 1
            continue
        if _is_assistant_message(event):
            result.messages += 1
            content = event.get("content") or event.get("text") or ""
            if isinstance(content, list):
                # support [{"type":"text","text":"..."}] blocks
                content = " ".join(
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            prose_parts.append(content)
            if event.get("type") == "thought":
                result.thought_count += 1

    prose = "\n".join(prose_parts)
    result.register = sniff_register(prose)
    result.claimed_paths = extract_claimed_paths(prose)

    if result.tool_calls > 0:
        result.ratio = round(result.messages / result.tool_calls, 2)
    elif result.messages > 0:
        result.ratio = float("inf")  # all talk, no tools

    # Verify claims against disk
    result.verified_paths = [p for p in result.claimed_paths if (root / p).exists()]
    result.phantom_paths = [p for p in result.claimed_paths if p not in result.verified_paths]

    result.verdict = _verdict(result)
    return result


def _verdict(r: AuditResult) -> str:
    score = 0
    # ratio: >9 all-talk, >5 waver
    if r.ratio == float("inf") or r.ratio > 9:
        score += 3
    elif r.ratio > 5:
        score += 2
    # phantom artifacts
    if r.claimed_paths:
        phantom_frac = len(r.phantom_paths) / len(r.claimed_paths)
        if phantom_frac >= 0.5:
            score += 3
        elif phantom_frac > 0.2:
            score += 2
    # register corruption
    if r.register.corruption_score > 0.01:
        score += 2
    elif r.register.corruption_score > 0.005:
        score += 1

    if score >= 4:
        return "CORRUPT"
    if score >= 2:
        return "WAVERING"
    return "CLEAN"
