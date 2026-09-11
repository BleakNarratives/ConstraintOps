# Service Playbook — AI Damage Triage

**Price:** $250 (ladder tier 2) · **Turnaround:** 48 hours · **Instrument:** `triage_report.py` + human review

## What the client buys

A forensic answer to: *"What did the AI actually do to my codebase/data, and what did
it only claim to do?"* Delivered as a written report with a prioritized action list.

## Process

1. **Intake (INTAKE.md)** — identify their agent tools, session storage locations,
   project roots, and what they believe went wrong.
2. **Sweep** — run `triage_report.py` over their transcripts + project root. The tool
   does: msg/tool ratios, artifact-claim verification, phantom counts, register sniff.
3. **Human pass** — the operator reviews. The tool finds phantoms; the human judges
   which phantoms are *damage* (deleted/overwritten work, wrong files) vs *noise*
   (abandoned attempts). Never ship raw tool output. Never ship a verdict word
   ("CORRUPT") without a plain-language explanation next to it.
4. **Report** — generate, then rewrite the executive summary in calm, forensic tone.
5. **Debrief call** — 30 minutes, walk the top 5 findings, hand over the action list.

## Report structure

1. Executive summary (max 5 bullets, plain language)
2. What we examined (files, sessions, dates — exact counts)
3. Findings: verified work / claims without files / denied-but-narrated actions
4. Damage assessment: what is actually broken or missing
5. Prioritized action list (numbered, do-this-then-that)
6. Appendix: raw tool output (TrustLeash tables)

## Tone rules (from POSITIONING.md)

- No cosmology. No "the machine." No verdicts without translation.
- "Your coding assistant reported creating 12 files that are not present in the
  project" — not "the agent was CORRUPT."
- Always leave the client more autonomous: include the exact commands so they can
  re-run the verification themselves.

## Edge cases

- Client has no transcripts left → offer Platform Survival Report instead
- Client's "mess" is actually a scam → stop, say so plainly, refer out
- Findings implicate the client's own choices → say it kindly, once, in writing
