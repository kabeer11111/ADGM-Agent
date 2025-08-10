# rag.py
import chromadb
from sentence_transformers import SentenceTransformer
import os

# Create persistent client with a specific path
DB_PATH = "./chroma_db"
client = chromadb.PersistentClient(path=DB_PATH)
db = client.get_or_create_collection("adgm_laws")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_relevant_passages(query_text, top_k=10):
    """
    Retrieve relevant legal passages for a given query
    Increased default top_k for more comprehensive context
    """
    try:
        query_embedding = embed_model.encode([query_text])[0]
        results = db.query(query_embeddings=[query_embedding], n_results=top_k)
        documents = results.get('documents', [[]])[0]
        
        # Log what was retrieved for debugging
        print(f"RAG Query: '{query_text}' -> Retrieved {len(documents)} passages")
        
        return documents
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return []

def retrieve_for_document_type(doc_content, top_k=5):
    """
    Use RAG to help identify document type based on legal content
    """
    query = f"document type classification legal requirements {doc_content[:200]}"
    return retrieve_relevant_passages(query, top_k)

def retrieve_for_compliance_check(doc_type, section_content, top_k=8):
    """
    Retrieve relevant compliance requirements for specific document type and content
    """
    query = f"{doc_type} compliance requirements {section_content[:150]}"
    return retrieve_relevant_passages(query, top_k)

def retrieve_for_summary_context(doc_type, key_terms, top_k=6):
    """
    Retrieve context for document summarization
    """
    query = f"{doc_type} purpose requirements {' '.join(key_terms[:10])}"
    return retrieve_relevant_passages(query, top_k)

def get_rag_enhanced_suggestion(issue_description, doc_type, section_content=""):
    """
    Generate suggestions using comprehensive RAG context
    """
    # Multiple targeted queries for comprehensive context
    queries = [
        f"{doc_type} {issue_description}",
        f"ADGM compliance {issue_description}",
        f"{doc_type} requirements standard clauses"
    ]
    
    all_context = []
    for query in queries:
        context = retrieve_relevant_passages(query, top_k=5)
        all_context.extend(context)
    
    # Remove duplicates and combine
    unique_context = list(set(all_context))
    combined_context = "\n".join(unique_context[:15])  # Limit to avoid token limits
    
    return combined_context

def check_rag_database_status():
    """
    Check if RAG database has been populated - FIXED VERSION
    """
    try:
        # First check if database directory exists
        if not os.path.exists(DB_PATH):
            return False, f"RAG database directory {DB_PATH} does not exist"
        
        # Try to count documents
        try:
            count = db.count()
            if count > 0:
                return True, f"RAG database active with {count} documents"
        except Exception as count_error:
            print(f"Count method error: {count_error}")
        
        # Fallback: try peek method
        try:
            peek_result = db.peek(limit=1)
            if peek_result and peek_result.get('documents') and len(peek_result['documents']) > 0:
                return True, f"RAG database active with content"
        except Exception as peek_error:
            print(f"Peek method error: {peek_error}")
        
        # If we get here, database exists but is empty
        return False, "RAG database exists but is empty - run ingest.py to populate"
        
    except Exception as e:
        return False, f"RAG database error: {e}"

def get_document_requirements(doc_type):
    """
    Use RAG to find specific requirements for document types
    """
    query = f"{doc_type} mandatory requirements essential clauses ADGM"
    requirements = retrieve_relevant_passages(query, top_k=8)
    
    if requirements:
        return "\n".join(requirements[:5])  # Top 5 most relevant
    else:
        return f"No specific requirements found in knowledge base for {doc_type}"

def debug_rag_database():
    """Debug function to check what's in the RAG database"""
    try:
        print("=== RAG Database Debug ===")
        print(f"Database path: {DB_PATH}")
        print(f"Path exists: {os.path.exists(DB_PATH)}")
        
        # Method 1: Try count
        try:
            count = db.count()
            print(f"Document count: {count}")
        except Exception as e:
            print(f"Count method failed: {e}")
        
        # Method 2: Try peek
        try:
            peek_result = db.peek(limit=3)
            print(f"Peek result structure: {type(peek_result)}")
            print(f"Peek keys: {peek_result.keys() if hasattr(peek_result, 'keys') else 'No keys'}")
            if 'documents' in peek_result:
                print(f"Documents found: {len(peek_result['documents'])}")
                if peek_result['documents']:
                    print(f"First doc preview: {peek_result['documents'][0][:100]}...")
        except Exception as e:
            print(f"Peek method failed: {e}")
        
        # Method 3: Try query
        try:
            query_result = db.query(query_texts=["ADGM company"], n_results=2)
            print(f"Query result structure: {type(query_result)}")
            print(f"Query keys: {query_result.keys() if hasattr(query_result, 'keys') else 'No keys'}")
            if 'documents' in query_result:
                docs = query_result['documents']
                print(f"Query documents: {len(docs)} lists")
                if docs and docs[0]:
                    print(f"First query result: {docs[0][0][:100] if docs[0] else 'Empty'}...")
        except Exception as e:
            print(f"Query method failed: {e}")
            
    except Exception as e:
        print(f"Debug failed: {e}")

if __name__ == "__main__":
    debug_rag_database()