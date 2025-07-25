# agent/multi_tool_agent/agent.py

import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# Import your tool functions directly

from .tool import (
    load_audit_sheet,
    validate_entries,
    assign_conformity,
    summarize_findings,
    export_to_excel,
)

# ===========================
# LLM Model Configuration
# ===========================
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434")
model = LiteLlm(
    model="ollama/gemma3",
    api_base=OLLAMA_API_BASE,
    temperature=0.0,
)

# ===========================
# Agent Instruction
# ===========================
instruction = """
You are an audit-data assistant. 
When the user asks you to perform an action on the Excel audit data,
respond with exactly one JSON object to call the appropriate tool:

  { "tool": "<tool_name>", "params": { … } }

Available tools:
- load_audit_sheet
- validate_entries
- assign_conformity
- summarize_findings
- export_to_excel
"""

# ===========================
# Register your callables
# ===========================
tools = [
    load_audit_sheet,
    validate_entries,
    assign_conformity,
    summarize_findings,
    export_to_excel,
]

# ===========================
# Create the Agent
# ===========================
root_agent = LlmAgent(
    name="multi_tool_agent",
    model=model,
    instruction=instruction,
    tools=tools,
    generate_content_config=types.GenerateContentConfig(temperature=0.15),
)

# Debug: print which functions were registered
print("\nRegistered Tools:")
for fn in tools:
    print(" -", fn.__name__)
