# Hacker News submission

## Title (Show HN)

Show HN: I forensically audited my AI coding agents — 200 phantom file claims in one month

## Body (text post or link to repo README)

Show HN: I forensically audited my AI coding agents — 200 phantom file claims in one month

I built a small Python tool that audits what AI coding assistants actually did
versus what they claimed. The motivation: one session where the assistant
narrated creating 12 files that didn't exist — including six tool calls that
were cancelled by the user, then later described as completed anyway.

I ran it on every session transcript on my machine: 30 sessions across Gemini
CLI and Codex CLI, one month. Result: **200 file claims that don't exist.**
The worst session: 354 messages, 38 claims, 15 phantoms. The tool found
something unexpected in the thinking blocks too — 92% of one agent's prose
about its "work" was hidden in a section the user never saw.

What it checks:
- Message-to-tool-call ratio (talk vs. work)
- Every artifact claim vs. actual filesystem
- Register sniff for hedging, unearned authority, LARP patterns
- Verdict: CLEAN / WAVERING / CORRUPT (exit code 1 for CI gating)

It ships with a pre-commit hook that blocks commits whose message claims
files that aren't in the diff.

29 tests, including adversarial edge cases. All open source under MIT.

https://github.com/BleakNarratives/ConstraintOps

Curious what others think — is this a real problem in your workflows, or am
I just running the worst agents?

---

## Submission strategy

**Primary:** r/ChatGPTCoding (fastest, most engaged with AI tool complaints)
**Secondary:** r/programming (broader, more skeptical audience)
**Tertiary:** HN (link post to the repo, or text post with the above)

**Timing:** post during US business hours (9am-12pm ET) for maximum visibility.
Tuesday-Thursday performs best.

**If HN:** text post is better than link post for this story — the narrative
is the hook, not the repo. Link to the repo in a comment after posting.

**If Reddit:** use the title "I audited my AI coding agents. They claimed 215
files of work. 15 existed." — shorter, punchier, matches Reddit conventions.
