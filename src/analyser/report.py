from datetime import datetime

def severity_badge(score: int) -> str:
    if score >= 8:
        return f"🔴 CRITICAL ({score}/10)"
    elif score >= 5:
        return f"🟠 HIGH ({score}/10)"
    elif score >= 3:
        return f"🟡 MEDIUM ({score}/10)"
    else:
        return f"🟢 LOW ({score}/10)"

def generate_report(rca: dict, top_entries: list[dict], output_path: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    badge = severity_badge(rca.get("severity_score", 0))

    # Summary table rows
    source_counts: dict[str, dict[str, int]] = {}
    for e in top_entries:
        sev = e.get("Severity", "Unknown")
        src = e.get("Source", "Unknown")
        source_counts.setdefault(sev, {})
        source_counts[sev][src] = source_counts[sev].get(src, 0) + 1

    table_rows = []
    for sev, sources in source_counts.items():
        for src, count in sources.items():
            table_rows.append(f"| {sev} | {src} | {count} |")
    table_str = "\n".join(table_rows)

    # Recommendations
    recs = rca.get("recommendations", [])
    recs_str = "\n".join(f"{r}" for r in recs)

    # Raw log lines
    raw_logs = "\n".join(
        f"[{e.get('Timestamp','N/A')}] [{e.get('Severity','N/A')}] "
        f"[EventId: {e.get('EventId','N/A')}] [{e.get('Source','N/A')}] "
        f"{e.get('Message','N/A')}"
        for e in top_entries
    )

    report = f"""# Azure Log Analysis Report
> Generated: {now}

---

## Severity Assessment
**{badge}**
_{rca.get('severity_justification', '')}_ 

---

## Explain what happened
{rca.get('what_happened', 'N/A')}

---
## Root cause 
{rca.get('root_cause', 'N/A')}

---

## Event summary
| Severity | Source | Count |
|----------|--------|-------|
{table_str}

---

## Recommendations
{recs_str}

---

## Top critical log lines
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)