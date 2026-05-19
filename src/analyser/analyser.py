import json
import os
import argparse
from dotenv import load_dotenv
from google import genai

load_dotenv()

SEVERITY_RANK = {
    "critical": 0,
    "error": 1,
    "warning": 2,
    "information": 3,
    "verbose": 4,
    "unknown": 5
}

def load_parsed_logs(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def rank_and_filter(entries: list[dict], top_n: int = 20) -> list[dict]:
    sorted_entries = sorted(
        entries,
        key=lambda e: SEVERITY_RANK.get(e.get("Severity", "unknown").lower(), 5)
    )
    return sorted_entries[:top_n]

def group_summary(entries: list[dict]) -> str:
    groups: dict[str, dict[str, int]] = {}
    for e in entries:
        severity = e.get("Severity", "Unknown")
        source = e.get("Source", "Unknown")
        groups.setdefault(severity, {})
        groups[severity][source] = groups[severity].get(source, 0) + 1

    lines = []
    for severity, sources in groups.items():
        for source, count in sources.items():
            lines.append(f"  - [{severity}] {source}: {count} event(s)")
    return "\n".join(lines)

def build_prompt(top_entries: list[dict], summary: str) -> str:
    log_block = "\n".join(
        f"[{e.get('Timestamp', 'N/A')}] [{e.get('Severity', 'N/A')}] "
        f"[EventId: {e.get('EventId', 'N/A')}] [{e.get('Source', 'N/A')}] "
        f"{e.get('Message', 'N/A')}"
        for e in top_entries
    )

    return f"""
Below is a summary of log events grouped by severity and source:
{summary}

Below are the top {len(top_entries)} most critical log entries:
{log_block}

Taks:
1. Identify WHAT happened (describe the incident or failure in plain English, 2-3 sentences).
2. Identify the ROOT CAUSE (the most likely underlying technical reason, be specific).
3. List the TOP 3 RECOMMENDED FIXES in order of priority, each as a concrete actionable step.
4. Assign a SEVERITY SCORE from 1 (minor) to 10 (critical outage) with a one-line justification.

Respond ONLY in the following JSON format, no markdown, no extra text:
{{
  "what_happened": "...",
  "root_cause": "...",
  "recommendations": [
    "1. ...",
    "2. ...",
    "3. ..."
  ],
  "severity_score": 7,
  "severity_justification": "..."
}}"""

def call_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text.strip()
    # Strip markdown code fences if Gemini adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def analyse(input_path: str) -> tuple[dict, list[dict]]:
    entries = load_parsed_logs(input_path)
    top_entries = rank_and_filter(entries, top_n=20)
    summary = group_summary(entries)
    prompt = build_prompt(top_entries, summary)
    rca = call_gemini(prompt)
    return rca, top_entries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Log Analyser")
    parser.add_argument("--input", required=True, help="Path to parsed JSON log file")
    parser.add_argument("--output", required=True, help="Path to save the markdown report")
    args = parser.parse_args()

    from report import generate_report
    rca, top_entries = analyse(args.input)
    generate_report(rca, top_entries, args.output)
    print(f"\n✅ Report saved to: {args.output}")
    print(f"   Severity score : {rca['severity_score']}/10")
    print(f"   Root cause     : {rca['root_cause'][:80]}...")