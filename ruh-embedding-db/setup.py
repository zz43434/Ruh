#!/usr/bin/env python3
"""
Setup script for embedding Quran data from JSON files.
This script merges datasets by surah number, flattens the data structure,
generates embeddings using sentence-transformers, and injects data into Qdrant.
If embeddings already exist, it will skip generation and directly inject data into Qdrant.
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple, Optional
import logging
import time
from collections import defaultdict
import sys

# Import Qdrant client for vector database operations
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: qdrant-client not installed. Will not be able to inject data into Qdrant.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Model configuration
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"  # Fast and efficient model for semantic search

# Qdrant configuration
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
COLLECTION_NAME = "quran_embeddings"


def load_json_file(file_path: str) -> Any:
    """Load JSON data from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return None


def check_embeddings_exist() -> bool:
    """
    Check if embeddings have already been generated.
    
    Returns:
        bool: True if all required embedding files exist, False otherwise
    """
    required_files = [
        os.path.join(OUTPUT_DIR, "embeddings.npy"),
        os.path.join(OUTPUT_DIR, "flattened_items.json"),
        os.path.join(OUTPUT_DIR, "qdrant_data.json"),
        os.path.join(OUTPUT_DIR, "metadata.json")
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.info(f"Missing required file: {file_path}")
            return False
    
    logger.info("All embedding files already exist")
    return True


def inject_data_into_qdrant(payload_list: List[Dict], vector_list: List[List[float]]) -> bool:
    """
    Inject data into Qdrant vector database.
    
    Args:
        payload_list: List of payload dictionaries
        vector_list: List of vector embeddings
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not QDRANT_AVAILABLE:
        logger.error("Qdrant client not available. Cannot inject data.")
        return False
    
    try:
        logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        vector_size = len(vector_list[0]) if vector_list else 0
        if not vector_size:
            logger.error("No vectors to inject")
            return False
        
        # Create collection if it doesn't exist
        if COLLECTION_NAME not in collection_names:
            logger.info(f"Creating collection: {COLLECTION_NAME}")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
        else:
            logger.info(f"Collection {COLLECTION_NAME} already exists")
        
        # Prepare points for upsert
        points = []
        for i, (payload, vector) in enumerate(zip(payload_list, vector_list)):
            # Use the item's id if available, otherwise generate one
            point_id = payload.get("id", f"point_{i}")
            if isinstance(point_id, str) and point_id.isdigit():
                point_id = int(point_id)
            elif isinstance(point_id, str):
                # Hash the string ID to get a numeric ID
                point_id = hash(point_id) % (2**63)
            
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
        
        # Upsert in batches to avoid memory issues
        batch_size = 100
        total_points = len(points)
        
        for i in range(0, total_points, batch_size):
            batch = points[i:i+batch_size]
            logger.info(f"Upserting batch {i//batch_size + 1}/{(total_points-1)//batch_size + 1} ({len(batch)} points)")
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
        
        logger.info(f"Successfully injected {total_points} points into Qdrant")
        return True
        
    except Exception as e:
        logger.error(f"Error injecting data into Qdrant: {str(e)}")
        return False


def merge_datasets(verses_data: List[Dict], analysis_data: List[Dict]) -> Dict[int, Dict]:
    """
    Merge Quran verses and surah analysis data by surah number.
    
    Returns a dictionary with surah_number as key and merged data as value.
    """
    logger.info("Merging datasets by surah number")
    
    # Create a dictionary to store merged data by surah number
    merged_data = {}
    
    # Process verses data
    for surah in verses_data:
        surah_number = surah.get("surah_number")
        if surah_number is None:
            continue
        
        merged_data[surah_number] = {
            "surah_number": surah_number,
            "name": surah.get("name", ""),
            "ayah_count": surah.get("ayah_count", 0),
            "revelation_place": surah.get("revelation_place", ""),
            "verses": surah.get("verses", []),
            "analyses": {
                "summary": "",
                "summary_themes": [],
                "summary_sentiment": "",
                "chunks": []
            }
        }
    
    # Process analysis data and merge with verses
    for analysis in analysis_data:
        surah_number = analysis.get("surah_number")
        if surah_number is None or surah_number not in merged_data:
            continue
        
        merged_data[surah_number]["analyses"] = {
            "summary": analysis.get("summary_analysis", ""),
            "summary_themes": analysis.get("summary_themes", []),
            "summary_sentiment": analysis.get("summary_sentiment", ""),
            "chunks": analysis.get("chunk_analyses", [])
        }
    
    logger.info(f"Merged data for {len(merged_data)} surahs")
    return merged_data


def flatten_merged_data(merged_data: Dict[int, Dict]) -> List[Dict]:
    """
    Flatten the merged data structure into a list of items for embedding.
    
    Each item represents either a verse or an analysis chunk with all relevant context.
    """
    flattened_items = []
    
    for surah_number, surah_data in merged_data.items():
        surah_name = surah_data.get("name", "")
        revelation_place = surah_data.get("revelation_place", "")
        
        # Process verses
        for verse in surah_data.get("verses", []):
            verse_number = verse.get("verse_number", "")
            arabic_text = verse.get("arabic_text", "")
            
            # Find relevant analysis chunks for this verse
            relevant_analyses = []
            for chunk in surah_data.get("analyses", {}).get("chunks", []):
                verse_range = chunk.get("verse_range", "")
                if verse_range and verse_number in verse_range:
                    relevant_analyses.append(chunk.get("analysis", ""))
            
            # Create rich text for embedding that combines all available information
            analysis_text = " ".join(relevant_analyses)
            summary = surah_data.get("analyses", {}).get("summary", "")
            themes = ", ".join(surah_data.get("analyses", {}).get("summary_themes", []))
            
            text_for_embedding = (
                f"Surah {surah_name} ({surah_number}) verse {verse_number}, "
                f"revealed in {revelation_place}: {arabic_text}. "
            )
            
            if analysis_text:
                text_for_embedding += f"Analysis: {analysis_text}. "
            
            if summary:
                text_for_embedding += f"Surah summary: {summary}. "
            
            if themes:
                text_for_embedding += f"Themes: {themes}."
            
            flattened_item = {
                "id": f"verse_{verse_number}",
                "type": "verse",
                "verse_id": verse_number,
                "arabic_text": arabic_text,
                "surah_number": surah_number,
                "surah_name": surah_name,
                "revelation_place": revelation_place,
                "analysis": analysis_text if analysis_text else None,
                "surah_summary": summary if summary else None,
                "themes": themes if themes else None,
                "text_for_embedding": text_for_embedding
            }
            
            flattened_items.append(flattened_item)
        
        # Add surah-level item with summary
        summary = surah_data.get("analyses", {}).get("summary", "")
        if summary:
            themes = ", ".join(surah_data.get("analyses", {}).get("summary_themes", []))
            sentiment = surah_data.get("analyses", {}).get("summary_sentiment", "")
            
            text_for_embedding = (
                f"Complete analysis of Surah {surah_name} ({surah_number}), "
                f"revealed in {revelation_place}. "
                f"Summary: {summary}. "
            )
            
            if themes:
                text_for_embedding += f"Themes: {themes}. "
            
            if sentiment:
                text_for_embedding += f"Sentiment: {sentiment}."
            
            flattened_item = {
                "id": f"surah_{surah_number}",
                "type": "surah",
                "surah_number": surah_number,
                "surah_name": surah_name,
                "revelation_place": revelation_place,
                "summary": summary,
                "themes": themes if themes else None,
                "sentiment": sentiment if sentiment else None,
                "text_for_embedding": text_for_embedding
            }
            
            flattened_items.append(flattened_item)
    
    logger.info(f"Flattened data into {len(flattened_items)} items")
    return flattened_items


def generate_embeddings(texts: List[str], model_name: str = MODEL_NAME) -> np.ndarray:
    """Generate embeddings for a list of texts using sentence-transformers."""
    logger.info(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    logger.info(f"Generating embeddings for {len(texts)} texts")
    start_time = time.time()
    embeddings = model.encode(texts, show_progress_bar=True)
    elapsed_time = time.time() - start_time
    
    logger.info(f"Embeddings generated in {elapsed_time:.2f} seconds")
    return embeddings


def save_to_json(data: Any, file_path: str) -> None:
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Data saved to {file_path}")


def save_embeddings(embeddings: np.ndarray, file_path: str) -> None:
    """Save embeddings to a numpy file."""
    np.save(file_path, embeddings)
    logger.info(f"Embeddings saved to {file_path}")


def create_qdrant_compatible_data(flattened_items: List[Dict], embeddings: np.ndarray) -> Tuple[List[Dict], List[Dict]]:
    """
    Create Qdrant-compatible payload and vectors.
    
    Returns:
        Tuple of (payload_list, vector_list)
    """
    payload_list = []
    vector_list = []
    
    for i, item in enumerate(flattened_items):
        # Create payload without the text_for_embedding field to save space
        payload = {k: v for k, v in item.items() if k != 'text_for_embedding'}
        
        payload_list.append(payload)
        vector_list.append(embeddings[i].tolist())
    
    return payload_list, vector_list


def main():
    """Main function to process data and generate embeddings."""
    logger.info("Starting embedding process")
    
    # Check if embeddings already exist
    if check_embeddings_exist():
        logger.info("Embeddings already exist, skipping generation")
        
        # Load existing Qdrant-compatible data
        qdrant_data_file = os.path.join(OUTPUT_DIR, "qdrant_data.json")
        qdrant_data = load_json_file(qdrant_data_file)
        
        if qdrant_data:
            logger.info("Loaded existing Qdrant data, injecting into Qdrant")
            payload_list = qdrant_data.get("payload", [])
            vector_list = qdrant_data.get("vectors", [])
            
            # Inject data into Qdrant
            if inject_data_into_qdrant(payload_list, vector_list):
                logger.info("Successfully injected existing data into Qdrant")
            else:
                logger.error("Failed to inject data into Qdrant")
        else:
            logger.error("Failed to load existing Qdrant data")
        
        return
    
    # If embeddings don't exist, generate them
    logger.info("Generating new embeddings")
    
    # Load Quran verses
    verses_file = os.path.join(DATA_DIR, "quran_verses.json")
    verses_data = load_json_file(verses_file)
    if not verses_data:
        logger.error("Failed to load Quran verses data")
        return
    
    # Load Surah analysis
    analysis_file = os.path.join(DATA_DIR, "surah_analysis.json")
    analysis_data = load_json_file(analysis_file)
    if not analysis_data:
        logger.warning("Failed to load Surah analysis data, using only verses data")
        analysis_data = []
    
    # Merge datasets by surah number
    merged_data = merge_datasets(verses_data, analysis_data)
    
    # Save merged data
    merged_data_file = os.path.join(OUTPUT_DIR, "merged_data.json")
    save_to_json(merged_data, merged_data_file)
    
    # Flatten merged data for embedding
    flattened_items = flatten_merged_data(merged_data)
    
    # Save flattened items
    flattened_items_file = os.path.join(OUTPUT_DIR, "flattened_items.json")
    save_to_json(flattened_items, flattened_items_file)
    
    # Generate embeddings
    texts = [item["text_for_embedding"] for item in flattened_items]
    embeddings = generate_embeddings(texts)
    
    # Save embeddings
    embeddings_file = os.path.join(OUTPUT_DIR, "embeddings.npy")
    save_embeddings(embeddings, embeddings_file)
    
    # Create Qdrant-compatible data
    payload_list, vector_list = create_qdrant_compatible_data(flattened_items, embeddings)
    
    # Save Qdrant-compatible data
    qdrant_data = {
        "payload": payload_list,
        "vectors": vector_list
    }
    qdrant_data_file = os.path.join(OUTPUT_DIR, "qdrant_data.json")
    save_to_json(qdrant_data, qdrant_data_file)
    
    # Create metadata file
    metadata = {
        "total_items": len(flattened_items),
        "verse_items": sum(1 for item in flattened_items if item["type"] == "verse"),
        "surah_items": sum(1 for item in flattened_items if item["type"] == "surah"),
        "embedding_dim": embeddings.shape[1] if len(embeddings) > 0 else 0,
        "model": MODEL_NAME,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    metadata_file = os.path.join(OUTPUT_DIR, "metadata.json")
    save_to_json(metadata, metadata_file)
    
    # Inject data into Qdrant
    if inject_data_into_qdrant(payload_list, vector_list):
        logger.info("Successfully injected data into Qdrant")
    else:
        logger.error("Failed to inject data into Qdrant")
    
    logger.info("Embedding process completed successfully")


if __name__ == "__main__":
    main()