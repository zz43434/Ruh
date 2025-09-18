#!/usr/bin/env python3
"""
Comparison script to demonstrate the improvement of semantic search over keyword matching.
"""

from app.services.verse_service import VerseService

def compare_search_methods():
    """Compare keyword vs semantic search for various queries."""
    verse_service = VerseService()
    
    test_queries = [
        "guidance and wisdom",
        "patience in difficult times", 
        "forgiveness and mercy",
        "seeking knowledge",
        "gratitude to Allah"
    ]
    
    print("🔍 SEARCH METHOD COMPARISON")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)
        
        # Keyword search (old method)
        print("🔤 Keyword Search Results:")
        try:
            keyword_results = verse_service._keyword_search_fallback(query, max_results=3)
            if keyword_results:
                for i, verse in enumerate(keyword_results[:3], 1):
                    print(f"   {i}. Verse {verse['verse_number']}")
                    print(f"      Arabic: {verse['arabic_text'][:50]}...")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Semantic search (new method)
        print("🧠 Semantic Search Results:")
        try:
            semantic_results = verse_service.search_verses_semantic(query, max_results=3)
            if semantic_results:
                for i, (verse, similarity) in enumerate(semantic_results[:3], 1):
                    print(f"   {i}. Verse {verse['verse_number']} (similarity: {similarity:.3f})")
                    print(f"      Arabic: {verse['arabic_text'][:50]}...")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    compare_search_methods()