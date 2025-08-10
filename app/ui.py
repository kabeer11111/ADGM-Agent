
from collections import Counter
import json
import streamlit as st
from datetime import datetime

import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.parser import detect_doc_type
from app.rules import red_flags
from app.checklist import verify_checklist
from app.comments import insert_comments
from app.summary import summarize_document

PROCESS_MAP = {
    "Company Incorporation": [
        "Articles of Association", "Memorandum of Association",
        "Incorporation Application Form", "UBO Declaration", "Board Resolution",
        "Register of Members and Directors", "Shareholder Resolution", "Change of Registered Address Notice"
    ],
    "Licensing Regulatory Filings": [
        "Licensing Regulatory Filing", "Renewal Application Form", "Compliance Declaration"
    ],
    "Employment HR Contracts": ["Employment Contract"],
    "Commercial Agreements": ["Commercial Agreement"],
    "Compliance Risk Policies": ["Compliance Risk Policy"]
}

def main():
    st.title("ADGM Corporate Agent - RAG-Powered Compliance Review")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload ADGM .docx files", 
        type="docx", 
        accept_multiple_files=True
    )
    
    if not uploaded_files:
        st.info("👆 Please upload one or more .docx files to begin analysis")
        return

    st.success(f"Processing {len(uploaded_files)} uploaded files...")

    # Initialize processing containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    filepaths = []
    doc_types = []
    all_issues = []
    summaries = {}
    
    # Create debugging expander
    with st.expander("🔍 Processing Debug Information", expanded=False):
        debug_container = st.empty()

    # Process each uploaded file
    debug_info = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Update progress
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
        
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            filepaths.append(temp_path)
            
            # Step 1: Detect document type
            detected_type = detect_doc_type(temp_path)
            doc_types.append(detected_type)
            
            debug_info.append(f"📄 {uploaded_file.name}: Detected as '{detected_type}'")
            
            # Step 2: Generate summary
            summary = summarize_document(temp_path, detected_type)
            summaries[temp_path] = summary
            
            debug_info.append(f"   ✅ Summary generated ({len(summary)} characters)")
            
            # Step 3: Check for issues
            issues = red_flags(temp_path, detected_type)
            all_issues.extend(issues)
            
            debug_info.append(f"   🚨 Found {len(issues)} issues")
            
            # Update debug display
            with debug_container.container():
                st.text("\n".join(debug_info))
        
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            debug_info.append(f"❌ {uploaded_file.name}: Error - {str(e)}")
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    if not filepaths:
        st.error("No files were successfully processed.")
        return

    st.markdown("---")

    # ===== DOCUMENT SUMMARIES SECTION =====
    st.header("📋 Document Summaries")
    
    for i, (filepath, doc_type) in enumerate(zip(filepaths, doc_types)):
        filename = os.path.basename(filepath)
        
        with st.expander(f"{i+1}. {filename} ({doc_type})", expanded=False):
            summary = summaries.get(filepath, "Summary not available")
            st.markdown(summary)
            
            # Show any issues for this specific document
            doc_issues = [issue for issue in all_issues if issue.get("document_type") == doc_type]
            if doc_issues:
                st.subheader("Issues Found:")
                for issue in doc_issues:
                    severity_color = {
                        "High": "🔴",
                        "Medium": "🟡", 
                        "Low": "🟢"
                    }.get(issue.get("severity", ""), "⚪")
                    
                    st.write(f"{severity_color} **{issue.get('severity', 'Unknown')}**: {issue.get('issue', 'No description')}")
                    st.write(f"   💡 *{issue.get('suggestion', 'No suggestion')}*")
                    if issue.get('citations'):
                        st.write(f"   📚 *{', '.join(issue['citations'])}*")
                    st.write("")

    st.markdown("---")

    # ===== PROCESS DETECTION SECTION =====
    st.header("🎯 Process Detection")
    
    # Map document types to processes
    process_candidates = []
    for dtype in doc_types:
        for process_name, doc_list in PROCESS_MAP.items():
            if dtype in doc_list:
                process_candidates.append(process_name)
    
    if process_candidates:
        detected_process = Counter(process_candidates).most_common(1)[0][0]
        confidence = process_candidates.count(detected_process) / len(doc_types) * 100
        
        st.success(f"**Detected Process**: {detected_process} (Confidence: {confidence:.0f}%)")
        
        # Show process mapping details
        with st.expander("Process Detection Details"):
            st.write("**Document Type Mapping:**")
            for dtype in set(doc_types):
                count = doc_types.count(dtype)
                mapped_processes = [proc for proc, docs in PROCESS_MAP.items() if dtype in docs]
                st.write(f"- {dtype} (×{count}): {', '.join(mapped_processes) if mapped_processes else 'No process mapping'}")
    else:
        detected_process = "Unknown"
        st.warning("**Detected Process**: Unknown - No clear process mapping found")

    st.markdown("---")

    # ===== COMPLIANCE CHECKLIST SECTION =====
    st.header("📝 Compliance Checklist")
    
    missing, problematic = verify_checklist(doc_types, detected_process, all_issues)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Required Documents")
        if detected_process in PROCESS_MAP:
            required_docs = PROCESS_MAP[detected_process]
            for doc in required_docs:
                if doc in doc_types:
                    if doc in problematic:
                        st.write(f"🟡 {doc} *(uploaded, has issues)*")
                    else:
                        st.write(f"✅ {doc} *(uploaded, ok)*")
                else:
                    st.write(f"❌ {doc} *(missing)*")
        else:
            st.write("No checklist available for detected process")
    
    with col2:
        st.subheader("⚠️ Status Summary")
        if missing:
            st.error(f"**Missing Documents** ({len(missing)})")
            for doc in missing:
                st.write(f"- {doc}")
        
        if problematic:
            st.warning(f"**Problematic Documents** ({len(problematic)})")
            for doc in problematic:
                st.write(f"- {doc}")
        
        if not missing and not problematic:
            st.success("All required documents present and compliant!")

    st.markdown("---")

    # ===== ISSUES SUMMARY SECTION =====
    st.header("🚨 Issues Summary")
    
    if all_issues:
        # Group issues by severity
        severity_groups = {"High": [], "Medium": [], "Low": []}
        for issue in all_issues:
            severity = issue.get("severity", "Unknown")
            if severity in severity_groups:
                severity_groups[severity].append(issue)
        
        # Display by severity
        for severity, color in [("High", "🔴"), ("Medium", "🟡"), ("Low", "🟢")]:
            issues = severity_groups[severity]
            if issues:
                st.subheader(f"{color} {severity} Severity ({len(issues)} issues)")
                for issue in issues:
                    with st.expander(f"{issue.get('document_type', 'Unknown')} - {issue.get('issue', 'No description')}"):
                        st.write(f"**Document**: {issue.get('document_type', 'Unknown')}")
                        st.write(f"**Section**: {issue.get('section', 'Not specified')}")
                        st.write(f"**Issue**: {issue.get('issue', 'No description')}")
                        st.write(f"**Suggestion**: {issue.get('suggestion', 'No suggestion')}")
                        if issue.get('citations'):
                            st.write(f"**Legal References**: {', '.join(issue['citations'])}")
    else:
        st.success("🎉 No compliance issues detected!")

    st.markdown("---")

    # ===== JSON OUTPUT SECTION =====
    st.header("💾 Structured Analysis Output")
    
    structured_output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "process": detected_process,
        "documents_uploaded": len(doc_types),
        "documents_by_type": dict(Counter(doc_types)),
        "required_documents": len(PROCESS_MAP.get(detected_process, [])),
        "missing_documents": missing,
        "problematic_documents": problematic,
        "total_issues": len(all_issues),
        "issues_by_severity": {
            "High": len([i for i in all_issues if i.get("severity") == "High"]),
            "Medium": len([i for i in all_issues if i.get("severity") == "Medium"]),
            "Low": len([i for i in all_issues if i.get("severity") == "Low"])
        },
        "detailed_issues": [
            {
                "document_type": i.get("document_type", ""),
                "section": i.get("section", ""),
                "issue": i.get("issue", ""),
                "severity": i.get("severity", ""),
                "suggestion": i.get("suggestion", ""),
                "citations": i.get("citations", [])
            }
            for i in all_issues
        ],
        "document_summaries": {
            os.path.basename(path): summary 
            for path, summary in summaries.items()
        }
    }

    # Display JSON in collapsible section
    with st.expander("View JSON Output", expanded=False):
        st.json(structured_output)

    # Download JSON
    json_str = json.dumps(structured_output, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON Analysis",
        data=json_str,
        file_name=f"adgm_analysis_{detected_process.lower().replace(' ', '_')}.json",
        mime="application/json"
    )

    st.markdown("---")

    # ===== REVIEWED DOCUMENTS DOWNLOAD =====
    st.header("📤 Download Reviewed Documents")
    st.write("Download your documents with embedded comments and suggestions:")
    
    for filepath, doc_type in zip(filepaths, doc_types):
        filename = os.path.basename(filepath)
        
        try:
            # Get issues for this specific document
            doc_issues = [issue for issue in all_issues if issue.get("document_type") == doc_type]
            
            # Insert comments and generate reviewed version
            summary_text = summaries.get(filepath, "Summary not available")
            reviewed_path = insert_comments(filepath, doc_issues, summary_text)
            
            # Provide download button
            with open(reviewed_path, "rb") as f:
                st.download_button(
                    label=f"📄 Download {filename} (Reviewed)",
                    data=f.read(),
                    file_name=f"{filename.replace('.docx', '')}_reviewed.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_{i}_{filepath}"  # Unique key for each button
                )
        
        except Exception as e:
            st.error(f"Error preparing reviewed version of {filename}: {str(e)}")

    # Cleanup temporary files
    try:
        for filepath in filepaths:
            if os.path.exists(filepath):
                os.remove(filepath)
            reviewed_path = filepath.replace(".docx", "_reviewed.docx")
            if os.path.exists(reviewed_path):
                os.remove(reviewed_path)
    except:
        pass  # Ignore cleanup errors

if __name__ == "__main__":
    main()