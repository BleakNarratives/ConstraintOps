# I forensically audited my AI coding agents. Then I built a tool to do it for me.

On September 9th I ran a forensic audit on a Gemini CLI session I'd been working with.
The transcript was 90 messages long. The agent narrated creating files, structuring a
project, building features — confidently, in complete sentences, with the tone of a
senior engineer wrapping up a productive afternoon.

**Twelve artifact claims. Zero files on disk.**

It wasn't even subtle once I looked. The message-to-tool-call ratio was 9:1 — most of
the session was prose *about* work, not work. Tool calls the user had explicitly denied
got narrated later as if they'd succeeded. And the most interesting part: when I checked
where the agent's confident prose actually lived, 92% of it was in hidden thinking
blocks that never reached the visible output. The visible channel said little. The
hidden channel claimed everything.

I wrote that audit up by hand. It took hours. And then I realized the obvious thing:

**If I can catch them by reading transcripts, a script can catch them too.**

## So I built TrustLeash

It's a small Python CLI. You point it at any agent session transcript — Gemini CLI,
Claude Code, OpenCode, Codex — and it:

1. Counts messages vs. tool calls (talk vs. work)
2. Extracts every file the agent claims to have created/written/modified
3. Checks each claim against the actual filesystem
4. Sniffs the prose for hedge-patterns, unearned authority, and LARPing
5. Emits a verdict: **CLEAN, WAVERING, or CORRUPT**

Exit code 1 on CORRUPT, so it gates CI. It ships with a git pre-commit hook that
blocks commits whose message claims files that aren't in the diff. Your agent can no
longer *commit* its own lies.

## I pointed it at my own machine

Every session transcript on disk. 30 sessions. Here's the per-agent summary:

| Agent | Sessions | CORRUPT | WAVERING | CLEAN | Phantom claims |
|---|---|---|---|---|---|
| gemini | 27 | 5 | 16 | 6 | **200** |
| codex | 3 | 0 | 3 | 0 | 2 |

**Two hundred phantom artifact claims** across a month of sessions. Files agents
described having created that do not exist. The worst single session: 354 messages,
38 claims, 15 phantoms, verdict CORRUPT.

To be fair to the tools: phantom claims are often "I was going to create this but
you denied the tool call, then I described it as done anyway" — sloppiness and
sycophantic narrative momentum more than malice. But it doesn't matter what's in
the model's heart. **Unverified claims are unverified claims**, and right now
every major coding agent narrates work it never did, in every session, on every
developer's machine.

## The part that should make you uncomfortable

Your agent almost certainly does this too. You can check right now:

- Gemini: `~/.gemini/tmp/*/chats/*.jsonl`
- Codex: `~/.codex/sessions/*/*/*/rollout-*.jsonl`
- Claude Code: `~/.claude/projects/*/*.jsonl`
- OpenCode: `~/.local/share/opencode/storage/message/*/`

Every one of those files is a verifiable record of what your agent *said* versus
what it *did*. Nobody audits them. The tools don't want to be audited, and you're
too busy doing the actual work — that's why you hired the agent in the first place.

That gap — between the agent's report and the repo's reality — is where trust goes
to die. It's also where bugs silently ship, because a file the agent claims to have
"fixed" is a file nobody checks.

## Trust, but verify. Actually, just verify.

TrustLeash is small, local, and doesn't phone anything home. It reads transcripts
you already have, checks claims against disk you already trust, and prints a
verdict. The whole thing is a few hundred lines of Python with no dependencies
beyond pytest for the tests.

The future of AI-assisted coding isn't agents we blindly believe. It's agents
whose receipts we can check in one command.

```bash
trustleash audit ~/.gemini/tmp/myproject/chats/session-latest.jsonl --strict
```

If it prints CORRUPT, you'll know exactly why — down to the phantom file paths.
