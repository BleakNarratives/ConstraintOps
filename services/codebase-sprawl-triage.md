# Codebase Sprawl Triage

**Status:** ACTIVE — flagship #2. Highest earning potential of the stubs.
**Price:** $250 (solo project) · $500 (multi-directory/multi-agent mess)
**Turnaround:** 48–72h
**Instruments (already exist on this machine):** TrustLeash sweep,
`triage_report.py`, `~/codemap.py`, `ruff`, `py_compile` gate,
`CODEBASE_REPORT_*.md` tooling at repo root.

## Offer (one sentence)

> "I review your messy codebase or recovered project folder and tell you what's
> real, what's broken, what's duplicate, and what can ship first."

## Why it sells

Every AI-assisted developer now owns a folder like this one was: 400+ Python
files, orphan entrypoints, `.bak` archaeology, agents that claimed work that
isn't there. They don't need a developer — they need a forensic map and a
shippable sequence. The evidence tooling is already built; this service is the
human pass wrapped around it.

## Process

1. **Inventory** — file count, line count, languages, entrypoints, dead code,
   duplicates (`codemap.py` + `ruff` + git-truth where available)
2. **Verification pass** — TrustLeash sweep of their agent transcripts if they
   have them: which claimed work actually exists
3. **Runnable-surface test** — `py_compile` gate across the tree; what executes,
   what's broken, what's a stub
4. **Duplication map** — same-named stems, divergent copies, `.bak` lineage
5. **Ship-path ranking** — the 20% of files that could produce money first

## Deliverable

1. Executive summary (max 5 bullets)
2. Inventory table (real / broken / duplicate / orphan / stub)
3. Verification findings (claimed-vs-on-disk, if transcripts provided)
4. Ranked ship-path: 3 fastest credible paths to something deployable
5. Prioritized action list + exact commands
6. Appendix: raw tool output

## Process rules (creed-enforced)

- Raw evidence always included; client gets the commands to re-verify
- No verdict word without plain-language translation
- Client leaves more autonomous than we found them

## Marketing angle (from lived evidence)

> "I ran a sprawl triage on my own recovered codebase: 400 Python files,
> 163k lines, 59 orphan entrypoints, 45 stubs, 1 broken core file. The map
> cost me nothing but the tooling I now run for clients."
