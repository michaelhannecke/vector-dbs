import os
import json
import time
import logging
import numpy as np
import faiss
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
INDEX_PATH = os.environ.get("INDEX_PATH", "/data/faiss/index.idx")
DIMENSION = int(os.environ.get("VECTOR_DIMENSION", "384"))
INDEX_TYPE = os.environ.get("INDEX_TYPE", "Flat")
NLIST = int(os.environ.get("NLIST", "100"))  # Number of clusters for IVF indexes
NPROBE = int(
    os.environ.get("NPROBE", "10")
)  # Number of clusters to probe during search
API_TOKEN = os.environ.get("API_TOKEN", None)  # Optional API token for authentication

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


# Define data models
@dataclass
class IndexStats:
    index_type: str
    dimension: int
    total_vectors: int
    is_trained: bool
    nlist: int = None
    nprobe: int = None
    metric_type: str = "L2"


# Initialize or load index
def init_index():
    """
    Initialize FAISS index either by loading existing or creating new.
    
    This function handles three scenarios:
    1. Load existing index from disk if available
    2. Create new index based on INDEX_TYPE configuration
    3. Configure index parameters (nprobe for IVF indexes)
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global index

    if os.path.exists(INDEX_PATH):
        # Load existing index from persistent storage
        logger.info(f"Loading index from {INDEX_PATH}")
        try:
            index = faiss.read_index(INDEX_PATH)
            logger.info(f"Loaded index with {index.ntotal} vectors")

            # Configure IVF-specific parameters for search performance
            if isinstance(index, faiss.IndexIVF):
                index.nprobe = NPROBE  # Number of clusters to probe during search
                logger.info(f"Set nprobe to {NPROBE}")

            return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    else:
        # Create new index based on configuration
        logger.info(f"Creating new {INDEX_TYPE} index with dimension {DIMENSION}")
        try:
            if INDEX_TYPE == "Flat":
                # Flat index: exact search, no training required
                index = faiss.IndexFlatL2(DIMENSION)
            elif INDEX_TYPE == "IVF":
                # IVF index: approximate search, requires training
                quantizer = faiss.IndexFlatL2(DIMENSION)  # Quantizer for clustering
                index = faiss.IndexIVFFlat(quantizer, DIMENSION, NLIST, faiss.METRIC_L2)
                # Note: IVF index needs to be trained before use with training data
            elif INDEX_TYPE == "HNSW":
                # HNSW index: graph-based approximate search
                index = faiss.IndexHNSWFlat(DIMENSION, 32)  # 32 is M parameter (connections per node)
            else:
                # Fallback to flat index for unknown types
                logger.warning(f"Unknown index type {INDEX_TYPE}, defaulting to Flat")
                index = faiss.IndexFlatL2(DIMENSION)

            # Persist the empty index to disk for future use
            logger.info(f"Saving initial empty index to {INDEX_PATH}")
            faiss.write_index(index, INDEX_PATH)
            return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False


# Authentication middleware
def authenticate():
    """
    Validate API authentication using Bearer token.
    
    Authentication is optional - if no API_TOKEN is configured,
    all requests are allowed. When configured, expects:
    Authorization: Bearer <token>
    
    Returns:
        bool: True if authenticated or no auth required, False otherwise
    """
    # No authentication required if token not configured
    if API_TOKEN is None:
        return True

    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            # Parse "Bearer <token>" format
            token_type, token = auth_header.split()
            if token_type.lower() == "bearer" and token == API_TOKEN:
                return True
        except ValueError:
            # Malformed header (not enough parts to split)
            pass

    return False


# Get index stats
def get_index_stats():
    stats = IndexStats(
        index_type=INDEX_TYPE,
        dimension=DIMENSION,
        total_vectors=index.ntotal,
        is_trained=True,  # Flat index is always trained
    )

    if isinstance(index, faiss.IndexIVF):
        stats.is_trained = index.is_trained
        stats.nlist = index.nlist
        stats.nprobe = index.nprobe

    return stats


# API routes
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})


@app.route("/stats", methods=["GET"])
def stats():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(asdict(get_index_stats()))


@app.route("/add", methods=["POST"])
def add_vectors():
    """
    Add vectors to the FAISS index.
    
    Expected JSON payload:
    {
        "vectors": [[...], [...], ...],  # List of vectors (required)
        "ids": [1, 2, 3, ...]           # Optional: custom IDs for vectors
    }
    
    For IVF indexes, training occurs automatically when enough vectors
    are available (>= NLIST parameter).
    """
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        vectors = np.array(data["vectors"], dtype=np.float32)

        # Validate vector dimensions match index configuration
        if vectors.shape[1] != DIMENSION:
            return jsonify(
                {
                    "error": f"Vector dimension mismatch. Expected {DIMENSION}, got {vectors.shape[1]}"
                }
            ), 400

        # Auto-train IVF index when we have enough vectors
        if (
            isinstance(index, faiss.IndexIVF)
            and not index.is_trained
            and vectors.shape[0] >= NLIST
        ):
            logger.info(f"Training IVF index with {vectors.shape[0]} vectors")
            index.train(vectors)  # Train clustering on provided vectors

        # Add vectors with or without custom IDs
        ids = None
        if "ids" in data:
            # Use custom IDs provided by client
            ids = np.array(data["ids"], dtype=np.int64)
            if len(ids) != vectors.shape[0]:
                return jsonify(
                    {
                        "error": f"Number of IDs ({len(ids)}) does not match number of vectors ({vectors.shape[0]})"
                    }
                ), 400

            index.add_with_ids(vectors, ids)
        else:
            # Auto-generate sequential IDs
            index.add(vectors)

        # Persist updated index to disk
        faiss.write_index(index, INDEX_PATH)

        return jsonify(
            {
                "status": "success",
                "vectors_added": len(vectors),
                "total_vectors": index.ntotal,
            }
        )

    except Exception as e:
        logger.error(f"Error adding vectors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/search", methods=["POST"])
def search_vectors():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        query_vectors = np.array(data["query_vectors"], dtype=np.float32)
        k = data.get("k", 5)

        # Check dimensions
        if query_vectors.shape[1] != DIMENSION:
            return jsonify(
                {
                    "error": f"Vector dimension mismatch. Expected {DIMENSION}, got {query_vectors.shape[1]}"
                }
            ), 400

        # Set custom nprobe for this search if provided
        custom_nprobe = data.get("nprobe")
        if custom_nprobe and isinstance(index, faiss.IndexIVF):
            original_nprobe = index.nprobe
            index.nprobe = int(custom_nprobe)
        else:
            original_nprobe = None

        # Perform search
        start_time = time.time()
        distances, indices = index.search(query_vectors, k)
        search_time = time.time() - start_time

        # Reset nprobe if it was changed
        if original_nprobe is not None:
            index.nprobe = original_nprobe

        # Format results
        results = []
        for i in range(len(query_vectors)):
            results.append(
                {"distances": distances[i].tolist(), "indices": indices[i].tolist()}
            )

        return jsonify(
            {
                "status": "success",
                "results": results,
                "search_time_ms": search_time * 1000,
            }
        )

    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/delete", methods=["POST"])
def delete_vectors():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        ids = np.array(data["ids"], dtype=np.int64)

        # Check if index supports deletion
        if not isinstance(index, faiss.IndexIDMap) and not isinstance(
            index, faiss.IndexIVF
        ):
            return jsonify(
                {"error": "Current index type does not support deletion"}
            ), 400

        # Perform deletion
        if isinstance(index, faiss.IndexIDMap):
            index.remove_ids(ids)
        elif isinstance(index, faiss.IndexIVF):
            index.remove_ids(ids)

        # Save index after update
        faiss.write_index(index, INDEX_PATH)

        return jsonify(
            {
                "status": "success",
                "vectors_deleted": len(ids),
                "total_vectors": index.ntotal,
            }
        )

    except Exception as e:
        logger.error(f"Error deleting vectors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset_index():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Create new index based on configuration
        if INDEX_TYPE == "Flat":
            new_index = faiss.IndexFlatL2(DIMENSION)
        elif INDEX_TYPE == "IVF":
            quantizer = faiss.IndexFlatL2(DIMENSION)
            new_index = faiss.IndexIVFFlat(quantizer, DIMENSION, NLIST, faiss.METRIC_L2)
        elif INDEX_TYPE == "HNSW":
            new_index = faiss.IndexHNSWFlat(DIMENSION, 32)
        else:
            new_index = faiss.IndexFlatL2(DIMENSION)

        # Replace global index
        global index
        index = new_index

        # Save empty index
        faiss.write_index(index, INDEX_PATH)

        return jsonify({"status": "success", "message": "Index reset successfully"})

    except Exception as e:
        logger.error(f"Error resetting index: {e}")
        return jsonify({"error": str(e)}), 500


# Initialize the index on startup
if not init_index():
    logger.error("Failed to initialize index. Exiting.")
    exit(1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
