"""Thread monitor — pulls matching threads from Reddit/HN public feeds,
generates draft replies for human editing + posting. Zero auth required.

    python scripts/thread_monitor.py                  # scan all sources
    python scripts/thread_monitor.py --source reddit   # reddit only
    python scripts/thread_monitor.py --source hn        # HN only
    python scripts/thread_monitor.py --days 3          # last 3 days only

Output: drafts/thread_<id>.md — one per matching thread, with context +
draft reply ready for human edit + post.

This does NOT post anything. It reads public feeds and hands you drafts.
The last 10% (judgment + posting) is yours by design — platforms defend it
because it's the valuable part.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DRAFT_DIR = Path(__file__).resolve().parent.parent / "drafts"
DRAFT_DIR.mkdir(exist_ok=True)

# Keywords that signal someone needs what ConstraintOps sells
KEYWORDS = [
    # AI damage
    r"\bai\b.*\b(broke|crash|destroy|delet|ruin|hallucin|lie|lied|wrong|damage|fail|bug|corrupt)",
    r"\b(coding assistant|code assistant|copilot|cursor|claude|gemini|chatgpt|codex)\b.*\b(broke|wrong|bad|broken|terrible|ruined|mess|destroyed)",
    r"\b(broke|crashed|destroyed|delet|ruin)\b.*\b(code|project|repo|file|database|server|deploy)",
    r"\b(ai|assistant|agent|bot|copilot)\b.*\b(created|claimed|said|built|wrote|fixed)\b.*\b(not there|doesn't exist|missing|phantom|fake|wrong)",
    # Platform / automation pain
    r"\b(locked out|banned|suspended|demonetized|kyc|appeal|support.*maze|chatbot.*loop)",
    r"\b(automat|script|workflow|pipeline|bot)\b.*\b(broke|fail|silent|dangerous|scary|lost|gone)",
    # Codebase mess
    r"\b(codebase|project|repo)\b.*\b(mess|disaster|chaos|sprawl|spaghetti|unmaintainable|orphan)",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in KEYWORDS]

# Reply templates — each is a starting point, NOT a finished reply
REPLY_TEMPLATES = {
    "ai_damage": (
        "Hey — I built a tool that does exactly this. It audits what AI coding "
        "assistants actually did versus what they claimed. Ran it on my own "
        "machine: 30 sessions, 200 phantom file claims. The check takes minutes "
        "and you keep all the evidence.\n\n"
        "If you want, I can walk you through it for free: bleaknarratives@gmail.com"
    ),
    "platform_maze": (
        "I've been through this exact thing. The key insight: these systems "
        "respond to procedure, not grievance. I turned my own disaster into a "
        "step-by-step escalation plan that actually worked.\n\n"
        "Happy to share the template if it helps: bleaknarratives@gmail.com"
    ),
    "codebase_mess": (
        "I've been on the other side of this — recovered a 400-file codebase "
        "where half the entries were AI-generated orphans. Built a triage tool "
        "that sorts real/broken/duplicate in minutes.\n\n"
        "Free to try if you want a second pair of eyes: bleaknarratives@gmail.com"
    ),
}


def classify_match(text: str) -> str:
    """Classify which service category a thread matches."""
    t = text.lower()
    if any(w in t for w in ["locked out", "banned", "suspended", "kyc", "appeal", "support"]):
        return "platform_mess"
    if any(w in t for w in ["codebase", "project", "repo", "spaghetti", "orphan"]):
        return "codebase_mess"
    return "ai_damage"


# ---------------------------------------------------------------------------
# Reddit (public .json feeds, no auth)
# ---------------------------------------------------------------------------

def fetch_reddit(subreddits: list[str], days: int = 7) -> list[dict]:
    """Fetch recent posts from subreddits via public .json API."""
    posts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=25"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ConstraintOps/1.0 (github.com/BleakNarratives/ConstraintOps)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            for child in data.get("data", {}).get("children", []):
                p = child.get("data", {})
                created = datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc)
                if created < cutoff:
                    continue
                body = f"{p.get('title', '')} {p.get('selftext', '')}"
                if not any(rx.search(body) for rx in COMPILED):
                    continue
                posts.append({
                    "source": "reddit",
                    "subreddit": sub,
                    "id": p.get("id", ""),
                    "title": p.get("title", ""),
                    "url": f"https://reddit.com{p.get('permalink', '')}",
                    "score": p.get("score", 0),
                    "created": created.isoformat(),
                    "body": p.get("selftext", "")[:1000],
                    "category": classify_match(body),
                })
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            print(f"  [warn] reddit r/{sub}: {e}", file=sys.stderr)
        time.sleep(2)  # be polite to public API
    return posts


# ---------------------------------------------------------------------------
# HN (official API, no auth)
# ---------------------------------------------------------------------------

def fetch_hn(days: int = 7) -> list[dict]:
    """Fetch recent HN stories matching keywords."""
    posts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/newstories.json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            story_ids = json.loads(resp.read())[:100]  # top 100 new
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"  [warn] HN story list: {e}", file=sys.stderr)
        return posts

    for sid in story_ids[:80]:
        try:
            req = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
            with urllib.request.urlopen(req, timeout=10) as resp:
                story = json.loads(resp.read())
        except (urllib.error.URLError, json.JSONDecodeError, OSError):
            continue
        if not story:
            continue
        created = datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc)
        if created < cutoff:
            continue
        body = f"{story.get('title', '')} {story.get('text', '') or ''}"
        if not any(rx.search(body) for rx in COMPILED):
            continue
        posts.append({
            "source": "hn",
            "id": str(sid),
            "title": story.get("title", ""),
            "url": f"https://news.ycombinator.com/item?id={sid}",
            "score": story.get("score", 0),
            "created": created.isoformat(),
            "body": (story.get("text") or "")[:1000],
            "category": classify_match(body),
        })
        time.sleep(0.5)
    return posts


# ---------------------------------------------------------------------------
# Draft generation
# ---------------------------------------------------------------------------

def generate_draft(post: dict) -> str:
    """Generate a draft reply for a matching thread."""
    cat = post["category"]
    template = REPLY_TEMPLATES.get(cat, REPLY_TEMPLATES["ai_damage"])

    # Pull a specific detail from the post body for personalization
    detail = ""
    sentences = post["body"].split(".")
    for s in sentences:
        if any(rx.search(s) for rx in COMPILED):
            detail = s.strip()[:200]
            break

    draft = f"""# Draft Reply — {post['source']}

**Thread:** {post['title']}
**URL:** {post['url']}
**Score:** {post.get('score', '?')} | **Posted:** {post.get('created', '?')}
**Category:** {cat}
**Matched detail:** {detail}

---

## Template reply (edit before posting):

{template}

---

## Notes for you (do NOT post this part):

- Read the full thread before posting — check if someone already gave good
  advice. Don't duplicate. Don't pitch if the thread is resolved.
- If the person is clearly in crisis (legal, financial, safety), link them to
  appropriate resources instead of pitching the service.
- Edit the template to reference their SPECIFIC situation — generic replies
  get ignored.
- Post once, then walk away. Do not thread-jack. Do not reply to your own reply.
- The email address is the funnel. Everything else is just being helpful.
"""
    return draft


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Thread monitor — drafts only, no posting")
    ap.add_argument("--source", choices=["reddit", "hn", "all"], default="all")
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    SUBREDDITS = [
        "ChatGPTCoding", "artificial", "LocalLLaMA", "selfhosted",
        "programming", "Cursor", "claudeai", "machinelearning",
        "Crostini", "chromeos", "linux",
    ]

    posts = []
    if args.source in ("reddit", "all"):
        print(f"Scanning Reddit ({len(SUBREDDITS)} subs, last {args.days} days)...")
        posts.extend(fetch_reddit(SUBREDDITS, args.days))
    if args.source in ("hn", "all"):
        print(f"Scanning Hacker News (last {args.days} days)...")
        posts.extend(fetch_hn(args.days))

    posts.sort(key=lambda p: -p.get("score", 0))

    if not posts:
        print("No matching threads found.")
        return 0

    print(f"\n{len(posts)} matching thread(s) found:\n")
    for post in posts:
        # Write draft file
        draft = generate_draft(post)
        fname = f"thread_{post['source']}_{post['id']}.md"
        (DRAFT_DIR / fname).write_text(draft, encoding="utf-8")

        # Print summary
        print(f"  [{post['source']:6}] score={post.get('score', '?'):>4}  "
              f"{post['title'][:70]}")
        print(f"          {post['url']}")
        print(f"          -> drafts/{fname}")
        print()

    print(f"Drafts written to: {DRAFT_DIR}")
    print("Edit a draft, post the reply, delete the draft file. That's the loop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
