#!/usr/bin/env python3
"""
Sprint 2 - M3: Test Retrieval Quality
Test embedding và retrieval để verify quality.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_retrieval():
    """Test retrieval quality với các queries khác nhau"""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        print("ERROR: chromadb chưa cài. pip install -r requirements.txt")
        return False
    
    ROOT = Path(__file__).resolve().parent
    db_path = os.environ.get("CHROMA_DB_PATH", str(ROOT / "chroma_db"))
    collection_name = os.environ.get("CHROMA_COLLECTION", "day10_kb")
    model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    print(f"=== Sprint 2 - M3: Retrieval Quality Test ===")
    print(f"ChromaDB path: {db_path}")
    print(f"Collection: {collection_name}")
    print(f"Model: {model_name}")
    print()
    
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=db_path)
    emb = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    try:
        col = client.get_collection(name=collection_name, embedding_function=emb)
    except Exception as e:
        print(f"ERROR: Collection not found: {e}")
        return False
    
    # Get collection stats
    count = col.count()
    print(f"✅ Collection loaded: {count} vectors")
    print()
    
    # Test queries
    test_queries = [
        {
            "query": "chính sách hoàn tiền",
            "expected_doc": "policy_refund_v4",
            "description": "Query về refund policy"
        },
        {
            "query": "SLA ticket P1",
            "expected_doc": "sla_p1_2026",
            "description": "Query về SLA"
        },
        {
            "query": "tài khoản bị khóa",
            "expected_doc": "it_helpdesk_faq",
            "description": "Query về IT helpdesk"
        },
        {
            "query": "ngày phép năm",
            "expected_doc": "hr_leave_policy",
            "description": "Query về HR leave policy"
        }
    ]
    
    results_summary = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"--- Test {i}: {test['description']} ---")
        print(f"Query: '{test['query']}'")
        print(f"Expected doc_id: {test['expected_doc']}")
        
        # Perform retrieval
        results = col.query(
            query_texts=[test['query']],
            n_results=3,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Check results
        if results['ids'] and len(results['ids'][0]) > 0:
            top_result = results['ids'][0][0]
            top_doc_id = results['metadatas'][0][0].get('doc_id', 'unknown')
            top_distance = results['distances'][0][0]
            top_text = results['documents'][0][0][:100] + "..."
            
            passed = top_doc_id == test['expected_doc']
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"Top result: {top_result}")
            print(f"  doc_id: {top_doc_id}")
            print(f"  distance: {top_distance:.4f}")
            print(f"  text: {top_text}")
            print(f"Status: {status}")
            
            results_summary.append({
                'test': test['description'],
                'passed': passed,
                'top_doc_id': top_doc_id,
                'expected': test['expected_doc']
            })
        else:
            print("❌ FAIL: No results returned")
            results_summary.append({
                'test': test['description'],
                'passed': False,
                'top_doc_id': 'none',
                'expected': test['expected_doc']
            })
        
        print()
    
    # Summary
    print("=== Summary ===")
    passed_count = sum(1 for r in results_summary if r['passed'])
    total_count = len(results_summary)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"Passed: {passed_count}/{total_count} ({pass_rate:.1f}%)")
    print()
    
    for r in results_summary:
        status = "✅" if r['passed'] else "❌"
        print(f"{status} {r['test']}: got '{r['top_doc_id']}', expected '{r['expected']}'")
    
    print()
    print(f"=== Idempotency Check ===")
    print(f"Total vectors in collection: {count}")
    print(f"Expected: 6 vectors (from cleaned data)")
    idempotent = count == 6
    print(f"Idempotency: {'✅ PASS' if idempotent else '❌ FAIL'}")
    
    return passed_count == total_count and idempotent


if __name__ == "__main__":
    success = test_retrieval()
    exit(0 if success else 1)
