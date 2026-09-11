# WHO_DID_WHAT.md — ConstraintOps

## 2026-09-11 (later) — Buffy (Freebuff agent, GLM via z-ai) — integration & sprint-prep pass

- **Restructure:** moved `TrustLeash/` inside `ConstraintOps/` — one repo, one
  unit. Fixed path refs in `triage_report.py`, `flywheel.py`, test paths.
  29/29 tests green; flywheel green post-move.
- **`sprawl_report.py`** — new Codebase Sprawl Triage generator (inventory,
  compile gate, hash-based duplicate detection, backup-lineage, stem
  collisions, entrypoints, evidence appendix). First real run caught a bug in
  its own compile gate (cfile=os.devnull → every file falsely "broken"); fixed
  and re-run: honest 14/14 clean on the repo. Self-sample at
  `portfolio/LIVE_SPRAWL_SELF.md`.
- **Filled all 4 Codex stubs** in `services/`: codebase-sprawl-triage (ACTIVE
  flagship #2), survival-stack-audit (merged into DIGITAL_RESILIENCE_PLAN —
  same service, two audiences), mess-to-map-report (ACTIVE $100 entry tier,
  + `services/mess-to-map-intake.md` same-day mini-form),
  research-to-opportunity-brief (deliberately DORMANT, activation triggers
  documented).
- **New docs:** ONE_PAGER.md (pasteable offer), WINTER_CASH_PLAN.md
  (week-by-week zero-budget path), EMAIL_TEMPLATES.md (4 moments),
  CLIENT_FORMS.md (pilot agreement + testimonial capture),
  FOLLOW_UP_SEQUENCE.md (2-touch max, stop rule),
  roadmaps/next-72-hours.md rewritten as token/hardware-constrained sprint.
- **Creed audit** (`CREED_AUDIT_2026-09-11.md`): scanned all client-facing
  docs. Found + fixed 3 private-thesis leaks (Basilisk/Jaynes/McGilchrist
  references in service playbooks). No uncited claims found; two placeholder
  CTAs logged as BLOCKING items before any public publish.
- **OUTREACH.md**: added 10 prospect archetypes with pains, venues, and
  lead services; pipeline board now archetype-keyed.
- **ROADMAP.md**: 0.x items ticked with evidence; Phase 1 marked CURRENT;
  winter override added (contact before craft).
- **TrustLeash git note:** repo now lives at `ConstraintOps/.git` (Codex
  initialized it inside ConstraintOps/; move made it the repo root).

## 2026-09-11 — Buffy (Freebuff agent, GLM via z-ai)

**Session context:** Operator's 30-day plan to turn the codebase into something that
makes money and helps people. Strategic pivot approved by operator: productize the
agent-verification stack instead of building yet another local AI assistant.

### Built (all in ~/TrustLeash unless noted)

- **TrustLeash v0.1** — forensic audit tool for AI coding agents. Parses session
  transcripts, computes msg/tool ratio, extracts artifact claims, verifies them
  against the filesystem, sniffs prose register (hedge/authority/LARP), emits
  verdict CLEAN / WAVERING / CORRUPT. Exit code 1 on CORRUPT for CI gating.
  - `trustleash/analyzer.py` — core engine + verdict logic
  - `trustleash/verifier.py` — filesystem claim verification
  - `trustleash/gemini_adapter.py` — Gemini CLI transcript decoder, incl.
    thought-block scanning (found 92% of one agent's prose hidden in thoughts)
  - `trustleash/adapters.py` — Claude Code, OpenCode, Codex adapters + auto format
    detection; `audit_transcript()` universal entry point
  - `trustleash/report.py`, `trustleash/__main__.py` — markdown reports + CLI
    (`audit`, `install-hook` subcommands)
  - `hooks/trustleash-pre-commit` — git pre-commit hook blocking commits whose
    message claims files not in the diff. Functionally tested both directions.
    (Note: first version had an `exit 0` that swallowed the block verdict — caught
    by testing the lying case explicitly. The hook caught its own bug class.)
  - `scripts/sweep.py` — machine-wide sweep → `leaderboard.md`
  - Tests: 29 passing (`tests/`), incl. corrupt-session fixture and edge cases

### Validation

- Re-audited the 3 manually-audited Gemini sessions: verdicts matched manual
  Internal Affairs audit (d3a1d5f6 CORRUPT ✓, a418a156 WAVERING ✓, 5a12241c
  adjacent). Tool-call counts matched exactly on two; documented deltas in
  `TrustLeash/VALIDATION.md`.
- Machine-wide sweep: **30 sessions, 200 phantom artifact claims in one month**
  (gemini 27 sessions/5 corrupt; codex 3/0 corrupt). See `TrustLeash/leaderboard.md`.

### Built (in ~/ConstraintOps)

- `README.md` — doctrine (5 rules), stack map, public offer
- `POSITIONING.md` — the creed ("We reveal, we don't conceal..."), private thesis
  vs public offer, three traps, pricing ladder ($0/$250/$750/$1500)
- `INTAKE.md` — triage-call questionnaire + operator notes
- `TRIAGE_CALL_SCRIPT.md` — free-call script: opening, money moment (no-lose
  frame), 3 objection counters, 3 exits (incl. referral-out)
- `services/` — 4 playbooks: AI_DAMAGE_TRIAGE, AUTOMATION_RISK_REVIEW,
  PLATFORM_SURVIVAL_REPORT, DIGITAL_RESILIENCE_PLAN
- `site/index.html` — one-page landing site, public language only, with the
  "no third outcome" irrefutable frame
- `triage_report.py` — turnkey client-deliverable generator wrapping TrustLeash;
  verified end-to-end on real sessions (76-line report from 3 transcripts, 2
  agent formats auto-detected). Hardened after stress tests: unreadable/empty
  files now disclosed as such, never rendered CLEAN; verified files listed by name.
- `portfolio/SAMPLE_AI_DAMAGE_TRIAGE.md` — public portfolio piece from the real
  sweep, redacted
- `flywheel.py` — self-healing 4-stage chain: pytest → sweep → self-triage →
  state snapshot. Failures quarantined to `state/failures.json` with retry hint;
  chain continues degraded. Verified all stages green (5.2s).
- `WHO_DID_WHAT.md`, `runbook.txt`, `QRD.md`, `MRD.txt`, `ROADMAP.md` — this set

### Known limitations (honest ledger)

- Claim extraction is regex-based, decent not exhaustive; thresholds tunable
- 5a12241c verdict was WAVERING vs manual CORRUPT (documented threshold gap)
- Claude/OpenCode adapters tested on fixtures only (no live transcripts on disk yet)
- Landing page CTA is a mailto placeholder; booking flow not wired
- Nothing pushed to GitHub yet; no domain/DNS; no email inbox set up

### Operator decisions on record

- Operator declined credential rotation advice and git init at root (for now)
- Operator chose "trust layer" over "build another assistant" and over ContentEngine
  (parked as outline in `~/ContentEngine/OUTLINE.md`)
- Directive in force: automate/delegate to keep the human out of the loop
