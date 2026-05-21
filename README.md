# 🔍 Azure Intelligent Log Analyser

> Parse Azure Monitor and Windows Event logs and get AI-generated  
> root cause analysis in seconds — with a modern web interface.  
> Powered by Gemini 2.5 Flash. Built from 3 years of Azure IaaS incident response at Microsoft.

---

## What it does

Drop in a log file. Get back a plain-English report: what broke, why it broke,  
how to fix it — with a severity score from 1 to 10.

No manual log reading. No guessing. Just answers.

---

## Features

- 🌐 **Modern web UI** — drag & drop log files, live progress bar, built-in report viewer
- 🤖 **AI-powered RCA** — Gemini 2.5 Flash identifies root cause and top 3 fixes
- 🔴 **Severity scoring** — 1–10 score with plain-English justification
- 🕐 **Report history** — all past analyses saved and browsable in the sidebar
- ⚙️ **CLI mode** — run headless via terminal for automation pipelines
- 📄 **Markdown export** — every report saved as a `.md` file locally

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Backend | Python · FastAPI · Uvicorn |
| AI Analysis | Python · Google Gemini 2.5 Flash API |
| Web Frontend | HTML · CSS · Vanilla JS (zero dependencies) |
| Log Parser | C# · .NET 8 CLI |
| Pipeline Runner | Python · run.py |

---

## How to Run (Web UI)

### Prerequisites
- Python 3.11+
- .NET 8 SDK
- Free Gemini API key from [aistudio.google.com](https://aistudio.google.com) — no credit card needed

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/azure-log-analyser.git
cd azure-log-analyser/src/analyser

python3 -m venv venv
source venv/bin/activate          # Mac/Linux
pip install google-genai python-dotenv fastapi uvicorn python-multipart

echo "GEMINI_API_KEY=your_key_here" > .env
```

### Start the app

```bash
cd azure-log-analyser/src/analyser
source venv/bin/activate
uvicorn server:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

---

## How to Run (CLI only)

```bash
cd azure-log-analyser
python3 run.py --file samples/vm_boot_failure.json
```

---

## Sample Output

Drop in a log file and get back:

| Field | Example |
|-------|---------|
| Severity | 🔴 CRITICAL (8/10) |
| What happened | VM rebooted unexpectedly due to disk corruption on the OS volume |
| Root cause | NTFS corruption on Disk 0 triggered a kernel panic (bugcheck 0x7E) |
| Fix 1 | Run chkdsk /f /r on the OS volume from WinRE |
| Fix 2 | Replace Standard HDD managed disk with Premium SSD |
| Fix 3 | Enable Azure VM boot diagnostics for early warning |

---

## Scenarios Included

| Sample File | Scenario |
|-------------|----------|
| `vm_boot_failure.json` | Unexpected VM reboot + OS disk corruption + kernel panic |
| `disk_iops_saturation.json` | SQL Server failure caused by Standard HDD IOPS cap exceeded |

---

## Why I Built This

After 3 years doing root cause analysis on Azure IaaS workloads at Microsoft,
I built this tool to automate the first 20 minutes of any incident investigation.
It packages the debugging patterns I used daily into a tool any engineer can run.