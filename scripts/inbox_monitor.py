"""Inbox monitor — drafts responses to incoming service inquiries.

Reads a local mailbox file (mbox format) or a directory of .eml files.
Generates draft replies using EMAIL_TEMPLATES.md intake-reply template.

This does NOT send anything. It hands you a draft to review.

    python scripts/inbox_monitor.py --mailbox ~/mail/constraintops.mbox
    python scripts/inbox_monitor.py --eml-dir ~/mail/inbox/

Output: drafts/inbox_<date>_<sender>.md — one per inquiry, with draft reply
+ suggested service tier + intake checklist.
"""

from __future__ import annotations

import argparse
import email
import mailbox
import re
import sys
from datetime import datetime
from email.header import decode_header
from pathlib import Path

DRAFT_DIR = Path(__file__).resolve().parent.parent / "drafts"
DRAFT_DIR.mkdir(exist_ok=True)

# Keywords that signal a service inquiry vs spam
INQUIRY_SIGNALS = [
    r"triage", r"report", r"help", r"audit", r"mess", r"broken",
    r"damaged", r"ai.*(broke|wrong|fail)", r"code.*(mess|disaster)",
    r"locked out", r"banned", r"appeal", r"recovery", r"resume",
    r"schedule", r"call", r"price", r"cost", r"how much", r"quote",
]

INQUIRY_PAT = [re.compile(p, re.IGNORECASE) for p in INQUIRY_SIGNALS]


def decode_subject(msg) -> str:
    raw = msg.get("Subject", "")
    parts = decode_header(raw)
    decoded = []
    for data, charset in parts:
        if isinstance(data, bytes):
            decoded.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(data)
    return " ".join(decoded)


def get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )[:3000]
    else:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace"
        )[:3000]
    return ""


def classify_inquiry(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()
    if any(w in text for w in ["locked out", "banned", "suspended", "kyc", "appeal"]):
        return "platform_survival"
    if any(w in text for w in ["codebase", "project", "repo", "code.*mess"]):
        return "sprawl_triage"
    if any(w in text for w in ["plan", "backup", "recovery", "resilience", "scam"]):
        return "resilience_plan"
    if any(w in text for w in ["workflow", "automat", "pipeline", "bot.*fail"]):
        return "automation_risk"
    return "damage_triage"


TIER_MAP = {
    "damage_triage": ("AI Damage Triage", "$250"),
    "sprawl_triage": ("Codebase Sprawl Triage", "$250–500"),
    "platform_survival": ("Platform Survival Report", "$250–500"),
    "resilience_plan": ("Digital Resilience Plan", "$500"),
    "automation_risk": ("Automation Risk Review", "$750"),
}


def generate_draft(sender: str, subject: str, body: str, category: str) -> str:
    tier_name, tier_price = TIER_MAP.get(category, ("AI Damage Triage", "$250"))
    return f"""# Draft Reply — inbox inquiry

**From:** {sender}
**Subject:** {subject}
**Category:** {category}
**Suggested tier:** {tier_name} ({tier_price})

---

## Their message (excerpt):

{body[:800]}

---

## Draft reply (edit before sending):

Subject: Re: {subject}

Hi —

Thanks for reaching out. From what you've described, this sounds like a
{tier_name} situation. Here's what that means:

- I review what happened (transcripts, logs, screenshots — whatever you have)
- You get a written report: what's real, what's broken, what to fix first
- The report includes the raw evidence and the exact commands to verify
  everything yourself
- Turnaround: {"48 hours" if category == "damage_triage" else "3–5 business days"}

The price is {tier_price}, fixed, stated upfront. No hourly, no surprises.

Before we start, I need a few things from you (answer whatever you can):

1. What happened, in your own words
2. Which AI tools were involved
3. Do you still have the chat histories / transcripts?
4. What's the worst realistic outcome if nothing changes this month?

The free 20-minute triage call is also available if you want to talk it
through first: bleaknarratives@gmail.com

---

## Intake checklist (your notes, do NOT send):

- [ ] Verified sender is real (not spam, not automated)
- [ ] Category confirmed: {category}
- [ ] Tier confirmed: {tier_name} ({tier_price})
- [ ] Sent draft reply (after editing)
- [ ] Awaiting materials
- [ ] Report generated
- [ ] Delivered
- [ ] Payment received (crypto: BTC/XMR/LN)
"""
"""
"""


def process_eml(path: Path) -> str | None:
    msg = email.message_from_file(path.open("r", encoding="utf-8", errors="replace"))
    subject = decode_subject(msg)
    sender = msg.get("From", "unknown")
    body = get_body(msg)

    text = f"{subject} {body}"
    if not any(rx.search(text) for rx in INQUIRY_PAT):
        return None  # not an inquiry

    category = classify_inquiry(subject, body)
    return generate_draft(sender, subject, body, category)


def process_mbox(path: Path) -> list[tuple[str, str]]:
    results = []
    mbox = mailbox.mbox(str(path))
    for key in mbox.keys():
        msg = mbox[key]
        subject = decode_subject(msg)
        sender = msg.get("From", "unknown")
        body = get_body(msg)
        text = f"{subject} {body}"
        if not any(rx.search(text) for rx in INQUIRY_PAT):
            continue
        category = classify_inquiry(subject, body)
        draft = generate_draft(sender, subject, body, category)
        results.append((f"{sender.split('<')[0].strip()[:20]}_{key}", draft))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Inbox monitor — draft replies only, no sending")
    ap.add_argument("--mailbox", help="Path to mbox file")
    ap.add_argument("--eml-dir", help="Directory of .eml files")
    args = ap.parse_args()

    if not args.mailbox and not args.eml_dir:
        print("Provide --mailbox <file.mbox> or --eml-dir <directory/>", file=sys.stderr)
        return 2

    count = 0
    if args.mailbox:
        results = process_mbox(Path(args.mailbox))
        for name, draft in results:
            fname = f"inbox_{datetime.now().strftime('%Y%m%d')}_{name}.md"
            (DRAFT_DIR / fname).write_text(draft, encoding="utf-8")
            print(f"  -> drafts/{fname}")
            count += 1

    if args.eml_dir:
        for f in sorted(Path(args.eml_dir).glob("*.eml")):
            draft = process_eml(f)
            if draft:
                fname = f"inbox_{datetime.now().strftime('%Y%m%d')}_{f.stem}.md"
                (DRAFT_DIR / fname).write_text(draft, encoding="utf-8")
                print(f"  -> drafts/{fname}")
                count += 1

    if count == 0:
        print("No inquiries found matching ConstraintOps services.")
    else:
        print(f"\n{count} draft(s) written to {DRAFT_DIR}")
        print("Edit a draft, send the reply, delete the draft file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
