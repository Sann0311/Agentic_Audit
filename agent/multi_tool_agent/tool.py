# agent/tool.py

from typing import Any, Dict, List
from pydantic import BaseModel
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
    try:
        issues = []
        for idx, row in enumerate(params.records):
            raw_evidence = row.get("Baseline Evidence", "")
            conformity = row.get("Conformity Level", "").strip().lower()

            # DEBUG
            print(f"\n[DEBUG] Row {idx + 2}")
            print(f"  Question ID: {row.get('Question ID')}")
            print(f"  Baseline Evidence: {repr(raw_evidence)}")
            print(f"  Conformity Level: {repr(conformity)}")

            # Normalize evidence
            if isinstance(raw_evidence, str):
                normalized = raw_evidence.replace("\n", " ").replace("\r", "").strip()
            else:
                normalized = str(raw_evidence).strip()

            # Skip if evidence is sufficient or conformity is full
            if normalized and normalized.lower() not in ("nan", "none") or conformity == "full conformity":
                continue

            # Flag missing evidence
            issues.append({
                "row": idx + 2,
                "Question ID": row.get("Question ID", ""),
                "issue": "Missing Baseline Evidence"
            })

        return {
            "status": "success",
            "issues": issues,
            "total_issues": len(issues)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "issues": []
        }



# 3. ASSIGN CONFORMITY

class AssignParams(BaseModel):
    records: List[Dict[str, Any]]

def assign_conformity(params: AssignParams) -> Dict[str, Any]:
    """
    Sets 'Conformity Level' to Full if evidence exists, 
    otherwise None. (Customize logic for Partial as needed.)
    """
    try:
        updated = []
        for row in params.records:
            evidence = row.get("Baseline Evidence")
            
            # Check if evidence exists and is not empty
            if evidence is not None and str(evidence).strip() != "" and not pd.isna(evidence):
                level = "Full"
            else:
                level = "None"
            
            new_row = row.copy()
            new_row["Conformity Level"] = level
            updated.append(new_row)
        
        # Clean the updated records for JSON
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
            lvl = row.get("Conformity Level", "None")
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