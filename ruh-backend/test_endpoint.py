#!/usr/bin/env python3
"""
Simple test script to verify the optimized chapter details endpoint performance.
This bypasses database initialization to focus on testing the VerseService optimizations.
"""

import time
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.verse_service import VerseService

def test_chapter_performance():
    """Test the performance of the optimized chapter details endpoint."""
    
    print("Testing optimized chapter details endpoint...")
    print("=" * 50)
    
    # Test 1: Basic chapter loading without translations (should be fast)
    print("\n1. Testing chapter loading WITHOUT translations:")
    start_time = time.time()
    
    verse_service = VerseService()
    chapter = verse_service.get_chapter_with_verses(
        surah_number=1, 
        include_summary=False, 
        include_translations=False
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if chapter:
        print(f"✅ Success! Chapter loaded in {duration:.3f} seconds")
        print(f"   Chapter: {chapter['name']}")
        print(f"   Verses count: {len(chapter['verses'])}")
        print(f"   Has translations: {'translation' in chapter['verses'][0] if chapter['verses'] else 'N/A'}")
    else:
        print("❌ Failed to load chapter")
    
    # Test 2: Chapter loading with translations (should still be reasonably fast)
    print("\n2. Testing chapter loading WITH translations:")
    start_time = time.time()
    
    chapter_with_translations = verse_service.get_chapter_with_verses(
        surah_number=1, 
        include_summary=False, 
        include_translations=True
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if chapter_with_translations:
        print(f"✅ Success! Chapter with translations loaded in {duration:.3f} seconds")
        print(f"   Chapter: {chapter_with_translations['name']}")
        print(f"   Verses count: {len(chapter_with_translations['verses'])}")
        print(f"   Has translations: {'translation' in chapter_with_translations['verses'][0] if chapter_with_translations['verses'] else 'N/A'}")
    else:
        print("❌ Failed to load chapter with translations")
    
    # Test 3: Chapter loading with summary (should be slower due to AI generation)
    print("\n3. Testing chapter loading WITH summary:")
    start_time = time.time()
    
    chapter_with_summary = verse_service.get_chapter_with_verses(
        surah_number=1, 
        include_summary=True, 
        include_translations=False
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if chapter_with_summary:
        print(f"✅ Success! Chapter with summary loaded in {duration:.3f} seconds")
        print(f"   Chapter: {chapter_with_summary['name']}")
        print(f"   Has summary: {'summary' in chapter_with_summary}")
        if 'summary' in chapter_with_summary:
            print(f"   Summary preview: {chapter_with_summary['summary'][:100]}...")
    else:
        print("❌ Failed to load chapter with summary")
    
    print("\n" + "=" * 50)
    print("Performance test completed!")
    
    # Test service initialization performance
    print("\n4. Testing service initialization performance:")
    start_time = time.time()
    
    # Create a new instance (should use singleton)
    new_service = VerseService()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Service initialization took {duration:.3f} seconds")
    print(f"   Same instance: {new_service is verse_service}")

if __name__ == "__main__":
    test_chapter_performance()