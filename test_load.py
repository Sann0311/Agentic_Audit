# test_load.py

from agent.tool import load_audit_sheet, LoadParams

def main():
    # Adjust the path and sheet_name to whatever your file actually is called
    params = LoadParams(
    path="Vendor_Self_Assessment_Form_Evidence List .xlsx",
    sheet_name="GenAI Security Audit Sheet"
)

    result = load_audit_sheet(params)
    print(f"Status: {result['status']}")
    print(f"Rows loaded: {len(result['records'])}")
    # Optional: print the first record to inspect
    print("First record:", result["records"][0])

if __name__ == "__main__":
    main()
