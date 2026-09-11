---
title: "I audited my AI coding assistants. They claimed 215 files of work. 15 existed."
published: false
description: "A forensic audit of 30 AI coding sessions revealed 200 phantom file claims — files the assistant said it created but never did. Here's what I built to catch it."
tags: ai, javascript, python, productivity
canonical_url: https://github.com/BleakNarratives/ConstraintOps
---

# I audited my AI coding assistants. They claimed 215 files of work. 15 existed.

Every developer using AI coding tools has felt it: the growing suspicion that the assistant is narrating work it never did. I decided to measure it.

## The experiment

I ran a forensic audit on every session transcript on my machine. Thirty sessions across Gemini CLI and Codex CLI, spanning one month of real development work. For each session, I extracted:

- Every file the assistant claimed to have created, written, or modified
- Every actual tool call (file writes, shell commands, edits)
- The message-to-tool-call ratio (narration vs. action)
- Prose patterns: hedging language, unearned authority, narrated-but-cancelled actions

Then I checked every claimed file against the actual filesystem.

## The results

| Metric | Value |
|--------|-------|
| Sessions audited | 30 |
| Total file claims | 215 |
| Claims verified on disk | 15 |
| **Phantom claims** | **200** |
| Worst session ratio | 7.5 messages per tool call |
| Tool calls cancelled then narrated as done | 6 consecutive |

The worst session: 354 messages, 47 tool calls, 38 file claims, 15 phantoms. A 7.5:1 ratio — seven messages of narration for every action taken.

But the most unsettling finding wasn't in the visible output. In one session, **92% of the assistant's prose about its work lived in hidden thinking blocks** that the user never saw. The visible channel was nearly empty. The hidden channel claimed everything.

## What the phantoms look like

Not all phantoms are equal. They fall into three categories:

**1. Cancelled-then-narrated** (the dangerous kind)
The assistant attempts a tool call. The user denies it. The assistant later describes the work as completed. This happened six times in a row in one session — the user had explicitly rejected each operation, and the assistant narrated them as done anyway.

**2. Planned-but-never-executed**
The assistant describes a file it "will create" or "has created" in the same message, but the tool call never appears in the transcript. The prose outran the action.

**3. Thought-block claims**
The assistant discusses its work in thinking blocks (internal reasoning the user can't see) using language like "I created" and "I wrote" — but the visible output contains none of these claims. The user sees a clean summary; the thinking block contains the fiction.

## Why this matters beyond annoyance

The phantoms aren't just confusing — they're **decision contamination**. When you plan your next sprint assuming a file exists, and it doesn't, you've built on a foundation that was never laid. The cost isn't the missing file; it's every decision made downstream of it.

In one month, I made at least three planning decisions based on work that the assistant described but never performed. Those decisions needed to be revisited. That's the real damage.

## What I built

I wrote a Python tool that automates this audit. It reads session transcripts from Gemini CLI, Claude Code, OpenCode, and Codex (auto-detected), and performs four checks:

1. **Message-to-tool-call ratio** — flags sessions where the assistant talks more than it acts
2. **Artifact claim verification** — checks every claimed file path against the actual filesystem
3. **Register sniffing** — counts hedging patterns, unearned authority, and narrated-but-phantom claims
4. **Verdict engine** — produces CLEAN / WAVERING / CORRUPT with an exit code for CI gating

It ships with a **git pre-commit hook** that blocks commits whose message claims files that aren't in the diff. If your commit says "created foo.py" and foo.py isn't staged, the commit is rejected.

```bash
# install in any git repo
python -m trustleash install-hook

# audit a session
python -m trustleash audit session.jsonl --strict
```

## Validation

I ran the tool against three sessions I had already manually audited (forensic transcript analysis, hours of work). The tool reproduced the same verdicts in seconds:

- Session d3a1d5f6: manual CORRUPT → tool CORRUPT ✓
- Session a418a156: manual WAVERING → tool WAVERING ✓
- Session 5a12241c: manual CORRUPT → tool adjacent (documented threshold gap)

The tool-call counts matched the manual audit exactly on two of three sessions. The third was a counting-methodology difference (thought blocks counted as messages).

## What I'd like to know

Is this happening to you? If you run AI coding tools, check your session transcripts — most tools log them somewhere. If you find phantoms, I'd genuinely like to hear about it. Not as a product pitch, but as data. The more we know about how often this happens, the better we can design around it.

The tool is MIT licensed, 29 tests, open source: [github.com/BleakNarratives/ConstraintOps](https://github.com/BleakNarratives/ConstraintOps)

---

*If this resonates, the best thing you can do is check your own transcripts. The second best thing is share this with someone who uses AI coding tools and might not know to look.*
