import argparse
import subprocess
import sys
import os
from datetime import datetime

def run_pipeline(log_file: str):
    project_root = os.path.dirname(os.path.abspath(__file__))
    csharp_cli   = os.path.join(project_root, "src", "LogAnalyser.CLI", "LogAnalyser.CLI")
    analyser_dir = os.path.join(project_root, "src", "analyser")
    analyser_py  = os.path.join(analyser_dir, "analyser.py")
    python_bin   = os.path.join(analyser_dir, "venv", "bin", "python3")

    timestamp    = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    parsed_json  = os.path.join(project_root, "samples", f"parsed_{timestamp}.json")
    report_md    = os.path.join(project_root, "samples", f"report_{timestamp}.md")

    log_file = os.path.abspath(log_file)

    # --- Check if log file is already JSON (skip C# parser if so) ---
    if log_file.endswith(".json"):
        print(f"📂 Input is JSON — skipping C# parser, sending directly to AI analyser...")
        parsed_json = log_file
    else:
        print(f"⚙️  Step 1/2 — Parsing log file with C# CLI...")
        result = subprocess.run(
            ["dotnet", "run", "--project", csharp_cli, "--", "--file", log_file, "--output", parsed_json],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ C# parser failed:\n{result.stderr}")
            sys.exit(1)
        print(f"   Parsed log saved to: {parsed_json}")

    print(f"🤖 Step 2/2 — Running AI analysis with Gemini...")
    result = subprocess.run(
        [python_bin, analyser_py, "--input", parsed_json, "--output", report_md],
        capture_output=True, text=True, cwd=analyser_dir
    )
    if result.returncode != 0:
        print(f"❌ AI analyser failed:\n{result.stderr}")
        sys.exit(1)

    print(result.stdout)
    print(f"📄 Report: {report_md}")
    print(f"\nOpen it with: code {report_md}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure Log Analyser Pipeline")
    parser.add_argument("--file", required=True, help="Path to log file (.json or .csv)")
    args = parser.parse_args()
    run_pipeline(args.file)