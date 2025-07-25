# backend/main.py

import os
import sys
import json
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ──────────────────────────────────────────────────────────────────────────────
# Ensure the headless agent package is importable at runtime
# ──────────────────────────────────────────────────────────────────────────────
AGENT_DIR = os.path.join(os.getcwd(), "agent")
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

# Pylance may not resolve this dynamic import:
from multi_tool_agent.agent import root_agent  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI setup
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    tool: str
    params: Dict[str, Any]

class Session(BaseModel):
    # ADK expects `session` to have a `.state` attribute
    state: Dict[str, Any] = {}

class AgentRunPayload(BaseModel):
    """
    Envelope that run_async expects:
    - tool: the tool name
    - params: its parameters
    - session: a Session object with .state
    """
    tool: str
    params: Dict[str, Any]
    session: Session

# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/status")
async def status():
    return {"message": "OK"}

@app.post("/api/create_session")
async def create_session():
    # No real session tracking needed; return a dummy
    return {"session_id": "default"}


from fastapi import Request

@app.post("/api/run")
async def run_tool(request: Request):
    """
    Invoke one of the agent’s tools headlessly and return the final output.
    Accepts raw JSON for better compatibility with PowerShell and other clients.
    """
    try:
        data = await request.json()
        tool = data.get("tool")
        params = data.get("params", {})
        payload = AgentRunPayload(
            tool=tool,
            params=params,
            session=Session()
        )
        gen = root_agent.run_async(payload)
        final_output = None
        async for msg in gen:
            final_output = msg
        if hasattr(final_output, "model_dump"):
            return final_output.model_dump()
        return final_output
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/get_reports")
async def get_reports():
    reports: List[Dict[str, Any]] = []
    data_dir = "/attack_data"
    for fname in os.listdir(data_dir):
        if fname.endswith(".json") and "REPORT" in fname:
            with open(os.path.join(data_dir, fname), "r") as f:
                reports.append(json.load(f))
    return reports

@app.get("/api/attack_data/{filename}")
async def get_attack_data(filename: str):
    file_path = os.path.join("/attack_data", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    with open(file_path, "r") as f:
        return json.load(f)