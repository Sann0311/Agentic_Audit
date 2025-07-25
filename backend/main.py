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

# Also import the tool functions directly for direct invocation
# Import from the tool.py file in the agent directory
sys.path.append(os.path.join(AGENT_DIR, "multi_tool_agent"))
from tool import (
    load_audit_sheet, LoadParams,
    validate_entries, ValidateParams, 
    assign_conformity, AssignParams,
    summarize_findings, SummarizeParams,
    export_to_excel, ExportParams
)

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
# Tool mapping for direct invocation
# ──────────────────────────────────────────────────────────────────────────────
TOOL_MAPPING = {
    "load_audit_sheet": (load_audit_sheet, LoadParams),
    "validate_entries": (validate_entries, ValidateParams),
    "assign_conformity": (assign_conformity, AssignParams),
    "summarize_findings": (summarize_findings, SummarizeParams),
    "export_to_excel": (export_to_excel, ExportParams),
}

# ──────────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    tool: str
    params: Dict[str, Any]

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

@app.post("/api/run")
async def run_tool(request: RunRequest):
    """
    Invoke one of the agent's tools directly and return the output.
    This bypasses the agent conversation interface and calls tools directly.
    """
    try:
        tool_name = request.tool
        params = request.params
        
        print(f"Received request - Tool: {tool_name}, Params: {params}")
        
        # Check if tool exists
        if tool_name not in TOOL_MAPPING:
            available_tools = list(TOOL_MAPPING.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )
        
        # Get the tool function and parameter model
        tool_func, param_model = TOOL_MAPPING[tool_name]
        
        # Validate and create parameters
        try:
            validated_params = param_model(**params)
            print(f"Validated params: {validated_params}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Parameter validation failed for {tool_name}: {str(e)}"
            )
        
        # Call the tool function
        result = tool_func(validated_params)
        print(f"Tool result: {result}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Unexpected error: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/get_reports")
async def get_reports():
    reports: List[Dict[str, Any]] = []
    data_dir = "/attack_data"
    if os.path.exists(data_dir):
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