import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from analyser import analyse
from report import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR   = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Serve the frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    index = STATIC_DIR / "index.html"
    return HTMLResponse(content=index.read_text(encoding="utf-8"))

@app.get("/history")
async def get_history():
    reports = []
    for f in sorted(REPORTS_DIR.glob("*.json"), reverse=True)[:20]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            reports.append(data)
        except Exception:
            continue
    return JSONResponse(content=reports)

@app.post("/analyse")
async def analyse_log(file: UploadFile = File(...)):
    async def event_stream():
        try:
            # Step 1 — receive file
            yield f"data: {json.dumps({'step': 'upload', 'message': 'File received: ' + file.filename, 'progress': 10})}\n\n"
            await asyncio.sleep(0.3)

            contents = await file.read()
            tmp_path = REPORTS_DIR / f"tmp_{uuid.uuid4().hex}.json"

            # Handle JSON directly
            if file.filename.endswith(".json"):
                tmp_path.write_bytes(contents)
            else:
                yield f"data: {json.dumps({'step': 'error', 'message': 'Only .json files supported in this version.'})}\n\n"
                return

            yield f"data: {json.dumps({'step': 'parsing', 'message': 'Parsing log entries...', 'progress': 30})}\n\n"
            await asyncio.sleep(0.3)

            # Step 2 — run analysis
            yield f"data: {json.dumps({'step': 'analysing', 'message': 'Sending to Gemini 2.5 Flash for root cause analysis...', 'progress': 55})}\n\n"

            loop = asyncio.get_event_loop()
            rca, top_entries = await loop.run_in_executor(None, analyse, str(tmp_path))

            yield f"data: {json.dumps({'step': 'generating', 'message': 'Generating markdown report...', 'progress': 80})}\n\n"
            await asyncio.sleep(0.2)

            # Step 3 — save report
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_md  = REPORTS_DIR / f"report_{timestamp}.md"
            report_meta = REPORTS_DIR / f"report_{timestamp}.json"

            generate_report(rca, top_entries, str(report_md))

            # Save metadata for history
            meta = {
                "id": timestamp,
                "filename": file.filename,
                "timestamp": timestamp.replace("_", " "),
                "severity_score": rca.get("severity_score", 0),
                "severity_justification": rca.get("severity_justification", ""),
                "what_happened": rca.get("what_happened", ""),
                "root_cause": rca.get("root_cause", ""),
                "recommendations": rca.get("recommendations", []),
                "report_md": str(report_md),
                "entry_count": len(top_entries),
                "top_entries": top_entries
            }
            report_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

            # Cleanup tmp
            tmp_path.unlink(missing_ok=True)

            yield f"data: {json.dumps({'step': 'done', 'message': 'Analysis complete!', 'progress': 100, 'result': meta})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")