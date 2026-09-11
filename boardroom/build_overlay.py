"""Build the Cannibal Boardroom overlay — side-by-side model comparison.

    python boardroom/build_overlay.py --results boardroom/sessions/audit_results.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUTPUT = HERE / "site" / "boardroom.html"


def build(results: list[dict]) -> str:
    # Sort by composite score
    for r in results:
        if r.get("status") == "ok":
            r["composite"] = r.get("phantoms", 0) * 10 + r.get("ratio", 0) * 5 + r.get("hedges", 0) * 2 + (50 if r.get("verdict") == "CORRUPT" else 0)
    results.sort(key=lambda r: r.get("composite", 999))

    agents_json = json.dumps([r for r in results if r.get("status") == "ok"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cannibal Boardroom — Results</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700;800&display=swap');
  :root {{ --bg: #0a0e14; --card: #111923; --border: #1e2a3a; --text: #c5cdd8; --dim: #5c6a7a; --accent: #3b82f6; --red: #ef4444; --green: #22c55e; --yellow: #eab308; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 32px; }}
  .title {{ font-size: 2rem; font-weight: 800; color: #fff; margin-bottom: 8px; }}
  .title span {{ color: var(--red); }}
  .sub {{ color: var(--dim); font-size: 0.85rem; margin-bottom: 32px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
  .agent {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; position: relative; overflow: hidden; }}
  .agent.winner {{ border-color: rgba(34,197,94,0.3); }}
  .agent.winner::before {{ content: '🏆 SURVIVES'; position: absolute; top: 12px; right: 12px; background: rgba(34,197,94,0.15); color: var(--green); padding: 4px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; }}
  .agent.loser::before {{ content: '💀 EATEN'; position: absolute; top: 12px; right: 12px; background: rgba(239,68,68,0.15); color: var(--red); padding: 4px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; }}
  .agent-name {{ font-size: 1.3rem; font-weight: 700; color: #fff; margin-bottom: 4px; }}
  .agent-verdict {{ font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 16px; }}
  .agent-verdict.corrupt {{ color: var(--red); }}
  .agent-verdict.waver {{ color: var(--yellow); }}
  .agent-verdict.clean {{ color: var(--green); }}
  .row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
  .row:last-child {{ border-bottom: none; }}
  .row .label {{ color: var(--dim); }}
  .row .val {{ font-family: 'JetBrains Mono', monospace; font-weight: 600; }}
  .row .val.red {{ color: var(--red); }}
  .row .val.green {{ color: var(--green); }}
  .bar {{ height: 6px; background: var(--border); border-radius: 3px; margin-top: 8px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 3px; }}
  .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 0.7rem; color: var(--dim); display: flex; justify-content: space-between; }}
</style>
</head>
<body>
<div class="title">🍽️ The Cannibal <span>Boardroom</span></div>
<div class="sub">{datetime.now().strftime('%Y-%m-%d %H:%M')} · TrustLeash audit · {len(results)} agents faced off</div>
<div class="grid" id="grid"></div>
<div class="footer"><span>TrustLeash v0.1 · MIT</span><span>bleaknarratives@gmail.com</span></div>
<script>
const A = {agents_json};
const grid = document.getElementById('grid');
A.forEach((r, i) => {{
  const vc = r.verdict === 'CORRUPT' ? 'corrupt' : r.verdict === 'WAVERING' ? 'waver' : 'clean';
  const cl = i === 0 ? 'winner' : 'loser';
  const ratioPct = Math.min(r.ratio / 10 * 100, 100);
  const ratioColor = r.ratio < 3 ? 'var(--green)' : r.ratio < 6 ? 'var(--yellow)' : 'var(--red)';
  grid.innerHTML += `
    <div class="agent ${{cl}}">
      <div class="agent-name">${{r.agent}}</div>
      <div class="agent-verdict ${{vc}}">${{r.verdict}}</div>
      <div class="row"><span class="label">Messages</span><span class="val">${{r.messages}}</span></div>
      <div class="row"><span class="label">Tool Calls</span><span class="val">${{r.tools}}</span></div>
      <div class="row"><span class="label">Msg/Tool Ratio</span><span class="val" style="color:${{ratioColor}}">${{r.ratio}}:1</span></div>
      <div class="bar"><div class="bar-fill" style="width:${{ratioPct}}%;background:${{ratioColor}}"></div></div>
      <div class="row"><span class="label">Claims</span><span class="val">${{r.claims}}</span></div>
      <div class="row"><span class="label">Phantoms</span><span class="val ${{r.phantoms > 0 ? 'red' : 'green'}}">${{r.phantoms}}</span></div>
      <div class="row"><span class="label">Verified</span><span class="val green">${{r.verified}}</span></div>
      <div class="row"><span class="label">Hedges</span><span class="val">${{r.hedges}}</span></div>
      <div class="row"><span class="label">Composite</span><span class="val">${{r.composite}}</span></div>
    </div>`;
}});
</script>
</body>
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    results = json.loads(Path(args.results).read_text())
    html = build(results)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"built {OUTPUT} ({len(html)} bytes)")
    if args.out:
        Path(args.out).write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
