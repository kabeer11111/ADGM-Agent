import regex as re
from docx import Document
from app.models.llm_client import GeminiClient
from app.rag import (
    retrieve_relevant_passages, 
    get_rag_enhanced_suggestion,
    retrieve_for_compliance_check,
    get_document_requirements,
    check_rag_database_status
)

gemini = GeminiClient()

def get_rag_powered_suggestion(prompt, doc_type, context=""):
    """
    Generate suggestions using comprehensive RAG context
    """
    try:
        # Get RAG context for this specific issue
        rag_context = get_rag_enhanced_suggestion(prompt, doc_type, context)
        
        # Combine with any additional context
        full_context = f"{rag_context}\n\n{context}" if context else rag_context
        
        short_prompt = (
            "Based on ADGM legal requirements, provide a 1-2 sentence suggestion. "
            "Include specific legal references if available.\n\n" + prompt
        )

        response = gemini.ask(short_prompt, full_context)

        if not response or response.startswith(("[No suggestion", "[No response")):
            fallback = f"Review {doc_type} against ADGM requirements: {prompt.strip()}"
            return fallback

        return response.strip()

    except Exception as e:
        return f"Ensure compliance with ADGM laws. (Error: {str(e)[:40]})"

def check_document_against_rag_requirements(doc_type, full_text):
    """
    Use RAG to identify what requirements should be checked for this document type
    """
    requirements_text = get_document_requirements(doc_type)
    
    if "No specific requirements" in requirements_text:
        return []  # No RAG-based requirements found
    
    # Extract requirement keywords from RAG results
    requirement_issues = []
    
    # Common requirement patterns that might be mentioned in RAG results
    requirement_patterns = {
        "signature": r"sign(ed|ature)|execution|witnessed",
        "date": r"date|effective\s+date|commencement", 
        "parties": r"parties|contracting\s+parties",
        "jurisdiction": r"jurisdiction|governing\s+law|ADGM",
        "address": r"address|registered\s+office",
        "termination": r"termination|expiry|end",
        "liability": r"liability|indemnity|damages",
        "confidentiality": r"confidential|non.?disclosure"
    }
    
    for req_name, pattern in requirement_patterns.items():
        if req_name in requirements_text.lower() and not re.search(pattern, full_text, re.I):
            requirement_issues.append(req_name)
    
    return requirement_issues

def red_flags(doc_path, doc_type):
    """
    Enhanced red flag detection using RAG-powered analysis
    """
    
    # Check if RAG database is available
    rag_available, rag_status = check_rag_database_status()
    print(f"RAG Status: {rag_status}")
    
    try:
        doc = Document(doc_path)
        issues = []
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(texts)
        
        if not texts:
            return [{
                "section": "General",
                "issue": "Document appears to be empty or unreadable",
                "severity": "High",
                "suggestion": "Please check the document format and content.",
                "citations": [],
                "document_type": doc_type
            }]

        print(f"Analyzing {doc_type} with {len(texts)} paragraphs (RAG: {'ON' if rag_available else 'OFF'})")

        # === RAG-ENHANCED REQUIREMENT CHECKING ===
        if rag_available:
            rag_missing_requirements = check_document_against_rag_requirements(doc_type, full_text)
            for req in rag_missing_requirements:
                ctx = retrieve_for_compliance_check(doc_type, f"missing {req}", top_k=5)
                combined_ctx = "\n".join(ctx)
                
                issues.append({
                    "section": "General",
                    "issue": f"Missing requirement identified by legal knowledge: {req}",
                    "severity": "Medium",
                    "suggestion": get_rag_powered_suggestion(f"Document missing: {req}", doc_type, combined_ctx),
                    "citations": ["ADGM Legal Knowledge Base"],
                    "document_type": doc_type
                })

        # === JURISDICTION CHECKS (RAG-Enhanced) ===
        corporate_docs = ["Articles of Association", "Memorandum of Association", "Board Resolution", "Shareholder Resolution"]
        
        if doc_type in corporate_docs:
            has_adgm = re.search(r'\bADGM\b', full_text, re.I)
            has_uae_federal = re.search(r'UAE Federal Court|onshore UAE|Dubai Courts|UAE Federal Law', full_text, re.I)
            
            if has_uae_federal or not has_adgm:
                idx = next((i for i, p in enumerate(texts) if re.search(r'jurisdiction|law|court|governed', p, re.I)), 0)
                
                if rag_available:
                    ctx_passages = retrieve_for_compliance_check(doc_type, "jurisdiction ADGM law", top_k=5)
                    ctx = "\n".join(ctx_passages)
                else:
                    ctx = "ADGM jurisdiction required for corporate documents"
                
                prompt = f"Jurisdiction issue in {doc_type}. Text: {texts[idx] if idx < len(texts) else 'Not found'}"
                
                issues.append({
                    "section": f"Paragraph {idx+1}",
                    "issue": "Jurisdiction not specific to ADGM or references UAE Federal law",
                    "severity": "High",
                    "suggestion": get_rag_powered_suggestion(prompt, doc_type, ctx),
                    "citations": ["Companies Regulations 2020 s.6–12"],
                    "document_type": doc_type
                })

        # === UBO DECLARATION CHECKS (RAG-Enhanced) ===
        if doc_type == "UBO Declaration":
            required_fields = [
                ("full name", r"(?:full\s+)?name"),
                ("date of birth", r"(?:date\s+of\s+)?birth|DOB|born"),
                ("nationality", r"nationality|citizen"),
                ("passport", r"passport|ID\s+number"),
                ("address", r"address|residence")
            ]
            
            for field_name, pattern in required_fields:
                if not re.search(pattern, full_text, re.I):
                    if rag_available:
                        ctx_passages = retrieve_for_compliance_check(doc_type, f"UBO {field_name} requirements", top_k=3)
                        ctx = "\n".join(ctx_passages)
                    else:
                        ctx = f"UBO declarations must include {field_name}"
                    
                    prompt = f"UBO declaration missing: {field_name}."
                    issues.append({
                        "section": "General",
                        "issue": f"Missing UBO field: {field_name}",
                        "severity": "High",
                        "suggestion": get_rag_powered_suggestion(prompt, doc_type, ctx),
                        "citations": ["Beneficial Ownership & Control Regulations 2022"],
                        "document_type": doc_type
                    })

        # === EMPLOYMENT CONTRACT CHECKS (RAG-Enhanced) ===
        if doc_type == "Employment Contract":
            employment_requirements = [
                ("job title/position", r"(?:job\s+)?(?:title|position|role)"),
                ("salary/compensation", r"salary|wage|compensation|remuneration|pay"),
                ("working hours", r"working\s+hours|work\s+schedule|hours\s+of\s+work"),
                ("probation period", r"probation|trial\s+period"),
                ("termination clause", r"termination|dismiss|notice\s+period"),
                ("leave entitlement", r"leave|holiday|vacation|sick\s+leave|annual\s+leave")
            ]
            
            for req_name, pattern in employment_requirements:
                if not re.search(pattern, full_text, re.I):
                    if rag_available:
                        ctx_passages = retrieve_for_compliance_check(doc_type, f"employment {req_name} ADGM requirements", top_k=4)
                        ctx = "\n".join(ctx_passages)
                    else:
                        ctx = f"Employment contracts must specify {req_name}"
                    
                    prompt = f"Employment contract missing: {req_name}."
                    issues.append({
                        "section": "General",
                        "issue": f"Missing {req_name}",
                        "severity": "Medium",
                        "suggestion": get_rag_powered_suggestion(prompt, doc_type, ctx),
                        "citations": ["Employment Regulations 2019"],
                        "document_type": doc_type
                    })

        # === UNIVERSAL SIGNATURE CHECK (RAG-Enhanced) ===
        signature_patterns = [
            r"sign(ed|ature)", r"date:?\s*[_\s]{3,}", r"executed\s+on", r"witness"
        ]
        
        has_signature = any(
            re.search(pattern, text, re.I) 
            for text in texts 
            for pattern in signature_patterns
        )
        
        if not has_signature:
            if rag_available:
                ctx_passages = retrieve_for_compliance_check(doc_type, "signature execution requirements", top_k=3)
                ctx = "\n".join(ctx_passages)
            else:
                ctx = "Documents must be properly executed with signatures"
            
            issues.append({
                "section": "End of Document",
                "issue": "Missing signature block or execution clause",
                "severity": "Medium" if doc_type in ["Employment Contract", "Commercial Agreement"] else "Low",
                "suggestion": get_rag_powered_suggestion("Missing signature block", doc_type, ctx),
                "citations": ["Companies Regulations 2020"],
                "document_type": doc_type
            })

        print(f"Found {len(issues)} issues for {doc_type} (RAG-enhanced: {rag_available})")
        return issues

    except Exception as e:
        print(f"Error analyzing {doc_path}: {e}")
        return [{
            "section": "General",
            "issue": f"Error analyzing document: {str(e)[:100]}",
            "severity": "High",
            "suggestion": "Please check document format and try again.",
            "citations": [],
            "document_type": doc_type
        }]