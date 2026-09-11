# COMMENT TEMPLATES — when people ask questions on the post

Sorted by what they're actually asking. Pick the closest match, edit the
brackets, post once, walk away.

---

## "How does it work?"

> The tool reads the session transcript (Gemini, Claude, Codex — auto-detected)
> and does four checks:
> 1. Message-to-tool-call ratio (talk vs. work)
> 2. Every file claim vs. the actual filesystem
> 3. Prose register sniff (hedging, authority-without-evidence, LARP patterns)
> 4. Verdict: CLEAN / WAVERING / CORRUPT (exit code 1 for CI gating)
>
> The commit hook is separate — it reads your git commit message, finds any
> "created X.py" claims, and blocks the commit if X.py isn't in the diff.
> You can run the audit standalone or as a pre-commit gate.
>
> [link to TrustLeash README]

---

## "Can I try it?"

> Yeah — it's MIT licensed, just needs Python 3.10+ and pytest for tests.
>
> ```bash
> git clone https://github.com/BleakNarratives/ConstraintOps
> cd ConstraintOps/TrustLeash
> pip install pytest
> python -m pytest tests/ -q  # 29 tests
> python -m trustleash audit <your-session.jsonl> --strict
> ```
>
> The `--strict` flag makes it exit nonzero on CORRUPT, so you can chain it
> into CI or a pre-commit hook. The pre-commit hook installer is
> `python -m trustleash install-hook` inside any git repo.

---

## "What about [specific AI tool not supported]?"

> Right now it handles Gemini CLI, Claude Code, OpenCode, and Codex. The
> adapter layer is ~50 lines per tool — if you have a transcript format I
> don't support, open an issue with a sample (redacted) and I'll add it.
>
> The generic fallback also works on any JSONL where each line has a `role`
> and `content` field, which covers most agent logging.

---

## "This is just [existing tool]"

> It's not — [explain difference]. But if you know of something better,
> I'd genuinely like to see it. The problem is real regardless of who
> solves it.

---

## "I'm having this exact problem, can you help?"

> DM me at bleaknarratives@gmail.com with your transcript location and
> project root. I'll run the audit for free — takes minutes, and you get
> the raw evidence either way.

---

## "What's the business model?"

> The tool is free and open source. The paid service is the human layer:
> I run the audit, translate the verdicts into plain language, identify
> which phantoms are damage vs. noise, and give you a prioritized fix list.
> Fixed prices, stated upfront, raw evidence included with re-verify
> commands.

---

## Trolls / bad faith

Don't engage. If someone is clearly not asking in good faith, the best
response is silence. The post speaks for itself; the evidence is verifiable;
and every engagement with a troll is an engagement with a potential client
that didn't happen.

---

## Rules

- **One comment per question.** Don't thread-jack your own post.
- **Edit for their specific situation.** Generic copy-paste gets ignored.
- **Link to the repo, not to a sales page.** The code is the proof.
- **Walk away after posting.** Check back once in 24h for new questions.
  Don't hover.
