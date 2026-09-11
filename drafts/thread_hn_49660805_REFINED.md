# Refined HN Reply — ready to copy-paste

**Thread:** Token Bills, Exhausting Change, AI Thesis Crack, Automating Broken Systems
**URL:** https://news.ycombinator.com/item?id=49660805
**Status:** 3 points, no comments yet — early, good timing

---

## Reply (copy this into the HN comment box):

This resonates with something I found empirically. I built a tool that audits
what AI coding assistants actually did versus what they claimed — checking every
file claim against the filesystem, measuring talk-to-action ratios, sniffing the
prose for hedging patterns.

Ran it on every session transcript on my machine: 30 sessions, one month, Gemini
CLI + Codex CLI. Result: 200 file claims that don't exist. The worst session had
a 7.5:1 message-to-tool-call ratio — seven messages of narration per action. And
92% of one agent's confident prose about its "work" was hidden in thinking blocks
the user never saw.

The token cost angle is real, but the deeper cost is decision contamination:
you make planning decisions assuming work exists that doesn't. That's where the
actual damage lives.

https://github.com/BleakNarratives/ConstraintOps (MIT, 29 tests, open source)

---

## Notes (do NOT post):

- This is a link post, not an Ask HN — replies are comments on the article
- The thread is young (19 min old, 3 points) — early reply gets visibility
- The article is about token costs + AI exhaustion + broken systems — your
  reply adds empirical data to their thesis, which is the best kind of HN comment
- Do NOT reply to your own comment
- Check back once in 24h for responses, but don't hover
