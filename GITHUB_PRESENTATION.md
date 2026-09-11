# GITHUB PRESENTATION KIT — for the public `trustleash` repo

Ready-to-paste values for repo settings + README banner. Used at ROADMAP 2.1.

## Repo name

`trustleash`

## Description (185-char limit)

```
Forensic audits for AI coding agents — catches agents that narrate work they never did. Checks every artifact claim against your filesystem. Exit 1 on CORRUPT.
```

## Topics

```
ai-safety, ai-agents, audit, code-review, developer-tools,
forensics, gemini-cli, claude-code, codex, llm-verification,
transcript-analysis, accountability, python, cli
```

## README banner block (prepends existing README.md)

```markdown
<div align="center">

# 🐕‍🦺 TrustLeash

**Your AI coding agent said it created 12 files. They don't exist.**

*Forensic audits for AI coding agents — Gemini CLI, Claude Code, OpenCode, Codex.*

`trustleash audit session.jsonl --strict` → **CLEAN / WAVERING / CORRUPT**

[Quick start](#usage) · [How it works](#what-it-checks) · [Validation](VALIDATION.md) · [The launch story](LAUNCH_POST.md)

**Validated against real forensically-audited sessions: caught the same
CORRUPT verdicts a human analyst found — in seconds, not hours.**

One real month of sessions on one machine: **200 phantom artifact claims.**
Your agent keeps the receipts. This tool checks them.

</div>

---
```

## Pinned-repo card image (optional, later)

Skip for launch — the banner block carries it. Revisit after first client.

## Commit message convention for the flip

```
Public release: TrustLeash v0.1 — forensic audits for AI coding agents

- Verdict engine (CLEAN/WAVERING/CORRUPT) validated against 3 manually
  audited sessions; tool-call counts match human analysis exactly on 2 of 3
- Adapters: Gemini CLI, Claude Code, OpenCode, Codex (auto-detection)
- Git pre-commit hook: blocks commits claiming files not in the diff
- 29 tests incl. adversarial edge cases (thought-block claim hiding,
  corrupt transcripts, phantom absolute paths)
```

## Pre-flip checklist (all must be ☑, from REPO_STRATEGY.md)

- [ ] No `/home/<user>/` paths anywhere in public files
- [ ] `leaderboard.md` excluded or fully redacted
- [ ] LICENSE file present (MIT per pyproject)
- [ ] All 29 tests green in CI-clean checkout
- [ ] Landing page CTA no longer placeholder (so README can link it)
