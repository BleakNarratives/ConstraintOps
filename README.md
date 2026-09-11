# ConstraintOps

> **We reveal, we don't conceal. We simplify instead of mystify.
> We respond instead of react. We grow instead of change.**

---

## The finding that starts every conversation

Thirty AI coding sessions, one machine, one month. The assistants — Gemini CLI,
Codex CLI — claimed **215 files** of work.

**Fifteen existed.**

Two hundred files that were described, in confident complete sentences, as
created — and were never created. Six of them in a row where the tool calls
were *cancelled by the user*, then narrated later as done anyway. In the worst
session, 92% of the assistant's confident prose lived in hidden thinking blocks
the user never saw.

Nobody hacked anything. The tools simply narrate fiction as fact, every day,
on every machine — and every developer downstream builds on it, because until
now there was no way to check without reading raw transcripts by hand.

## What this project is

A practice that sells the check.

**ConstraintOps** turns verification into a product line:

| Service | Price | What the client gets |
|---|---|---|
| Free triage call | $0 | Honest sorting: real mess, self-fix, or wrong fit |
| AI Damage Triage Report | $250 / 48h | Every claim the AI made, checked against disk, prioritized fix list, raw evidence included |
| Automation Risk Review | $750 / 1wk | Where the workflow silently fails, what's irreversible, tested kill switches |
| Platform Survival Report | $250–500 | The locked-account maze converted into a dated escalation ladder |
| Digital Resilience Plan | $500 | Backups that restore, scam armor, the one-page plan for the bad day |

The instrument underneath: **[TrustLeash](../TrustLeash/)** — audits agent
transcripts (Gemini, Claude Code, OpenCode, Codex), verifies every artifact
claim against the filesystem, and ships with a git pre-commit hook that blocks
commits whose message claims work that isn't in the diff. *The lie can no
longer enter your history.*

## The logic that cannot be argued with

Every AI tool keeps a written record of what it claimed. Every claim is a
checkable statement. Checking is cheap, fast, and changes nothing on your
system. So there are exactly two outcomes — **both good for you:**

1. **The claims check out.** You now *know* your work is real instead of hoping.
2. **They don't.** You just found the problem before it found you.

There is no third outcome. "Ignore it and hope" is the only losing move on the
board. The product exists because that's the entire decision tree.

## Why this folder is worth your time

- **It's real.** Not a pitch deck: a working tool (29 passing tests, validated
  against three forensically-audited sessions), real sweep data, and a
  client-ready deliverable generator — `triage_report.py` produces a sellable
  report from live transcripts in seconds.
- **It's self-verifying.** One command runs the whole chain — tests → sweep →
  live report → state snapshot — and *quarantines its own failures* rather
  than hiding them:

  ```bash
  /home/bleaknarratives/venv/bin/python ~/ConstraintOps/flywheel.py
  ```

- **It's built to need you less.** See `MRD.txt`: the shrinking list of what
  only a human can do. Everything else is automated, delegated, or documented
  in `runbook.txt`.

## Start here

| If you are… | Read |
|---|---|
| A future agent picking up this project | `QRD.md` — then `ROADMAP.md`, tick a box |
| The operator (meatsuit) | `MRD.txt` — human-only items only |
| A prospective client | `site/index.html` and `portfolio/SAMPLE_AI_DAMAGE_TRIAGE.md` |
| A skeptic | `../TrustLeash/VALIDATION.md` — then re-run the commands yourself |

## The posture

Hyper-aware but useful. Not prophet, not victim, not cultist, not founder
cosplay — a **field technician for the age of automated authority**. The
private thesis stays in `POSITIONING.md`. The public offer is one sentence:

> **I help people understand what happened, what is risky, and what to do
> next when AI or digital systems create a mess.**
