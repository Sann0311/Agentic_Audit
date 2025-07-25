
from typing import Any, Dict, List
from pydantic import BaseModel
import pandas as pd
import numpy as np

# 4. SUMMARIZE FINDINGS

class SummarizeParams(BaseModel):
    records: List[Dict[str, Any]]

def summarize_findings(params: SummarizeParams) -> Dict[str, Any]:
    """
    Returns a count and percentage of each conformity level.
    """
    try:
        counts = {}
        total = len(params.records)
        for row in params.records:
            lvl = row.get("Conformity Level", "N/A")
            counts[lvl] = counts.get(lvl, 0) + 1
        # Build a summary dict
        summary = {}
        for lvl, cnt in counts.items():
            percentage = round((cnt / total) * 100, 2) if total > 0 else 0.0
            summary[lvl] = {
                "count": cnt,
                "percentage": percentage
            }
        return {
            "status": "success",
            "summary": summary,
            "total_records": total
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "summary": {}
        }

# 3. ASSIGN CONFORMITY PARAMS
class AssignParams(BaseModel):
    records: List[Dict[str, Any]]

# --- Conformity Assignment Logic ---
def assign_conformity_level(observation: str, baseline_evidence: str) -> str:
    """
    Assigns conformity level based on comparison of observation and baseline evidence.
    This is a simple rule-based version. You can replace with LLM/semantic logic if needed.
    """
    if not isinstance(observation, str) or not observation.strip():
        return "N/A"
    if not isinstance(baseline_evidence, str) or not baseline_evidence.strip():
        return "No Conformity"
    obs = observation.strip().lower()
    base = baseline_evidence.strip().lower()
    # Full conformity: observation contains all key evidence words (very basic)
    if base in obs or obs in base:
        return "Full Conformity"
    # Partial: some overlap (very basic, can be improved)
    obs_words = set(obs.split())
    base_words = set(base.split())
    overlap = obs_words & base_words
    if overlap and (len(overlap) >= min(3, len(base_words))):
        return "Partial Conformity"
    # No conformity: observation present but not matching evidence
    return "No Conformity"

# agent/tool.py


from typing import Any, Dict, List
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np

def clean_for_json(obj):
    """
    Recursively clean data structure to be JSON-safe.
    Converts NaN, inf, -inf to None, and other non-serializable types.
    """
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if pd.isna(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return obj

# 1. LOAD SHEET

class LoadParams(BaseModel):
    path: str
    sheet_name: str

def load_audit_sheet(params: LoadParams) -> Dict[str, Any]:
    """
    Reads the Excel file and returns its rows as a list of dicts.
    Handles NaN values and makes data JSON-safe.
    """
    try:
        df = pd.read_excel(params.path, sheet_name=params.sheet_name)
        
        # Convert DataFrame to records and clean for JSON
        records = df.to_dict(orient="records")
        clean_records = clean_for_json(records)
        
        return {
            "status": "success",
            "records": clean_records,
            "row_count": len(clean_records)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "records": []
        }


# 2. VALIDATE ENTRIES

class ValidateParams(BaseModel):
    records: List[Dict[str, Any]]

def validate_entries(params: ValidateParams) -> Dict[str, Any]:
    # ...existing code...
    pass

def assign_conformity(params: AssignParams) -> Dict[str, Any]:
    """
    Assigns 'Conformity Level' for each record based on comparison of Observation and Baseline Evidence.
    Levels: Full Conformity, Partial Conformity, No Conformity, N/A
    """
    try:
        updated = []
        for row in params.records:
            observation = row.get("Observation", "")
            baseline_evidence = row.get("Baseline Evidence", "")
            conformity = assign_conformity_level(observation, baseline_evidence)
            new_row = row.copy()
            new_row["Conformity Level"] = conformity
            updated.append(new_row)
        clean_updated = clean_for_json(updated)
        return {
            "status": "success",
            "records": clean_updated
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "records": []
        }
    """
    Returns a count and percentage of each conformity level.
    """
    try:
        counts = {}
        total = len(params.records)
        for row in params.records:
            lvl = row.get("Conformity Level", "N/A")
            counts[lvl] = counts.get(lvl, 0) + 1
        # Build a summary dict
        summary = {}
        for lvl, cnt in counts.items():
            percentage = round((cnt / total) * 100, 2) if total > 0 else 0.0
            summary[lvl] = {
                "count": cnt,
                "percentage": percentage
            }
        return {
            "status": "success",
            "summary": summary,
            "total_records": total
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "summary": {}
        }
                # ...existing code...


# 5. EXPORT TO EXCEL

class ExportParams(BaseModel):
    records: List[Dict[str, Any]]
    output_path: str

def export_to_excel(params: ExportParams) -> Dict[str, Any]:
    """
    Writes the provided records to an Excel file.
    """
    try:
        df = pd.DataFrame(params.records)
        df.to_excel(params.output_path, index=False)
        return {
            "status": "success",
            "output_path": params.output_path,
            "rows_exported": len(params.records)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "output_path": params.output_path
        }