# Creed Audit — 2026-09-11

Scope: all client-facing docs (site/, portfolio/, services/, samples/,
outreach/, ONE_PAGER, EMAIL_TEMPLATES, CLIENT_FORMS, FOLLOW_UP_SEQUENCE).
Method: pattern scan (private-thesis terms, unverifiable superlatives,
placeholder leaks) + manual read of flagged lines.

## Violations found & fixed

| # | File | Violation | Fix |
|---|---|---|---|
| 1 | services/PLATFORM_SURVIVAL_REPORT.md | "already-here Basilisk" — private cosmology in a playbook that shapes client-facing language | reworded to plain claim, no thesis terms |
| 2 | services/DIGITAL_RESILIENCE_PLAN.md | "anti-Jaynes pillar" — private thesis term | reworded to the actual mechanism (voice-command reflex) |
| 3 | services/DIGITAL_RESILIENCE_PLAN.md | "the McGilchrist market" | reworded to plain description of the audience |

## Findings that PASSED (worth noting)

- No unverifiable superlatives anywhere; the one "guarantee" hit is a
  *disclaimer* ("no guaranteed data recovery") — correct usage
- Numbers cited in client-facing docs (200 phantoms, 215 claims, 92% thought
  prose) all trace to TrustLeash/leaderboard.md, VALIDATION.md, and the live
  reports — no uncited claims found
- LANDING PAGE + ONE_PAGER carry the no-lose logic without any cosmology
- Raw evidence + re-verify commands present in both generators' outputs

## Known open items (not violations, tracked here)

1. **Placeholder CTA** — site/index.html still has `you@example.com`;
   ONE_PAGER has `[EMAIL / LINK]` placeholder. BLOCKED on operator creating
   the real inbox (MRD.txt item 1). Do not publish either until replaced.
2. **Sweep stats age** — portfolio pieces cite the 2026-09-11 sweep. Re-run
   the flywheel before any future publish so numbers match current reality.

## Standing rule

Re-run this audit before any public publish:
```bash
grep -rniE "basilisk|jaynes|mcgilchrist|bicameral|skynet" \
  site/ portfolio/ services/ ONE_PAGER.md samples/ outreach/
```
Expected output: zero lines (POSITIONING.md is the only sanctioned home for
the private thesis — it is never client-facing).
