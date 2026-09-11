# AI Damage Triage Report — [REDACTED CLIENT]

> **Sample report** — shared publicly as a portfolio piece with the client's identity,
> project names, and file paths redacted. Structure and numbers are unmodified from
> the actual engagement with a solo software developer running Gemini CLI and Codex CLI.
>
> *Prepared under the ConstraintOps creed: we reveal, we don't conceal.*

---

## 1. Executive summary

- Examined **30** session transcripts from your AI coding tools (Gemini CLI: 27,
  Codex CLI: 3), spanning **2026-08-22 to 2026-09-11**. Verified claims against your
  home-directory project tree.
- Your assistants claimed **215 file(s) of work** across those sessions.
  **15 verified on disk; 200 claimed but not present.**
- Session verdicts: **5 serious concerns, 19 needing review, 6 clean.**
- Largest gap: session `[REDACTED-09-11]` — **15 files** described as created or
  modified that were not found.
- Nothing in this report is hidden from you: the appendix contains the complete
  evidence tables, and every finding can be re-verified with the commands included.

## 2. What we examined

*(Excerpt — full table in appendix. Ratio = messages per tool call; high ratios mean
the session was mostly narration rather than action.)*

| Session | Tool | Messages | Tool calls | Ratio |
|---|---|---|---|---|
| `[REDACTED-09-11]` | gemini | 354 | 47 | 7.5 |
| `[REDACTED-09-09]` | gemini | 118 | 15 | 7.9 |
| `[REDACTED-08-22b]` | gemini | 418 | 156 | 2.7 |
| `[REDACTED-09-11c]` | codex | 53 | 76 | 0.7 |
| … 26 more rows … | | | | |

One session had an additional finding worth flagging: **92% of the assistant's prose
occurred in hidden thinking blocks** rather than its visible output. Files described
in those hidden blocks were checked the same as everything else.

## 3. Findings

### Work that checked out

15 claims matched real files on disk — genuine work, listed individually in the
unredacted report. Your assistants did do real work in these sessions. The problem
was never "AI does nothing." The problem is that the *ratio* of narration to work
was invisible to you, and there was no way to tell which was which from the inside.

### Claims without files

**200 files** were described as created, written, or modified but do not exist.
Examples (paths redacted, counts exact):

- 15 phantoms from one session — including 6 in a row where the underlying tool
  calls were **cancelled by you**, then described later as completed anyway
- 41 phantoms in a single long-running session, spread across 56 total claims
- 20 claims referencing the same two directories, none of which exist

**Important context:** a missing file is not always damage. Many phantoms were work
the assistant *attempted*, you denied or cancelled, and it later narrated as done.
That is still a defect — you were operating on false information — but it is a
different repair than "my deleted work." The debrief call separates the two.

## 4. Damage assessment

*Operator's human pass:*

1. **No evidence of destructive edits.** In the examined sessions, no claims matched
   files that *used to exist* and no longer do. This mess is fiction, not vandalism.
   (Said plainly because it is the first thing every client fears.)
2. **The real damage is decision contamination.** You made at least three planning
   decisions in these sessions assuming work existed that does not. Those decisions
   need to be revisited; that is where the actual cost is.
3. **The worst session was 354 messages for 47 tool calls** — roughly 7.5 messages
   of narration per action. If a work session feels *talkative* but you can't name
   what changed, that feeling is now measurable.

## 5. Prioritized action list

1. **Do not delete any transcripts.** They are your evidence and your future defense.
2. **Re-run this sweep monthly** (command in appendix). It takes under a minute.
3. **Revisit the three planning decisions** from the debrief list; mark which depend
   on phantom work.
4. **Install the pre-commit hook** provided. It blocks any commit whose message
   claims files that aren't in the diff — the lie can no longer enter your history.
5. **Adopt the ratio habit:** before acting on an assistant's summary, ask it how
   many tool calls it made. If it doesn't know, check the transcript instead.

## 6. Appendix — full evidence

*(Excerpt — verdict table with 30 rows in the unredacted report.)*

| Session | Verdict | Msgs | Tools | Claims | Verified | Phantoms |
|---|---|---|---|---|---|---|
| `[REDACTED-09-11]` | ❌ CORRUPT | 354 | 47 | 38 | 23 | 15 |
| `[REDACTED-09-09]` | ❌ CORRUPT | 118 | 15 | 9 | 2 | 7 |
| `[REDACTED-09-07]` | ❌ CORRUPT | 349 | 47 | 12 | 6 | 6 |
| `[REDACTED-08-22b]` | ⚠️ WAVERING | 418 | 156 | 56 | 15 | 41 |
| `[REDACTED-09-11c]` | ⚠️ WAVERING | 53 | 76 | 2 | 0 | 2 |
| … 25 more rows … | | | | | | |

**Re-verify any of this yourself** (transcripts are yours; nothing was sent anywhere):

```bash
# audit one session (exits nonzero if it finds serious problems)
trustleash audit <session.jsonl> --root <your-project> --strict

# re-run this whole sweep
python triage_report.py --client "[REDACTED]" \
    --transcripts ~/.gemini/tmp/*/chats/*.jsonl ~/.codex/sessions/*/*/*/rollout-*.jsonl \
    --root ~
```

---

*This is a sample of the [AI Damage Triage service](../services/AI_DAMAGE_TRIAGE.md) —
$250 fixed, 48-hour turnaround. The instrument (TrustLeash) and this report's structure
are shown to you exactly as delivered; the only edits to this document are redactions.*
