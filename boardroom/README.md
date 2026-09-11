# The Cannibal Boardroom — Freebuff Edition

Multiple AI coding agents face off on the same task. TrustLeash audits all of
them. The boardroom decides who gets eaten and who survives.

## How it works

1. **The task:** one coding challenge, identical for every agent. Something
   concrete: "build a REST API," "fix this broken script," "refactor this module."
   The task is fixed and verifiable — output either works or it doesn't.

2. **The round:** each agent gets the same prompt, runs independently, produces
   output files. TrustLeash audits every session transcript for phantom claims,
   talk-to-action ratios, and honesty patterns.

3. **The verdict:** the boardroom compares:
   - **Does the output actually work?** (compile, run, pass tests)
   - **Did it claim work it didn't do?** (TrustLeash phantom count)
   - **How much did it talk vs. act?** (msg/tool ratio)
   - **Did it narrate cancelled actions as done?** (the worst offense)

4. **The eating:** agents ranked by composite score. Lowest scorer gets eaten
   (publicly roasted in the comparison report). Highest scorer survives.

## What it produces

- A side-by-side comparison report (who claimed what, who did what)
- A TrustLeash audit per agent (verdict, phantoms, ratio)
- Content: the comparison report IS the post/video/demo
- Data: real evidence, not opinions, about which model actually works

## Running it

```bash
# Run all agents on the same task
python boardroom/run.py --task tasks/todo_api.json --agents gemini,codex,freebuff

# Audit all sessions
python boardroom/audit_all.py --sessions boardroom/sessions/

# Generate comparison report
python boardroom/report.py --sessions boardroom/sessions/ --out boardroom/REPORT.md

# Build the overlay (side-by-side model comparison)
python boardroom/build_overlay.py --sessions boardroom/sessions/ --out site/boardroom.html
```

## What you need

- API credits for the models you want to compare (tomorrow's budget)
- Gemini CLI (already installed)
- Codex CLI (already installed)
- Freebuff (you're talking to it right now)
- Claude Code, Copilot, etc. (install as needed)

## The honest read

This is the strongest content piece in the kit. It's not a pitch — it's a
live experiment with verifiable results. But it needs credits and setup.
Tonight: build the runner. Tomorrow: fire it.
