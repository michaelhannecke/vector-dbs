"""
FAISS Vector Search Library Example

This script demonstrates basic operations with FAISS:
- Index creation (flat and IVF)
- Vector addition
- Vector search
- Index saving and loading

Requirements:
    pip install faiss-cpu  # or faiss-gpu if GPU is available
    pip install numpy
"""

import os
import time
import numpy as np
import faiss

# Configuration
DIMENSION = 128  # Vector dimension
NUM_VECTORS = 10000  # Number of vectors for the example
INDEX_FILE = "faiss_index.idx"  # File to save the index
USE_GPU = False  # Set to True if using GPU


def generate_random_vectors(num_vectors, dim):
    """Generate random vectors for testing"""
    print(f"Generating {num_vectors} random vectors with dimension {dim}...")
    return np.random.random((num_vectors, dim)).astype("float32")


def create_flat_index(vectors, dim):
    """Create a flat index (exact search)"""
    print("Creating FlatL2 index (exact search)...")
    index = faiss.IndexFlatL2(dim)

    if USE_GPU:
        print("Moving index to GPU...")
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)

    start_time = time.time()
    index.add(vectors)
    end_time = time.time()

    print(
        f"Added {index.ntotal} vectors to flat index in {end_time - start_time:.2f} seconds"
    )
    return index


def create_ivf_index(vectors, dim, nlist=100):
    """Create an IVF index (approximate search)"""
    print(f"Creating IVF index with {nlist} clusters...")

    # Create a quantizer
    quantizer = faiss.IndexFlatL2(dim)

    # Create the index
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_L2)

    if USE_GPU:
        print("Moving index to GPU...")
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)

    # Train the index
    print("Training the index...")
    start_time = time.time()
    index.train(vectors)
    train_time = time.time() - start_time
    print(f"Trained index in {train_time:.2f} seconds")

    # Add vectors to the index
    print("Adding vectors to the index...")
    start_time = time.time()
    index.add(vectors)
    add_time = time.time() - start_time
    print(f"Added {index.ntotal} vectors to IVF index in {add_time:.2f} seconds")

    return index


def search_index(index, query_vectors, k=5, nprobe=None):
    """Search for nearest vectors in the index"""
    # Set number of clusters to probe for IVF indexes
    if nprobe is not None and hasattr(index, "nprobe"):
        old_nprobe = index.nprobe
        index.nprobe = nprobe
        print(f"Set nprobe to {nprobe} (was {old_nprobe})")

    print(f"Searching for top {k} nearest neighbors...")

    start_time = time.time()
    distances, indices = index.search(query_vectors, k)
    end_time = time.time()

    print(f"Search completed in {(end_time - start_time) * 1000:.2f} ms")

    # Reset nprobe to its original value
    if nprobe is not None and hasattr(index, "nprobe"):
        index.nprobe = old_nprobe

    return distances, indices


def save_index(index, filename):
    """Save the index to a file"""
    print(f"Saving index to {filename}...")

    # If index is on GPU, convert back to CPU for saving
    if USE_GPU:
        print("Moving index back to CPU...")
        index = faiss.index_gpu_to_cpu(index)

    faiss.write_index(index, filename)
    print(f"Index saved to {filename}")


def load_index(filename):
    """Load the index from a file"""
    print(f"Loading index from {filename}...")

    index = faiss.read_index(filename)

    if USE_GPU:
        print("Moving loaded index to GPU...")
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)

    print(f"Loaded index with {index.ntotal} vectors")
    return index


def print_search_results(distances, indices, vectors=None, metadata=None):
    """Print search results in a readable format"""
    print("\nSearch results:")

    for query_idx in range(len(distances)):
        print(f"Query {query_idx + 1}:")

        for i, (idx, dist) in enumerate(zip(indices[query_idx], distances[query_idx])):
            result = f"  Match {i + 1}: ID: {idx}, Distance: {dist:.4f}"

            if metadata is not None and idx < len(metadata):
                result += f", Metadata: {metadata[idx]}"

            print(result)

        print()


def main():
    """Main function to demonstrate FAISS operations"""
    try:
        # Generate random vectors
        vectors = generate_random_vectors(NUM_VECTORS, DIMENSION)

        # Create a flat index (exact search)
        flat_index = create_flat_index(vectors, DIMENSION)

        # Generate queries
        num_queries = 5
        query_vectors = generate_random_vectors(num_queries, DIMENSION)

        # Search the flat index
        print("\n=== Flat Index Search (Exact) ===")
        flat_distances, flat_indices = search_index(flat_index, query_vectors)
        print_search_results(flat_distances, flat_indices)

        # Create an IVF index (approximate search)
        ivf_index = create_ivf_index(vectors, DIMENSION)

        # Search the IVF index with default nprobe
        print("\n=== IVF Index Search (Default nprobe) ===")
        ivf_distances_default, ivf_indices_default = search_index(
            ivf_index, query_vectors
        )
        print_search_results(ivf_distances_default, ivf_indices_default)

        # Search the IVF index with higher nprobe for better recall
        print("\n=== IVF Index Search (Higher nprobe) ===")
        ivf_distances_higher, ivf_indices_higher = search_index(
            ivf_index, query_vectors, nprobe=30
        )
        print_search_results(ivf_distances_higher, ivf_indices_higher)

        # Save the IVF index
        save_index(ivf_index, INDEX_FILE)

        # Load the index
        loaded_index = load_index(INDEX_FILE)

        # Search the loaded index
        print("\n=== Loaded Index Search ===")
        loaded_distances, loaded_indices = search_index(loaded_index, query_vectors)
        print_search_results(loaded_distances, loaded_indices)

        # Clean up
        if (
            os.path.exists(INDEX_FILE)
            and input(f"\nDelete the index file '{INDEX_FILE}'? (y/n): ").lower() == "y"
        ):
            os.remove(INDEX_FILE)
            print(f"Index file '{INDEX_FILE}' deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
