# Survival Stack Audit

**Status:** ACTIVE — merged with the existing flagship playbook
[`DIGITAL_RESILIENCE_PLAN.md`](DIGITAL_RESILIENCE_PLAN.md). Do not build a second
delivery process; they are the same service with two names for two audiences:

- "**Digital Resilience Plan**" → non-technical individuals (jargon-free, $500)
- "**Survival Stack Audit**" → low-resource / power users running free-tool
  stacks (Chromebook+Linux users, minimal-income operators, privacy-minded
  people). Same five pillars, different vocabulary and examples.

## What changes per audience

| | Resilience Plan (individual) | Survival Stack Audit (power user) |
|---|---|---|
| Tone | zero jargon, one-sentence instructions | plain but technical OK |
| Focus | backups, 2FA, scam surface | stack fragility, single points of failure, free-tier dependencies |
| Extra pillar | verification habit vs AI instructions | **dependency audit**: every free tier/API the client depends on, what breaks when it's revoked (token limits, account bans, tool removal) |

## The dependency audit (the power-user differentiator)

Inventory every external dependency in their workflow: cloud APIs, free tiers,
storage quotas, auth tokens, hardware limits (RAM/disk), tools installed from
unmaintained repos. For each: what happens the day it disappears? This is the
audit this project's own lived experience qualifies us for — token limits,
Powerwash, destructive commands, credit cliffs.

## Deliverable

Same as `DIGITAL_RESILIENCE_PLAN.md` plus the dependency table ranked by
blast radius, with a "what to do the day it dies" line per dependency.

## Pricing note

Power-user tier can be $500 flat like the individual tier — the extra
technical depth trades against shorter explanations. Do not create a third
price point until a client asks.
