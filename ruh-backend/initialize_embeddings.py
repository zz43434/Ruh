#!/usr/bin/env python3
"""
Initialization script to generate embeddings for all Quranic verses.
This script should be run once to create the initial embeddings database.

Usage:
    python initialize_embeddings.py [--force] [--model MODEL_NAME]
    
Options:
    --force: Force regeneration of embeddings even if they already exist
    --model: Specify the embedding model to use (default: paraphrase-multilingual-MiniLM-L12-v2)
"""

import sys
import os
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.verse_service import VerseService
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStoreManager


def main():
    parser = argparse.ArgumentParser(description='Initialize verse embeddings for RAG system')
    parser.add_argument('--force', action='store_true', 
                       help='Force regeneration of embeddings even if they already exist')
    parser.add_argument('--model', type=str, 
                       default='paraphrase-multilingual-MiniLM-L12-v2',
                       help='Embedding model to use')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for processing verses')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    print("🚀 Initializing Quranic Verse Embeddings for RAG System")
    print("=" * 60)
    
    try:
        # Initialize services
        print("📚 Loading verse data...")
        verse_service = VerseService()
        
        # Check if we have verses
        all_verses = verse_service.get_all_verses()
        if not all_verses:
            print("❌ Error: No verses found in the database")
            return 1
        
        print(f"✅ Loaded {len(all_verses)} verses")
        
        # Initialize embedding service with specified model
        print(f"🤖 Initializing embedding model: {args.model}")
        embedding_service = EmbeddingService(model_name=args.model)
        
        # Check if embeddings already exist
        embeddings_exist = embedding_service.load_verse_embeddings()
        
        if embeddings_exist and not args.force:
            print("✅ Embeddings already exist!")
            stats = embedding_service.get_embedding_stats()
            print(f"   - Number of verses: {stats.get('num_verses', 'Unknown')}")
            print(f"   - Model: {stats.get('model_name', 'Unknown')}")
            print(f"   - Embedding dimension: {stats.get('embedding_dimension', 'Unknown')}")
            print("\n💡 Use --force flag to regenerate embeddings")
            return 0
        
        if args.force and embeddings_exist:
            print("🔄 Force flag detected. Regenerating embeddings...")
        
        # Create embeddings
        print("🔧 Creating embeddings...")
        print("   This may take several minutes depending on the number of verses...")
        
        embedding_service.create_verse_embeddings(all_verses)
        
        # Initialize vector store and save embeddings there too
        print("💾 Saving to vector store...")
        vector_store_manager = VectorStoreManager()
        verse_store = vector_store_manager.get_store("verses")
        
        # Add vectors to store
        vectors = embedding_service.verse_embeddings
        metadata = embedding_service.verse_metadata
        
        if vectors is not None and metadata:
            # Clear existing data if force regeneration
            if args.force:
                verse_store.clear()
            
            # Generate IDs for verses
            ids = [f"verse_{meta['verse_number']}" for meta in metadata]
            
            # Add to vector store
            verse_store.add_vectors(vectors, metadata, ids)
            verse_store.save()
            
            print("✅ Successfully saved embeddings to vector store")
        
        # Display final statistics
        print("\n📊 Embedding Statistics:")
        print("-" * 30)
        
        stats = embedding_service.get_embedding_stats()
        print(f"✅ Status: {stats.get('status', 'Unknown')}")
        print(f"📖 Number of verses: {stats.get('num_verses', 'Unknown')}")
        print(f"🤖 Model: {stats.get('model_name', 'Unknown')}")
        print(f"📏 Embedding dimension: {stats.get('embedding_dimension', 'Unknown')}")
        
        vector_stats = verse_store.get_stats()
        print(f"💾 Vector store size: {vector_stats.get('num_vectors', 'Unknown')} vectors")
        print(f"💽 Memory usage: {vector_stats.get('memory_usage_mb', 0):.2f} MB")
        
        # Test the system with a sample query
        print("\n🧪 Testing the system...")
        test_queries = [
            "guidance and wisdom",
            "patience and perseverance", 
            "forgiveness and mercy"
        ]
        
        for query in test_queries:
            try:
                results = embedding_service.find_similar_verses(query, top_k=2, min_similarity=0.1)
                print(f"   Query: '{query}' -> Found {len(results)} similar verses")
                if args.verbose and results:
                    for i, (verse_data, score) in enumerate(results[:1]):
                        print(f"      {i+1}. {verse_data.get('verse_number', 'Unknown')} "
                              f"(similarity: {score:.3f})")
            except Exception as e:
                print(f"   ❌ Error testing query '{query}': {e}")
        
        print("\n🎉 Initialization completed successfully!")
        print("   The RAG system is now ready to use.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Initialization interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import sentence_transformers
        import numpy
        import sklearn
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("   pip install sentence-transformers numpy scikit-learn")
        return False


if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    exit_code = main()
    sys.exit(exit_code)