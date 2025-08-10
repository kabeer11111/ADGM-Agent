ADGM_CHECKLIST = {
    "Company Incorporation": [
        "Articles of Association", "Memorandum of Association",
        "Incorporation Application Form", "UBO Declaration", "Board Resolution",
        "Register of Members and Directors", "Shareholder Resolution",
        "Change of Registered Address Notice"
    ],
    "Licensing Regulatory Filings": [
        "Licensing Regulatory Filing", "Renewal Application Form", "Compliance Declaration"
    ],
    "Employment HR Contracts": ["Employment Contract"],
    "Commercial Agreements": ["Commercial Agreement"],
    "Compliance Risk Policies": ["Compliance Risk Policy"]
}

def verify_checklist(found_types, process, issues=None):
    if process not in ADGM_CHECKLIST:
        return [], []

    required = set(ADGM_CHECKLIST[process])
    found = set(found_types)

    # Missing docs = required but not uploaded
    missing = list(required - found)

    problematic = []
    if issues:
        for issue in issues:
            dt = issue.get("document_type")
            # A doc is problematic if it is required, found, and not already marked problematic
            if dt in required and dt in found and dt not in problematic:
                problematic.append(dt)

    return missing, problematic
