"""
Milvus Vector Database Example

This script demonstrates basic operations with Milvus vector database:
- Connection setup
- Collection creation with schema
- Index creation
- Vector insertion
- Vector search
- Collection deletion

Requirements:
    pip install pymilvus
"""

import random
import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)

# Configuration
DIMENSION = 128  # Vector dimension
COLLECTION_NAME = "example_collection"
VECTOR_FIELD_NAME = "embeddings"
INDEX_TYPE = (
    "IVF_FLAT"  # Available options: FLAT, IVF_FLAT, IVF_SQ8, IVF_PQ, HNSW, etc.
)
METRIC_TYPE = "L2"  # Available options: L2, IP (Inner Product), COSINE, etc.
TOP_K = 5  # Number of nearest neighbors to retrieve


def connect_to_milvus():
    """Connect to Milvus server"""
    print("Connecting to Milvus...")
    connections.connect("default", host="localhost", port="19530")
    print("Successfully connected to Milvus!")


def create_collection():
    """Create a new collection in Milvus"""
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)
        print(f"Dropped existing collection '{COLLECTION_NAME}'")

    # Define fields for the collection
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name=VECTOR_FIELD_NAME, dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=256),
    ]

    # Create collection schema
    schema = CollectionSchema(
        fields=fields, description="Example collection for vector search"
    )

    # Create the collection
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    print(f"Collection '{COLLECTION_NAME}' created successfully!")

    return collection


def create_index(collection):
    """Create an index on the vector field"""
    print("Creating index...")
    index_params = {
        "index_type": INDEX_TYPE,
        "metric_type": METRIC_TYPE,
        "params": {"nlist": 128},  # Number of clusters for IVF-based indexes
    }

    collection.create_index(VECTOR_FIELD_NAME, index_params)
    print(f"Index '{INDEX_TYPE}' created on field '{VECTOR_FIELD_NAME}'")


def insert_vectors(collection, num_vectors=1000):
    """Insert vectors into the collection"""
    print(f"Generating {num_vectors} random vectors...")

    # Generate random vectors
    ids = [i for i in range(num_vectors)]
    vectors = [[random.random() for _ in range(DIMENSION)] for _ in range(num_vectors)]
    metadata = [f"metadata_{i}" for i in range(num_vectors)]

    # Insert vectors
    collection.insert([ids, vectors, metadata])
    print(f"Inserted {num_vectors} vectors into collection '{COLLECTION_NAME}'")


def search_vectors(collection, query_vector, top_k=TOP_K):
    """Search for similar vectors"""
    print("Loading collection...")
    collection.load()

    print(f"Searching for top {top_k} similar vectors...")
    search_params = {
        "metric_type": METRIC_TYPE,
        "params": {"nprobe": 10},  # Number of clusters to search for IVF indexes
    }

    results = collection.search(
        data=[query_vector],
        anns_field=VECTOR_FIELD_NAME,
        param=search_params,
        limit=top_k,
        output_fields=["metadata"],
    )

    return results


def main():
    """Main function to demonstrate Milvus operations"""
    try:
        # Connect to Milvus server
        connect_to_milvus()

        # Create collection
        collection = create_collection()

        # Insert vectors
        insert_vectors(collection, num_vectors=1000)

        # Create index
        create_index(collection)

        # Generate a random query vector
        query_vector = [random.random() for _ in range(DIMENSION)]

        # Search for similar vectors
        results = search_vectors(collection, query_vector)

        # Print search results
        for i, result in enumerate(results):
            print(f"\nSearch result {i + 1}:")
            for j, entity in enumerate(result):
                distance = entity.distance
                metadata = entity.entity.get("metadata")
                print(
                    f"  Top {j + 1}: ID: {entity.id}, Distance: {distance}, Metadata: {metadata}"
                )

        # Release collection
        collection.release()

        # Optionally drop the collection
        if input("\nDrop the collection? (y/n): ").lower() == "y":
            utility.drop_collection(COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' dropped.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Disconnect from Milvus
        connections.disconnect("default")
        print("Disconnected from Milvus.")


if __name__ == "__main__":
    main()
