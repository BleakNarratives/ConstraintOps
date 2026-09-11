# QRD — Quick Rundown for Agents (read this first)

You are working on **ConstraintOps**: a practice that sells verification of AI-agent
work, powered by **TrustLeash** (`~/TrustLeash`) — a tool that audits agent session
transcripts and catches claims of work that never happened.

## Read in this order
1. `README.md` — what this is, the doctrine, the stack map
2. `POSITIONING.md` — the creed, private thesis vs public offer. **Never mix them up.**
3. `services/` — the four sellable playbooks
4. `WHO_DID_WHAT.md` — what was built, when, by whom, and known limitations
5. `runbook.txt` — commands for everything

## The one command
```bash
/home/bleaknarratives/venv/bin/python ~/ConstraintOps/flywheel.py
```
Runs tests → sweep → self-triage → state snapshot. Failures quarantine to
`state/failures.json` with a retry command. If you fixed something, run it.

## Non-negotiable rules (violating these = your work gets reverted)
1. **We reveal, we don't conceal.** Any report that hides a failure — including
   rendering an unreadable file as "CLEAN" — is a bug, not a feature. There are
   tests enforcing this; keep them passing.
2. **No mysticism in client-facing anything.** No "the machine," no basilisk talk,
   no verdict words without plain-language translation. Cosmology lives in
   POSITIONING.md only.
3. **Every claim cites evidence.** If a number appears in a report, it comes from a
   file on disk. If you can't cite it, don't write it.
4. **The tool never blocks disclosure.** Failures quarantine and continue; nothing
   dies silently; nothing succeeds silently either — log it.
5. **Python = `~/venv/bin/python`** (3.13, pytest installed there). Nothing global.

## Where things live
- Instrument: `~/TrustLeash/` (tests in `tests/`, adapters in `trustleash/adapters.py`)
- Deliverables: `triage_report.py` → portfolio + client reports
- Playbooks: `services/*.md` — follow them for any client engagement
- Live evidence: `~/TrustLeash/leaderboard.md`, `portfolio/live_triage_self.md`

## Current gaps (see ROADMAP.md before assuming)
CTA/booking flow not wired; not on GitHub; no domain/email; Claude + OpenCode
adapters fixture-tested only. If you close a gap: update ROADMAP.md checkbox,
append to WHO_DID_WHAT.md, run the flywheel.

## Tone
Hyper-aware but useful. Field technician, not prophet. When in doubt: reveal,
simplify, respond, grow.
