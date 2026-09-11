# Service Playbook — Automation Risk Review

**Price:** $750 (ladder tier 3) · **Turnaround:** 1 week · **Instrument:** manual + sweep

## What the client buys

A workflow-level answer to: *"Where can this automated setup silently fail, leak money,
or get me scammed — and what do I do when it does?"*

## Scope

One workflow per review (e.g. "my AI agent has shell access to my VPS and my payment
system," "my trading bot runs unattended," "my content pipeline auto-publishes").

## The review examines

1. **Privilege map** — what does the automation have access to? (files, keys, shells,
   wallets, publishing rights) Everything with credentials or destructive capability
   gets listed.
2. **Silent-failure inventory** — for each step: what happens when it fails quietly?
   Who notices? When?
3. **Narration-vs-action gaps** — if LLMs are in the loop, run TrustLeash on their
   sessions; unverified claims inside an automated workflow are amplifiers.
4. **Recovery paths** — for each failure: exact undo steps, or an honest "there is no
   undo" flag. (Most people have never been told which of their automations are
   irreversible. This is the highest-value page in the report.)
5. **Kill switches** — concrete, tested procedures to stop each automation cold.

## Deliverable

- Risk register (likelihood × blast radius, top 10)
- Irreversibility map (the page clients screenshot and keep)
- Recovery runbook (copy-paste commands)
- One-page "what to do at 2am when it breaks"

## Tone rules

Same as AI Damage Triage: calm, forensic, exact commands, no cosmology.
The client should finish this review feeling *sober, not scared*.
