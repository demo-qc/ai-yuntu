"""Minimal HTTP wrapper around debug-trace.sh for Insomnia / curl testing.

Run:
    pip install fastapi uvicorn
    uvicorn server:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "debug-trace.sh"

app = FastAPI(title="ai-yuntu debug-trace")


class DebugRequest(BaseModel):
    trace_id: str
    app_name: str
    output_type: str = "basic"


@app.post("/debug")
def debug(req: DebugRequest):
    proc = subprocess.Popen(
        [str(SCRIPT), req.trace_id, req.app_name, req.output_type],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def stream():
        assert proc.stdout is not None
        for line in proc.stdout:
            yield line
        proc.wait()

    return StreamingResponse(stream(), media_type="application/x-ndjson")
