# agent/tool.py

from typing import Any, Dict, List
from pydantic import BaseModel
import pandas as pd

# 1. LOAD SHEET

class LoadParams(BaseModel):
    """
    Parameters for loading an Excel sheet.
    - path: the path to your .xlsx file
    - sheet_name: the worksheet name
    """
    path: str
    sheet_name: str

def load_audit_sheet(params: LoadParams) -> Dict[str, Any]:
    """
    Reads the Excel file and returns its rows as a list of dicts.
    """
    df = pd.read_excel(params.path, sheet_name=params.sheet_name)
    records: List[Dict[str, Any]] = df.to_dict(orient="records")
    return {
        "status": "success",
        "records": records
    }


# 2. VALIDATE ENTRIES

class ValidateParams(BaseModel):
    """
    Parameters for validating the loaded records.
    - records: output from load_audit_sheet
    """
    records: List[Dict[str, Any]]

def validate_entries(params: ValidateParams) -> Dict[str, Any]:
    """
    Flags any row where 'Baseline Evidence' is missing.
    """
    issues = []
    for idx, row in enumerate(params.records):
        if pd.isna(row.get("Baseline Evidence")):
            issues.append({
                "row": idx + 2,  # account for header row in Excel
                "Question ID": row.get("Question ID"),
                "issue": "Missing Baseline Evidence"
            })
    return {
        "status": "success",
        "issues": issues
    }


# 3. ASSIGN CONFORMITY

class AssignParams(BaseModel):
    """
    Parameters for assigning conformity levels.
    - records: the list from validate_entries (or load)
    """
    records: List[Dict[str, Any]]

def assign_conformity(params: AssignParams) -> Dict[str, Any]:
    """
    Sets 'Conformity Level' to Full if evidence exists, 
    otherwise None. (Customize logic for Partial as needed.)
    """
    updated = []
    for row in params.records:
        evidence = row.get("Baseline Evidence")
        if not pd.isna(evidence) and str(evidence).strip() != "":
            level = "Full"
        else:
            level = "None"
        new_row = row.copy()
        new_row["Conformity Level"] = level
        updated.append(new_row)
    return {
        "status": "success",
        "records": updated
    }


# 4. SUMMARIZE FINDINGS

class SummarizeParams(BaseModel):
    """
    Parameters for summarizing conformity results.
    - records: output from assign_conformity
    """
    records: List[Dict[str, Any]]

def summarize_findings(params: SummarizeParams) -> Dict[str, Any]:
    """
    Returns a count and percentage of each conformity level.
    """
    counts = {}
    total = len(params.records)
    for row in params.records:
        lvl = row.get("Conformity Level", "None")
        counts[lvl] = counts.get(lvl, 0) + 1

    # build a summary dict
    summary = {
        lvl: {
            "count": cnt,
            "percentage": round((cnt / total) * 100, 2) if total else 0.0
        } for lvl, cnt in counts.items()
    }
    return {
        "status": "success",
        "summary": summary
    }


# 5. EXPORT TO EXCEL

class ExportParams(BaseModel):
    """
    Parameters for exporting results back to Excel.
    - records: any list of dicts (e.g. from assign_conformity)
    - output_path: where to write the .xlsx
    """
    records: List[Dict[str, Any]]
    output_path: str

def export_to_excel(params: ExportParams) -> Dict[str, Any]:
    """
    Writes the provided records to an Excel file.
    """
    df = pd.DataFrame(params.records)
    df.to_excel(params.output_path, index=False)
    return {
        "status": "success",
        "output_path": params.output_path
    }
