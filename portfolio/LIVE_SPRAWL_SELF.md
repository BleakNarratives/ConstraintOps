# Codebase Sprawl Triage — BleakNarratives (self)

*Generated 2026-09-11 09:22 · prepared under the ConstraintOps creed: we reveal, we don't conceal. Every finding below can be re-verified with the commands in the appendix.*

## 1. Executive summary

- Folder `/home/bleaknarratives/ConstraintOps` contains **53 files** (14 code, 34 docs), roughly **1,864 lines** of code.
- Python compile gate: **14/14 files compile clean**; 0 broken (list in findings).
- 5 candidate entrypoints detected (__main__ guards).

## 2. Inventory

| Metric | Count |
|---|---|
| Total files (excluding deps/caches) | 53 |
| Code files | 14 |
| Docs/notes | 34 |
| Lines of code | 1,864 |
| Python compile-clean | 14/14 |
| Backup-lineage files | 0 |
| Exact-duplicate files | 0 |
| Same-name files in multiple dirs | 1 |
| Files >1MB (logs/assets in tree) | 0 |

## 3. Findings

### Broken code (compile gate)

- None. Everything that can be parsed, parses.

### Duplicate content (exact, by hash)

- None found.

### Backup-lineage (uncommitted history)

- None found.

## 4. Damage assessment — OPERATOR PASS REQUIRED

*Human pass: which broken files are load-bearing? Which duplicate set is canonical? Which backup file holds the newest real code? Placeholder until the operator reviews the evidence.*

## 5. Ship-path ranking — OPERATOR PASS REQUIRED

*Human pass: 3 fastest credible paths to something deployable, ranked by effort-to-first-value, each traceable to inventory rows above.*

## Appendix — evidence & re-verification

Re-run this exact analysis yourself:

```bash
python sprawl_report.py --client "BleakNarratives (self)" --root /home/bleaknarratives/ConstraintOps

# verify a specific python file compiles:
#   python -m py_compile <file>

# find exact duplicates yourself:
#   find <root> -type f -size +200c -exec sha256sum {} + | sort | uniq -w64 -D
```
