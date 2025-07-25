# agent/tool.py

from typing import Any, Dict, List
from pydantic import BaseModel
import pandas as pd

# 1. LOAD SHEET

class LoadParams(BaseModel):
    path: str
    sheet_name: str

def load_audit_sheet(params: LoadParams) -> Dict[str, Any]:
    df = pd.read_excel(params.path, sheet_name=params.sheet_name)
    records: List[Dict[str, Any]] = df.to_dict(orient="records")
    return {"status": "success", "records": records}


# 2. VALIDATE ENTRIES

class ValidateParams(BaseModel):
    records: List[Dict[str, Any]]

def validate_entries(params: ValidateParams) -> Dict[str, Any]:
    issues = []
    for idx, row in enumerate(params.records):
        if pd.isna(row.get("Baseline Evidence")):
            issues.append({
                "row": idx + 2,
                "Question ID": row.get("Question ID"),
                "issue": "Missing Baseline Evidence"
            })
    return {"status": "success", "issues": issues}


# 3. ASSIGN CONFORMITY

class AssignParams(BaseModel):
    records: List[Dict[str, Any]]

def assign_conformity(params: AssignParams) -> Dict[str, Any]:
    updated = []
    for row in params.records:
        evidence = row.get("Baseline Evidence")
        level = "Full" if (not pd.isna(evidence) and str(evidence).strip()) else "None"
        new_row = row.copy()
        new_row["Conformity Level"] = level
        updated.append(new_row)
    return {"status": "success", "records": updated}


# 4. SUMMARIZE FINDINGS

class SummarizeParams(BaseModel):
    records: List[Dict[str, Any]]

def summarize_findings(params: SummarizeParams) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    total = len(params.records)
    for row in params.records:
        lvl = row.get("Conformity Level", "None")
        counts[lvl] = counts.get(lvl, 0) + 1

    summary = {
        lvl: {
            "count": cnt,
            "percentage": round((cnt / total) * 100, 2) if total else 0.0
        }
        for lvl, cnt in counts.items()
    }
    return {"status": "success", "summary": summary}


# 5. EXPORT TO EXCEL

class ExportParams(BaseModel):
    records: List[Dict[str, Any]]
    output_path: str

def export_to_excel(params: ExportParams) -> Dict[str, Any]:
    df = pd.DataFrame(params.records)
    df.to_excel(params.output_path, index=False)
    return {"status": "success", "output_path": params.output_path}
