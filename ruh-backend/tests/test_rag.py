#!/usr/bin/env python3
"""
Test script to compare old keyword matching vs new RAG-based semantic search
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.verse_service import VerseService

def test_queries():
    """Test various queries to compare semantic vs keyword search"""
    
    # Initialize verse service
    verse_service = VerseService()
    
    test_queries = [
        "guidance and wisdom",
        "patience in difficult times", 
        "forgiveness and mercy",
        "prayer and worship",
        "charity and helping others",
        "trust in Allah",
        "seeking knowledge",
        "gratitude and thankfulness"
    ]
    
    print("🧪 Testing RAG-based Semantic Search vs Keyword Matching")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)
        
        try:
            # Test semantic search
            semantic_results = verse_service.search_verses_semantic(
                query, 
                max_results=3, 
                min_similarity=0.2
            )
            
            print(f"🔍 Semantic Search Results ({len(semantic_results)} found):")
            for i, (verse, similarity) in enumerate(semantic_results, 1):
                verse_num = verse.get('verse_number', 'Unknown')
                arabic = verse.get('arabic_text', '')[:50] + "..." if len(verse.get('arabic_text', '')) > 50 else verse.get('arabic_text', '')
                translation = verse.get('translation', '')[:80] + "..." if len(verse.get('translation', '')) > 80 else verse.get('translation', '')
                
                print(f"   {i}. Verse {verse_num} (similarity: {similarity:.3f})")
                print(f"      Arabic: {arabic}")
                print(f"      Translation: {translation}")
                print()
            
            if not semantic_results:
                print("   No results found with semantic search")
                
        except Exception as e:
            print(f"   ❌ Error in semantic search: {e}")
        
        print()
    
    # Test embedding statistics
    print("\n📊 System Statistics:")
    print("-" * 30)
    try:
        stats = verse_service.get_embedding_stats()
        embedding_stats = stats.get('embedding_service', {})
        vector_stats = stats.get('vector_store', {})
        
        print(f"✅ Status: {embedding_stats.get('status', 'Unknown')}")
        print(f"📖 Number of verses: {embedding_stats.get('num_verses', 'Unknown')}")
        print(f"🤖 Model: {embedding_stats.get('model_name', 'Unknown')}")
        print(f"📏 Embedding dimension: {embedding_stats.get('embedding_dimension', 'Unknown')}")
        print(f"💾 Vector store size: {vector_stats.get('num_vectors', 'Unknown')} vectors")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")


def test_specific_verse_retrieval():
    """Test retrieving specific verses to ensure the system works"""
    
    verse_service = VerseService()
    
    print("\n🔍 Testing Specific Verse Retrieval:")
    print("-" * 40)
    
    try:
        # Test getting a specific verse
        verse = verse_service.get_verse(1, 1)  # Al-Fatiha, verse 1
        if verse:
            print(f"✅ Retrieved verse 1:1")
            print(f"   Arabic: {verse.get('arabic_text', 'N/A')}")
            print(f"   Translation: {verse.get('translation', 'N/A')}")
        else:
            print("❌ Could not retrieve verse 1:1")
            
        # Test getting random verse
        random_verse = verse_service.get_random_verse()
        if random_verse:
            print(f"✅ Retrieved random verse: {random_verse.get('verse_number', 'Unknown')}")
        else:
            print("❌ Could not retrieve random verse")
            
    except Exception as e:
        print(f"❌ Error in verse retrieval: {e}")


if __name__ == "__main__":
    print("🚀 Starting RAG System Tests")
    print("=" * 50)
    
    try:
        test_specific_verse_retrieval()
        test_queries()
        
        print("\n🎉 Testing completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()