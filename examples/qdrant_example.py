"""
Qdrant Vector Database Example

This script demonstrates basic operations with Qdrant vector database:
- Client setup
- Collection creation
- Vector insertion with payloads
- Vector search with filtering
- Collection deletion

Requirements:
    pip install qdrant-client
"""

import random
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Configuration
DIMENSION = 128  # Vector dimension
COLLECTION_NAME = "example_collection"
DISTANCE = models.Distance.COSINE  # Options: COSINE, EUCLID (L2), DOT (Inner Product)
TOP_K = 5  # Number of nearest neighbors to retrieve


def connect_to_qdrant():
    """Connect to Qdrant server"""
    print("Connecting to Qdrant...")
    client = QdrantClient(host="localhost", port=6333)
    print("Successfully connected to Qdrant!")
    return client


def create_collection(client):
    """Create a new collection in Qdrant"""
    print(f"Creating collection '{COLLECTION_NAME}'...")

    # Check if collection exists and recreate
    if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")

    # Create the collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=DIMENSION, distance=DISTANCE),
        sparse_vectors_config=None,
    )

    print(f"Collection '{COLLECTION_NAME}' created successfully!")


def insert_vectors(client, num_vectors=1000):
    """Insert vectors with payloads into the collection"""
    print(f"Generating {num_vectors} random vectors with payloads...")

    # Generate random points
    points = []
    categories = ["article", "blog", "news", "review", "tutorial"]

    for i in range(num_vectors):
        # Create a random vector
        vector = [random.random() for _ in range(DIMENSION)]

        # Create payload
        payload = {
            "category": random.choice(categories),
            "rating": random.randint(1, 5),
            "tags": random.sample(["ai", "ml", "database", "vector", "search"], k=2),
            "name": f"item_{i}",
        }

        # Create point
        point = models.PointStruct(id=i, vector=vector, payload=payload)

        points.append(point)

    # Insert points in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upload_points(collection_name=COLLECTION_NAME, points=batch)
        print(
            f"Uploaded batch {i // batch_size + 1}/{(len(points) - 1) // batch_size + 1}"
        )

    print(f"Inserted {num_vectors} vectors into collection '{COLLECTION_NAME}'")


def search_vectors(client, query_vector, filter_condition=None, top_k=TOP_K):
    """Search for similar vectors with optional filtering"""
    print(f"Searching for top {top_k} similar vectors...")

    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=top_k,
    )

    return search_result


def main():
    """Main function to demonstrate Qdrant operations"""
    try:
        # Connect to Qdrant server
        client = connect_to_qdrant()

        # Create collection
        create_collection(client)

        # Insert vectors
        insert_vectors(client, num_vectors=1000)

        # Generate a random query vector
        query_vector = [random.random() for _ in range(DIMENSION)]

        # Basic search without filtering
        print("\nPerforming basic search:")
        basic_results = search_vectors(client, query_vector)

        # Print basic search results
        for i, result in enumerate(basic_results):
            print(
                f"  Match {i + 1}: ID: {result.id}, Score: {result.score}, Category: {result.payload['category']}"
            )

        # Search with filtering
        print("\nPerforming filtered search (only 'article' category):")
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="category", match=models.MatchValue(value="article")
                ),
                models.FieldCondition(
                    key="rating",
                    range=models.Range(
                        gte=4  # Greater than or equal to 4
                    ),
                ),
            ]
        )

        filtered_results = search_vectors(client, query_vector, filter_condition)

        # Print filtered search results
        for i, result in enumerate(filtered_results):
            print(
                f"  Match {i + 1}: ID: {result.id}, Score: {result.score}, "
                + f"Category: {result.payload['category']}, Rating: {result.payload['rating']}"
            )

        # Optionally delete the collection
        if input("\nDelete the collection? (y/n): ").lower() == "y":
            client.delete_collection(COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
