#!/usr/bin/env python3
"""
Script to query the Qdrant database and return the first item.
"""

import os
import json
import requests

# Qdrant configuration
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
COLLECTION_NAME = "quran_embeddings"

def query_first_item():
    """Query Qdrant using REST API and return the first item."""
    try:
        # Use Qdrant REST API directly
        url = f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points/scroll"
        
        print(f"Connecting to Qdrant at {url}")
        
        # Request parameters
        params = {
            "limit": 1,
            "with_payload": True,
            "with_vector": False  # Vector can be large, skip it
        }
        
        # Make the request
        response = requests.post(url, json=params)
        
        if response.status_code == 200:
            data = response.json()
            if data and "result" in data and "points" in data["result"] and len(data["result"]["points"]) > 0:
                first_point = data["result"]["points"][0]
                return {
                    "id": first_point.get("id"),
                    "payload": first_point.get("payload", {})
                }
            else:
                print("No points found in the collection")
                return None
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error querying Qdrant: {str(e)}")
        return None

if __name__ == "__main__":
    result = query_first_item()
    if result:
        print("\nFirst item in Qdrant:")
        print(f"ID: {result['id']}")
        print("\nPayload:")
        print(json.dumps(result['payload'], indent=2, ensure_ascii=False))
    else:
        print("Failed to retrieve item from Qdrant")