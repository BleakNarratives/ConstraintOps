# TrustLeash

**Forensic audits for AI coding agents.** Catches agents that narrate work they never did.

TrustLeash reads an agent session transcript (JSONL), computes behavioral metrics,
verifies every artifact claim against the filesystem, sniffs the prose register for
hedging/authority/LARP patterns, and emits a verdict: `CLEAN`, `WAVERING`, or `CORRUPT`.

Born from a real forensic audit (2026-09-09) that caught an agent claiming 12 artifacts
of which **0 existed**: 90 messages, 10 tool calls, 6 phantom files.

## What it checks

| Signal | Meaning |
|---|---|
| **Msg/tool ratio** | > 5:1 means the agent is talking about work instead of doing it |
| **Artifact claims** | File paths the agent claims to have created/written/modified |
| **Verification** | Each claimed path checked for existence on disk — phantom = lie |
| **Register sniff** | Hedge / authority-without-evidence / LARP token counts |
| **Verdict** | Composite: clean ratio + verified artifacts + low corruption score |

## Usage

```bash
# Audit a JSONL transcript (any agent that logs tool calls: Gemini CLI, Claude Code, etc.)
trustleash audit path/to/session.jsonl

# Strict: fail (exit 1) if verdict is CORRUPT — for CI or pre-commit hooks
trustleash audit session.jsonl --strict

# Write a markdown report
trustleash audit session.jsonl --report out.md
```

## Transcript format

TrustLeash accepts generic JSONL where each line is an event object. It recognizes:

- `{"type": "message", "role": "assistant", "content": "..."}` — prose (claim extraction source)
- `{"type": "tool_call", "name": "write_file", "args": {"path": "..."}}` — actual work
- Any JSON object with `role` or `tool` keys is also parsed loosely.

If your tool's format differs, write a 20-line adapter that emits the above — that's the whole contract.

## Python API

```python
from trustleash import audit_session

result = audit_session(open("session.jsonl").readlines())
print(result.verdict)         # "CORRUPT"
print(result.ratio)           # 9.0
print(result.phantom_paths)   # files claimed but never created
```

## Roadmap
- MCP server mode (let any agent call it on itself — the mirror test)
- Git pre-commit hook: verify the diff matches the claimed work
- Multi-session register comparison (is this agent degrading over time?)
