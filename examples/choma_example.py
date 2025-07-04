"""
Chroma Vector Database Example

This script demonstrates basic operations with Chroma vector database:
- Client setup
- Collection creation
- Vector insertion with metadata and documents
- Vector search with filtering
- Collection deletion

Requirements:
    pip install chromadb
"""

import random
import uuid
import chromadb
from chromadb.config import Settings

# Configuration
DIMENSION = 128  # Vector dimension
COLLECTION_NAME = "example_collection"
PERSIST_DIRECTORY = "./chroma_db"  # Where to store the database files


def connect_to_chroma():
    """
    Connect to Chroma DB with persistent storage.
    
    Chroma supports two modes:
    1. In-memory: Data lost when process ends
    2. Persistent: Data stored to disk for reuse
    
    Returns:
        chromadb.PersistentClient: Connected client instance
    """
    print("Setting up Chroma client...")

    # For in-memory database (no persistence) - data lost on restart
    # client = chromadb.Client()

    # For persistent database - data saved to local directory
    # This creates the directory if it doesn't exist
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

    print("Successfully connected to Chroma!")
    return client


def create_collection(client):
    """Create a new collection in Chroma"""
    print(f"Creating/getting collection '{COLLECTION_NAME}'...")

    # Try to get the collection
    try:
        # Get the collection if it exists
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' already exists, retrieving it.")
    except Exception:
        # Create the collection if it doesn't exist
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Example collection for vector search"},
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully!")

    return collection


def generate_random_embeddings(count, dim=DIMENSION):
    """
    Generate random vector embeddings for testing purposes.
    
    In production, embeddings would typically come from:
    - Text embeddings (using models like sentence-transformers)
    - Image embeddings (using models like CLIP)
    - Pre-computed embeddings from ML pipelines
    
    Args:
        count (int): Number of vectors to generate
        dim (int): Dimension of each vector
        
    Returns:
        list: List of random float vectors
    """
    return [[random.random() for _ in range(dim)] for _ in range(count)]


def insert_vectors(collection, num_vectors=100):
    """Insert vectors with metadata and documents into the collection"""
    print(f"Generating {num_vectors} random vectors with metadata and documents...")

    # Generate unique IDs
    ids = [str(uuid.uuid4()) for _ in range(num_vectors)]

    # Generate random embeddings
    embeddings = generate_random_embeddings(num_vectors)

    # Generate metadata and documents
    categories = ["article", "blog", "news", "tutorial", "review"]
    sources = ["web", "academic", "books", "internal", "social"]

    metadatas = []
    documents = []

    for i in range(num_vectors):
        # Create metadata
        metadata = {
            "category": random.choice(categories),
            "source": random.choice(sources),
            "rating": random.randint(1, 5),
            "index": i,
        }
        metadatas.append(metadata)

        # Create document text
        document = (
            f"Document {i} in the category {metadata['category']} from source {metadata['source']}. "
            f"This document has a rating of {metadata['rating']} out of 5."
        )
        documents.append(document)

    # Add embeddings to the collection
    collection.add(
        ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents
    )

    print(f"Inserted {num_vectors} vectors into collection '{COLLECTION_NAME}'")
    return ids, embeddings, metadatas


def search_by_vector(collection, query_vector, top_k=5, filter_dict=None):
    """
    Search for similar vectors with optional metadata filtering.
    
    Chroma uses cosine similarity by default for vector comparison.
    The 'where' parameter allows filtering by metadata fields.
    
    Args:
        collection: Chroma collection instance
        query_vector (list): Vector to search for
        top_k (int): Number of results to return
        filter_dict (dict): Optional metadata filter (e.g., {"category": "article"})
        
    Returns:
        dict: Search results with IDs, documents, metadata, and distances
    """
    print(f"Searching for top {top_k} similar vectors...")

    # Query the collection - Chroma automatically computes similarity
    results = collection.query(
        query_embeddings=[query_vector],        # List of query vectors
        n_results=top_k,                       # Number of results to return
        where=filter_dict,                     # Metadata filtering
        include=["documents", "metadatas", "distances"],  # What to include in results
    )

    return results


def main():
    """Main function to demonstrate Chroma operations"""
    try:
        # Connect to Chroma
        client = connect_to_chroma()

        # Create/get collection
        collection = create_collection(client)

        # Check for existing entries
        count = collection.count()
        print(f"Collection has {count} existing entries.")

        # Add new vectors if collection is empty
        if count == 0:
            ids, embeddings, metadatas = insert_vectors(collection, num_vectors=100)
            # Use the last embedding as query vector
            query_vector = embeddings[-1]
        else:
            # Generate a random query vector
            query_vector = generate_random_embeddings(1)[0]

        # Basic search without filtering
        print("\nPerforming basic search:")
        basic_results = search_by_vector(collection, query_vector)

        # Print basic search results
        for i, (id, document, metadata, distance) in enumerate(
            zip(
                basic_results["ids"][0],
                basic_results["documents"][0],
                basic_results["metadatas"][0],
                basic_results["distances"][0],
            )
        ):
            print(f"  Match {i + 1}:")
            print(f"    ID: {id}")
            print(f"    Distance: {distance}")
            print(
                f"    Category: {metadata['category']}, Source: {metadata['source']}, Rating: {metadata['rating']}"
            )
            print(f"    Document excerpt: {document[:100]}...\n")

        # Search with filtering by category
        filter_dict = {"category": "article"}
        print(
            f"\nPerforming filtered search (only '{filter_dict['category']}' category):"
        )
        filtered_results = search_by_vector(
            collection, query_vector, filter_dict=filter_dict
        )

        # Print filtered search results
        if filtered_results["ids"][0]:
            for i, (id, document, metadata, distance) in enumerate(
                zip(
                    filtered_results["ids"][0],
                    filtered_results["documents"][0],
                    filtered_results["metadatas"][0],
                    filtered_results["distances"][0],
                )
            ):
                print(f"  Match {i + 1}:")
                print(f"    ID: {id}")
                print(f"    Distance: {distance}")
                print(
                    f"    Category: {metadata['category']}, Source: {metadata['source']}, Rating: {metadata['rating']}"
                )
                print(f"    Document excerpt: {document[:100]}...\n")
        else:
            print(f"  No matches found for filter {filter_dict}")

        # Optionally delete the collection
        if input("\nDelete the collection? (y/n): ").lower() == "y":
            client.delete_collection(COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
