# 🔍 Azure Intelligent Log Analyser

> Parse Azure Monitor and Windows Event logs and get AI-generated
> root cause analysis reports in seconds — powered by Gemini 2.5 Flash.

Built from 3 years of hands-on Azure IaaS incident response at Microsoft.

---

## What it does

You give it a log file. It gives you a plain-English report: what broke,
why it broke, and exactly how to fix it — with a severity score.

No manual log reading. No guessing. Just answers.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Log Parser | C# .NET 8 CLI |
| AI Analysis | Python 3 + Gemini 2.5 Flash API |
| Pipeline Runner | Python 3 |
| Output | Markdown report |

---

## How to Run

### Prerequisites
- Python 3.11+
- .NET 8 SDK
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Setup

```bash
git clone https://github.com/NitescuBianca/azure-log-analyser.git
cd azure-log-analyser

# Set up Python environment
cd src/analyser
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
pip install google-genai python-dotenv

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env
cd ../..
```

### Run

```bash
python3 run.py --file samples/vm_boot_failure.json
```

---

## Sample Output