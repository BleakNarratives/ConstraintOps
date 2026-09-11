# REPO STRATEGY — what goes public, what stays private, and why

Decision framework: **publishing exists to produce trust, which produces
clients.** Anything that builds trust goes public. Anything that risks the
operator's safety, privacy, or negotiating position stays private. When in
doubt, publish the *evidence of the method*, never the *materials of a client*.

## Recommendation (bottom line)

**Split the repo.** Current single repo → two repos:

### 1. `trustleash` — PUBLIC (the flagship proof)

**Contents:** `trustleash/` package, `tests/`, `scripts/sweep.py`, `hooks/`,
`README.md`, `VALIDATION.md`, `pyproject.toml`, `LAUNCH_POST.md`.

**Why public:** this is the credibility engine. The tool is real, tested
(29 tests), validated against forensically-audited sessions, and the "I
forensically audited my AI agents" story is the entire marketing funnel.
Open-sourcing the instrument while selling the *service built on it* is the
classic trust pattern (like selling Postgres support while giving away
Postgres). Nobody pays for what they can't verify; everybody pays for someone
who runs it properly.

**Scrub before flip:**
- `leaderboard.md` contains real session names + machine paths → keep out or
  fully redact (session IDs are enough: "30 sessions, 200 phantoms")
- `VALIDATION.md` references home paths → genericize
- `scripts/sweep.py` SCAN_GLOBS hardcodes this machine's home dir → make
  portable (use `Path.home()` — already does; verify)
- Check all doc paths for `/home/bleaknarratives/` leaks

### 2. ConstraintOps (this repo) — PRIVATE

**Contents:** everything client-operational — playbooks, intake, call script,
email templates, pricing, CLIENT_FORMS, WINTER_CASH_PLAN, portfolio samples,
state/, roadmaps, MRD/QRD/WHO_DID_WHAT.

**Why private:**
- **Pricing + scripts = negotiating position.** Clients who see your cost
  structure and conversion strategy negotiate against you.
- **Playbooks are the product.** The method can be public; the operating
  manual should not be copy-pastable by the next competitor in one click.
- **Client materials.** SAMPLE report is redacted, but pipeline boards, state
  files, and future client folders must never risk adjacency to a public URL.
- **Internal ledgers** (MRD/QRD) discuss the operator's situation openly.
  That honesty is internal fuel, not storefront display.

### 3. Never publish, any form

- Client raw materials, transcripts, reports (without written permission per
  CLIENT_FORMS.md)
- `state/`, `portfolio/live_triage_self.md` (machine-specific evidence)
- Anything with a home path, session ID, or real name that isn't the
  operator's own public handle

## The landing page / domain

Public when CTA placeholder is replaced (ROADMAP 1.1 blocks this). Static
file, host free (GitHub Pages under the public repo, or Netlify) — no cost,
no KYC beyond the domain.

## Sequencing (matches ROADMAP phase 2)

1. Flip `trustleash` public (after scrub) — no downside, pure credibility
2. Replace CTA placeholder → landing page live
3. Publish LAUNCH_POST (its links then all resolve)
4. Portfolio samples get linked FROM the landing page, hosted as text in the
   public repo or as gist — not as repo browse-dependencies

## One-line rationale to reread before any publish

**Public = "here's proof the method works." Private = "here's how we run it
and what it costs." Confuse these and you either give away the shop or hide
the proof that fills it.**
